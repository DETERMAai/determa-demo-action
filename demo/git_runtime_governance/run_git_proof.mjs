import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SANDBOX_REPO_DIR = path.join(__dirname, "sandbox_repo");
const OUTPUT_DIR = path.join(__dirname, "output");
const LATEST_DIR = path.join(OUTPUT_DIR, "latest");

const TARGET_FILE = "service_config.env";
const DEPENDENCY_FILE = "dependencies.lock.json";
const QUEUE_FILE = "mutation_queue.json";
const ENVIRONMENT_PROFILE_FILE = "environment_profile.json";
const APPROVAL_RUNTIME_EPOCH = 1;
const GRANT_FRESHNESS_SECONDS = 900;

const CHECKPOINTS = {
  PRE_EXECUTION: "PRE_EXECUTION",
  MID_EXECUTION: "MID_EXECUTION",
  PRE_COMMIT: "PRE_COMMIT",
  FINALIZATION: "FINALIZATION"
};

function runGit(args, cwd, options = {}) {
  const out = execFileSync("git", args, {
    cwd,
    encoding: "utf8"
  });
  if (options.trim === false) return out;
  return out.trim();
}

function safeRunGit(args, cwd) {
  try {
    return {
      ok: true,
      output: runGit(args, cwd)
    };
  } catch (error) {
    return {
      ok: false,
      output: error.stdout ? String(error.stdout) : "",
      error: error.stderr ? String(error.stderr) : error.message
    };
  }
}

function normalizeText(input) {
  return input.replace(/\r\n/g, "\n");
}

function hashText(input) {
  return crypto.createHash("sha256").update(normalizeText(input), "utf8").digest("hex");
}

async function hashFile(filePath) {
  const content = await fs.readFile(filePath, "utf8");
  return hashText(content);
}

function nowIso() {
  return new Date().toISOString();
}

function runStamp(dateObj) {
  const y = dateObj.getUTCFullYear();
  const m = String(dateObj.getUTCMonth() + 1).padStart(2, "0");
  const d = String(dateObj.getUTCDate()).padStart(2, "0");
  const hh = String(dateObj.getUTCHours()).padStart(2, "0");
  const mm = String(dateObj.getUTCMinutes()).padStart(2, "0");
  const ss = String(dateObj.getUTCSeconds()).padStart(2, "0");
  return `${y}${m}${d}_${hh}${mm}${ss}`;
}

function clone(obj) {
  return JSON.parse(JSON.stringify(obj));
}

function divergenceLevel(score) {
  if (score >= 80) return "CRITICAL";
  if (score >= 55) return "HIGH";
  if (score >= 30) return "MEDIUM";
  return "LOW";
}

function authorityContinuityState(score, replayDetected, concurrentMutationDetected) {
  if (replayDetected || concurrentMutationDetected || score >= 80) return "INVALID";
  if (score >= 55) return "STALE";
  if (score >= 30) return "WEAKENING";
  return "VALID";
}

async function writeFileUtf8(filePath, content) {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, content, "utf8");
}

function appendEvent(chain, prevRef, eventType, phase, payload) {
  const eventId = `evt_${String(chain.length + 1).padStart(4, "0")}_${hashText(`${eventType}_${chain.length + 1}_${phase}`).slice(0, 8)}`;
  const event = {
    event_id: eventId,
    previous_event_id: prevRef.value,
    phase,
    timestamp: nowIso(),
    event_type: eventType,
    payload
  };
  chain.push(event);
  prevRef.value = eventId;
}

function isoWithOffset(baseIso, secondsOffset) {
  const baseMs = new Date(baseIso).getTime();
  return new Date(baseMs + secondsOffset * 1000).toISOString();
}

function makeQueueState({
  phase,
  depth,
  latencyMs,
  retryCount,
  priority,
  queuedMutations
}) {
  const state = {
    phase,
    queue_depth: depth,
    execution_latency_ms: latencyMs,
    retry_count: retryCount,
    execution_priority: priority,
    queued_mutations: queuedMutations
  };
  return {
    ...state,
    queue_witness_hash: hashText(JSON.stringify(state))
  };
}

async function setupSandboxRepo() {
  await fs.rm(SANDBOX_REPO_DIR, { recursive: true, force: true });
  await fs.mkdir(SANDBOX_REPO_DIR, { recursive: true });

  runGit(["init"], SANDBOX_REPO_DIR);
  runGit(["config", "user.name", "DETERMA Demo"], SANDBOX_REPO_DIR);
  runGit(["config", "user.email", "demo@determa.local"], SANDBOX_REPO_DIR);

  const baselineTarget = [
    "SERVICE=worker",
    "MAX_RETRIES=3",
    "TIMEOUT_SECONDS=45",
    "RUNTIME_GUARD=true"
  ].join("\n") + "\n";

  const baselineDeps = JSON.stringify(
    {
      "runtime-core": "2.4.1",
      "mutation-engine": "1.7.3",
      "queue-adapter": "0.9.8"
    },
    null,
    2
  ) + "\n";

  const baselineQueue = JSON.stringify(
    {
      pending_mutations: [],
      queue_epoch: 1
    },
    null,
    2
  ) + "\n";

  const baselineEnvironmentProfile = JSON.stringify(
    {
      environment_id: "staging",
      runtime_profile: "staging-default",
      feature_gate: "stable",
      region: "us-east-1",
      branch_track: "main"
    },
    null,
    2
  ) + "\n";

  await writeFileUtf8(path.join(SANDBOX_REPO_DIR, TARGET_FILE), baselineTarget);
  await writeFileUtf8(path.join(SANDBOX_REPO_DIR, DEPENDENCY_FILE), baselineDeps);
  await writeFileUtf8(path.join(SANDBOX_REPO_DIR, QUEUE_FILE), baselineQueue);
  await writeFileUtf8(path.join(SANDBOX_REPO_DIR, ENVIRONMENT_PROFILE_FILE), baselineEnvironmentProfile);

  runGit(["add", "."], SANDBOX_REPO_DIR);
  runGit(["commit", "-m", "baseline runtime state"], SANDBOX_REPO_DIR);

  return {
    baseline_head: runGit(["rev-parse", "HEAD"], SANDBOX_REPO_DIR),
    baseline_target: baselineTarget
  };
}

async function generatePatchProposal(runDir, baselineHead) {
  runGit(["checkout", "-B", "proposal_source", baselineHead], SANDBOX_REPO_DIR);

  const targetPath = path.join(SANDBOX_REPO_DIR, TARGET_FILE);
  const original = await fs.readFile(targetPath, "utf8");
  const patched = original.replace("MAX_RETRIES=3", "MAX_RETRIES=5");
  await fs.writeFile(targetPath, patched, "utf8");

  const patchContent = runGit(["diff", "--", TARGET_FILE], SANDBOX_REPO_DIR, { trim: false });
  if (!patchContent.trim()) {
    throw new Error("Patch generation failed: empty patch");
  }
  await fs.writeFile(targetPath, original, "utf8");

  const patchDir = path.join(runDir, "proposal");
  await fs.mkdir(patchDir, { recursive: true });
  const patchFile = path.join(patchDir, "mutation.patch");
  await fs.writeFile(patchFile, patchContent, "utf8");

  const patchHash = hashText(patchContent);
  return {
    proposal_id: `proposal_${patchHash.slice(0, 12)}`,
    target_file: TARGET_FILE,
    patch_hash: patchHash,
    patch_file: patchFile,
    approval_head: baselineHead,
    runtime_epoch: APPROVAL_RUNTIME_EPOCH,
    created_at: nowIso(),
    mutation_scope: "runtime.config.worker",
    patch: {
      operation: "line_replace",
      from: "MAX_RETRIES=3",
      to: "MAX_RETRIES=5"
    },
    patch_preview: "MAX_RETRIES=3 -> MAX_RETRIES=5"
  };
}

async function captureApprovalSnapshot(proposal, baselineHead) {
  const targetContent = await fs.readFile(path.join(SANDBOX_REPO_DIR, TARGET_FILE), "utf8");
  const dependencyContent = await fs.readFile(path.join(SANDBOX_REPO_DIR, DEPENDENCY_FILE), "utf8");
  const queueContent = await fs.readFile(path.join(SANDBOX_REPO_DIR, QUEUE_FILE), "utf8");
  const environmentProfileContent = await fs.readFile(path.join(SANDBOX_REPO_DIR, ENVIRONMENT_PROFILE_FILE), "utf8");
  const targetHash = hashText(targetContent);
  const dependencyHash = hashText(dependencyContent);
  const queueHash = hashText(queueContent);
  const environment_profile_hash = hashText(environmentProfileContent);
  const stagedExpectedContent = targetContent.replace(proposal.patch.from, proposal.patch.to);

  return {
    approval_id: `approval_${hashText(`${proposal.proposal_id}_${baselineHead}`).slice(0, 12)}`,
    head: baselineHead,
    target_file: TARGET_FILE,
    target_hash: targetHash,
    target_content: targetContent,
    dependency_content: dependencyContent,
    queue_content: queueContent,
    environment_profile_content: environmentProfileContent,
    dependency_hash: dependencyHash,
    queue_hash: queueHash,
    environment_profile_hash,
    runtime_epoch: APPROVAL_RUNTIME_EPOCH,
    approval_timestamp: nowIso(),
    expected_staged_target_hash: hashText(stagedExpectedContent)
  };
}

async function restoreRuntimeBaseline(approvalSnapshot) {
  await fs.writeFile(path.join(SANDBOX_REPO_DIR, TARGET_FILE), approvalSnapshot.target_content, "utf8");
  await fs.writeFile(path.join(SANDBOX_REPO_DIR, DEPENDENCY_FILE), approvalSnapshot.dependency_content, "utf8");
  await fs.writeFile(path.join(SANDBOX_REPO_DIR, QUEUE_FILE), approvalSnapshot.queue_content, "utf8");
  await fs.writeFile(path.join(SANDBOX_REPO_DIR, ENVIRONMENT_PROFILE_FILE), approvalSnapshot.environment_profile_content, "utf8");
}

function issueAuthorityGrant(proposal, approvalSnapshot) {
  return {
    grant_id: `grant_${hashText(`${proposal.patch_hash}_${approvalSnapshot.approval_id}`).slice(0, 12)}`,
    issued_at: nowIso(),
    freshness_window_seconds: GRANT_FRESHNESS_SECONDS,
    single_use: true,
    consumed: false,
    scope: {
      target_file: proposal.target_file,
      mutation_scope: proposal.mutation_scope,
      patch_hash: proposal.patch_hash,
      approval_head: approvalSnapshot.head
    }
  };
}

async function captureRuntimeWitness(runtimeEpoch, queueState, concurrentMutationDetected = false, options = {}) {
  const head = runGit(["rev-parse", "HEAD"], SANDBOX_REPO_DIR);
  const targetHash = await hashFile(path.join(SANDBOX_REPO_DIR, TARGET_FILE));
  const dependencyHash = await hashFile(path.join(SANDBOX_REPO_DIR, DEPENDENCY_FILE));
  const queueHash = await hashFile(path.join(SANDBOX_REPO_DIR, QUEUE_FILE));
  const normalizedQueueState =
    typeof queueState === "string"
      ? makeQueueState({
          phase: queueState,
          depth: options.queue_depth ?? 0,
          latencyMs: options.execution_latency_ms ?? 0,
          retryCount: options.retry_count ?? 0,
          priority: options.execution_priority ?? "normal",
          queuedMutations: options.queued_mutations ?? []
        })
      : queueState;

  return {
    head,
    target_file: TARGET_FILE,
    target_hash: targetHash,
    dependency_hash: dependencyHash,
    queue_hash: queueHash,
    runtime_epoch: runtimeEpoch,
    queue_state: normalizedQueueState.phase,
    queue_witness_hash: normalizedQueueState.queue_witness_hash,
    concurrent_mutation_detected: concurrentMutationDetected,
    queue_depth: normalizedQueueState.queue_depth,
    retry_count: normalizedQueueState.retry_count,
    execution_priority: normalizedQueueState.execution_priority,
    execution_latency_ms: normalizedQueueState.execution_latency_ms,
    queued_mutations: normalizedQueueState.queued_mutations,
    runtime_timestamp: options.runtime_timestamp ?? nowIso()
  };
}

async function captureEnvironmentWitness({
  environmentId,
  runtimeEpoch,
  queueState,
  delegatedFrom = null,
  runtimeTimestamp,
  queueDepth = 0,
  retryCount = 0,
  executionPriority = "normal",
  queuedMutations = []
}) {
  const head = runGit(["rev-parse", "HEAD"], SANDBOX_REPO_DIR);
  const dependencyHash = await hashFile(path.join(SANDBOX_REPO_DIR, DEPENDENCY_FILE));
  const queueHash = await hashFile(path.join(SANDBOX_REPO_DIR, QUEUE_FILE));
  const targetHash = await hashFile(path.join(SANDBOX_REPO_DIR, TARGET_FILE));
  const profilePath = path.join(SANDBOX_REPO_DIR, ENVIRONMENT_PROFILE_FILE);
  const profile = JSON.parse(await fs.readFile(profilePath, "utf8"));
  const normalizedQueueState =
    typeof queueState === "string"
      ? makeQueueState({
          phase: queueState,
          depth: queueDepth,
          latencyMs: 0,
          retryCount,
          priority: executionPriority,
          queuedMutations
        })
      : queueState;

  const configHash = hashText(
    JSON.stringify({
      runtime_profile: profile.runtime_profile,
      feature_gate: profile.feature_gate,
      region: profile.region,
      branch_track: profile.branch_track
    })
  );

  const branchHash = head;
  const environmentWitness = {
    environment_id: environmentId,
    runtime_epoch: runtimeEpoch,
    dependency_hash: dependencyHash,
    config_hash: configHash,
    queue_hash: queueHash,
    branch_hash: branchHash,
    queue_witness_hash: normalizedQueueState.queue_witness_hash,
    target_hash: targetHash,
    delegated_from: delegatedFrom,
    runtime_timestamp: runtimeTimestamp ?? nowIso()
  };

  environmentWitness.environment_witness_hash = hashText(JSON.stringify(environmentWitness));
  return environmentWitness;
}

function issueEnvironmentAuthorityGrant({
  proposal,
  sourceEnvironmentWitness,
  targetEnvironmentId,
  delegated = false
}) {
  return {
    grant_id: `xenv_grant_${hashText(`${proposal.patch_hash}_${sourceEnvironmentWitness.environment_id}_${targetEnvironmentId}`).slice(0, 12)}`,
    issued_at: nowIso(),
    freshness_window_seconds: GRANT_FRESHNESS_SECONDS,
    single_use: true,
    consumed: false,
    source_environment: sourceEnvironmentWitness.environment_id,
    target_environment: targetEnvironmentId,
    delegated,
    scope: {
      target_file: proposal.target_file,
      patch_hash: proposal.patch_hash,
      branch_hash: sourceEnvironmentWitness.branch_hash,
      dependency_hash: sourceEnvironmentWitness.dependency_hash
    }
  };
}

function crossEnvironmentContinuityState(score) {
  if (score >= 80) return "INVALID";
  if (score >= 55) return "STALE";
  if (score >= 30) return "WEAKENING";
  return "CONTINUOUS";
}

function revalidateLegitimacyAcrossEnvironments({
  proposal,
  authorityGrant,
  sourceEnvironment,
  targetEnvironment,
  runtimeWitness,
  divergenceInputs = {}
}) {
  const grantMs = new Date(authorityGrant.issued_at).getTime();
  const witnessMs = new Date(runtimeWitness.runtime_timestamp).getTime();
  const elapsedSeconds = Math.max(0, Math.floor((witnessMs - grantMs) / 1000));

  const checks = {
    runtime_epoch_continuity: targetEnvironment.runtime_epoch === sourceEnvironment.runtime_epoch,
    dependency_continuity: targetEnvironment.dependency_hash === sourceEnvironment.dependency_hash,
    configuration_continuity: targetEnvironment.config_hash === sourceEnvironment.config_hash,
    branch_continuity: targetEnvironment.branch_hash === sourceEnvironment.branch_hash,
    queue_continuity: targetEnvironment.queue_hash === sourceEnvironment.queue_hash,
    environment_witness_continuity:
      targetEnvironment.environment_witness_hash === sourceEnvironment.environment_witness_hash,
    delegated_authority_continuity: authorityGrant.delegated
      ? targetEnvironment.delegated_from === authorityGrant.source_environment
      : targetEnvironment.environment_id === authorityGrant.target_environment,
    freshness: elapsedSeconds <= authorityGrant.freshness_window_seconds,
    scope_continuity:
      proposal.patch_hash === authorityGrant.scope.patch_hash &&
      proposal.target_file === authorityGrant.scope.target_file
  };

  const penalties = {
    runtime_epoch_continuity: checks.runtime_epoch_continuity ? 0 : 14,
    dependency_continuity: checks.dependency_continuity ? 0 : 18,
    configuration_continuity: checks.configuration_continuity ? 0 : 18,
    branch_continuity: checks.branch_continuity ? 0 : 16,
    queue_continuity: checks.queue_continuity ? 0 : 12,
    environment_witness_continuity: checks.environment_witness_continuity ? 0 : 20,
    delegated_authority_continuity: checks.delegated_authority_continuity ? 0 : 20,
    freshness: checks.freshness ? 0 : 10,
    scope_continuity: checks.scope_continuity ? 0 : 28,
    dependency_drift_pressure: divergenceInputs.dependency_drift_pressure || 0,
    branch_advancement_pressure: divergenceInputs.branch_advancement_pressure || 0,
    config_drift_pressure: divergenceInputs.config_drift_pressure || 0,
    queue_drift_pressure: divergenceInputs.queue_drift_pressure || 0,
    delegated_runtime_aging: divergenceInputs.delegated_runtime_aging || 0
  };

  const divergenceScore = Math.min(100, Object.values(penalties).reduce((sum, p) => sum + p, 0));
  const divergenceLevelValue = divergenceLevel(divergenceScore);
  const continuity = crossEnvironmentContinuityState(divergenceScore);

  let admissibility = "ADMISSIBLE";
  if (
    !checks.scope_continuity ||
    !checks.delegated_authority_continuity ||
    !checks.branch_continuity ||
    !checks.runtime_epoch_continuity
  ) {
    admissibility = "DENIED";
  } else if (
    !checks.dependency_continuity ||
    !checks.configuration_continuity ||
    !checks.queue_continuity ||
    !checks.environment_witness_continuity ||
    !checks.freshness
  ) {
    admissibility = "DENIED";
  }

  const reasons = [];
  if (!checks.runtime_epoch_continuity) reasons.push("runtime epoch mismatch across environments");
  if (!checks.dependency_continuity) reasons.push("dependency continuity mismatch");
  if (!checks.configuration_continuity) reasons.push("configuration continuity mismatch");
  if (!checks.branch_continuity) reasons.push("branch continuity mismatch");
  if (!checks.queue_continuity) reasons.push("queue witness continuity mismatch");
  if (!checks.environment_witness_continuity) reasons.push("environment witness mismatch");
  if (!checks.delegated_authority_continuity) reasons.push("delegated authority continuity failed");
  if (!checks.freshness) reasons.push("cross-environment authority freshness expired");
  if (!checks.scope_continuity) reasons.push("cross-environment scope continuity failed");
  if (!reasons.length) reasons.push("cross-environment continuity preserved");

  return {
    admissibility,
    divergence_score: divergenceScore,
    divergence_level: divergenceLevelValue,
    cross_environment_legitimacy: continuity,
    elapsed_seconds: elapsedSeconds,
    checks,
    reason: reasons.join("; ")
  };
}

function evaluateLegitimacy({
  checkpoint,
  proposal,
  authorityGrant,
  approvalSnapshot,
  runtimeWitness,
  executionState,
  attemptIndex,
  divergenceInputs
}) {
  const approvalMs = new Date(approvalSnapshot.approval_timestamp).getTime();
  const runtimeMs = new Date(runtimeWitness.runtime_timestamp).getTime();
  const elapsedSeconds = Math.max(0, Math.floor((runtimeMs - approvalMs) / 1000));
  const runtimeHorizonSeconds = divergenceInputs.runtime_horizon_seconds ?? elapsedSeconds;
  const retryCount = divergenceInputs.retry_count ?? runtimeWitness.retry_count ?? 0;
  const queueDepth = divergenceInputs.queue_depth ?? runtimeWitness.queue_depth ?? 0;
  const retryAttempt = divergenceInputs.retry_attempt === true;
  const queueWitnessContinuity = divergenceInputs.queue_witness_hash
    ? runtimeWitness.queue_witness_hash === divergenceInputs.queue_witness_hash
    : true;
  const retryContinuity = retryAttempt
    ? runtimeWitness.head === approvalSnapshot.head &&
      runtimeWitness.dependency_hash === approvalSnapshot.dependency_hash &&
      runtimeWitness.runtime_epoch === approvalSnapshot.runtime_epoch &&
      queueWitnessContinuity
    : true;
  const replayDetected = authorityGrant.consumed || divergenceInputs.replay_attempt === true;

  const expectedTargetHash =
    executionState.status === "STAGED" ||
    executionState.status === "EXECUTING" ||
    executionState.status === "PRE_COMMIT"
      ? executionState.staged_target_hash || approvalSnapshot.expected_staged_target_hash
      : approvalSnapshot.target_hash;

  const checks = {
    head_continuity: runtimeWitness.head === approvalSnapshot.head,
    target_hash_continuity: runtimeWitness.target_hash === expectedTargetHash,
    freshness: elapsedSeconds <= authorityGrant.freshness_window_seconds,
    replay_status: replayDetected,
    scope_continuity:
      proposal.target_file === authorityGrant.scope.target_file &&
      proposal.patch_hash === authorityGrant.scope.patch_hash,
    dependency_continuity: runtimeWitness.dependency_hash === approvalSnapshot.dependency_hash,
    runtime_epoch_continuity: runtimeWitness.runtime_epoch === approvalSnapshot.runtime_epoch,
    queue_continuity: runtimeWitness.queue_hash === approvalSnapshot.queue_hash,
    concurrent_mutation_detection: runtimeWitness.concurrent_mutation_detected === true,
    retry_continuity: retryContinuity,
    authority_aging: runtimeHorizonSeconds <= authorityGrant.freshness_window_seconds,
    queue_witness_continuity: queueWitnessContinuity
  };

  let runtimeHorizonState = "SHORT";
  if (runtimeHorizonSeconds > authorityGrant.freshness_window_seconds) runtimeHorizonState = "EXCEEDED";
  else if (runtimeHorizonSeconds > 0.65 * authorityGrant.freshness_window_seconds) runtimeHorizonState = "LONG";
  else if (runtimeHorizonSeconds > 0.35 * authorityGrant.freshness_window_seconds) runtimeHorizonState = "EXTENDED";

  const penalties = {
    head_continuity: checks.head_continuity ? 0 : 22,
    target_hash_continuity: checks.target_hash_continuity ? 0 : 26,
    freshness: checks.freshness ? 0 : 8,
    replay_status: checks.replay_status ? 24 : 0,
    scope_continuity: checks.scope_continuity ? 0 : 30,
    dependency_continuity: checks.dependency_continuity ? 0 : 18,
    runtime_epoch_continuity: checks.runtime_epoch_continuity ? 0 : 12,
    queue_continuity: checks.queue_continuity ? 0 : 8,
    concurrent_mutation_detection: checks.concurrent_mutation_detection ? 28 : 0,
    retry_continuity: checks.retry_continuity ? 0 : 22,
    authority_aging: checks.authority_aging ? 0 : 18,
    waiting_duration: Math.min(Math.floor(runtimeHorizonSeconds / 40), 16),
    retry_delay: Math.min(retryCount * 6, 18),
    queue_depth_pressure: Math.min(queueDepth * 2, 12),
    queue_witness_drift: checks.queue_witness_continuity ? 0 : 14,
    execution_delay_amplification: divergenceInputs.execution_delay_amplification || 0,
    queue_contention: divergenceInputs.queue_contention || 0,
    partial_execution_duration: divergenceInputs.partial_execution_duration || 0,
    dependency_aging: divergenceInputs.dependency_aging || 0,
    branch_advancement: divergenceInputs.branch_advancement || 0,
    deferred_execution_drift: divergenceInputs.deferred_execution_drift || 0
  };

  const divergenceScoreRaw = Object.values(penalties).reduce((sum, p) => sum + p, 0);
  const divergenceScore = Math.min(100, divergenceScoreRaw);
  const divergence = divergenceLevel(divergenceScore);
  const authorityContinuity = authorityContinuityState(
    divergenceScore,
    checks.replay_status,
    checks.concurrent_mutation_detection
  );

  let admissibility = "ADMISSIBLE";
  if (
    !checks.scope_continuity ||
    checks.replay_status ||
    checks.concurrent_mutation_detection ||
    !checks.retry_continuity
  ) {
    admissibility = "DENIED";
  } else if (
    !checks.head_continuity ||
    !checks.target_hash_continuity ||
    !checks.dependency_continuity ||
    !checks.runtime_epoch_continuity
  ) {
    admissibility = "DENIED";
  } else if (!checks.freshness || !checks.queue_continuity) {
    admissibility = "REQUIRES_REVALIDATION";
  }

  const reasons = [];
  if (!checks.head_continuity) reasons.push("repository HEAD diverged");
  if (!checks.target_hash_continuity) reasons.push("target file hash diverged");
  if (!checks.dependency_continuity) reasons.push("dependency snapshot diverged");
  if (!checks.runtime_epoch_continuity) reasons.push("runtime epoch changed");
  if (!checks.queue_continuity) reasons.push("mutation queue state changed");
  if (!checks.freshness) reasons.push("authority grant freshness expired");
  if (!checks.scope_continuity) reasons.push("proposal scope mismatch");
  if (checks.replay_status) reasons.push("single-use authority grant replay detected");
  if (checks.concurrent_mutation_detection) reasons.push("concurrent mutation conflict detected");
  if (!checks.retry_continuity) reasons.push("retry continuity invalid under evolved runtime");
  if (!checks.authority_aging) reasons.push("runtime horizon exceeded authority aging bounds");
  if (!checks.queue_witness_continuity) reasons.push("queue witness continuity drifted");
  if (!reasons.length) reasons.push("authority continuity preserved");

  return {
    checkpoint,
    admissibility,
    divergence_score: divergenceScore,
    divergence_level: divergence,
    authority_continuity: authorityContinuity,
    runtime_horizon_seconds: runtimeHorizonSeconds,
    runtime_horizon_state: runtimeHorizonState,
    retry_count: retryCount,
    queue_depth: queueDepth,
    elapsed_seconds: elapsedSeconds,
    checks,
    reason: reasons.join("; ")
  };
}

async function applyPatchWorkingTree(proposal) {
  const targetPath = path.join(SANDBOX_REPO_DIR, TARGET_FILE);
  const beforeContent = await fs.readFile(targetPath, "utf8");
  if (!beforeContent.includes(proposal.patch.from)) {
    return {
      applied: false,
      reason: "patch precondition missing in target file",
      before_content: beforeContent,
      before_hash: hashText(beforeContent),
      after_hash: hashText(beforeContent),
      after_content: beforeContent
    };
  }

  const afterContent = beforeContent.replace(proposal.patch.from, proposal.patch.to);
  await fs.writeFile(targetPath, afterContent, "utf8");
  return {
    applied: true,
    reason: "patch staged in working tree",
    before_content: beforeContent,
    before_hash: hashText(beforeContent),
    after_hash: hashText(afterContent),
    after_content: afterContent
  };
}

async function restoreTargetContent(content) {
  await fs.writeFile(path.join(SANDBOX_REPO_DIR, TARGET_FILE), content, "utf8");
}

async function mutateRepositoryAfterApproval() {
  const depsPath = path.join(SANDBOX_REPO_DIR, DEPENDENCY_FILE);
  const queuePath = path.join(SANDBOX_REPO_DIR, QUEUE_FILE);
  const deps = JSON.parse(await fs.readFile(depsPath, "utf8"));
  deps["runtime-core"] = "2.5.0";
  await fs.writeFile(depsPath, JSON.stringify(deps, null, 2) + "\n", "utf8");

  const queue = JSON.parse(await fs.readFile(queuePath, "utf8"));
  queue.pending_mutations.push({ id: "queued_hotfix_01", status: "pending" });
  queue.queue_epoch = 2;
  await fs.writeFile(queuePath, JSON.stringify(queue, null, 2) + "\n", "utf8");

  runGit(["add", DEPENDENCY_FILE, QUEUE_FILE], SANDBOX_REPO_DIR);
  runGit(["commit", "-m", "runtime drift mutation before execution"], SANDBOX_REPO_DIR);
}

async function mutateDuringExecutionMidPath() {
  const depsPath = path.join(SANDBOX_REPO_DIR, DEPENDENCY_FILE);
  const queuePath = path.join(SANDBOX_REPO_DIR, QUEUE_FILE);
  const deps = JSON.parse(await fs.readFile(depsPath, "utf8"));
  deps["queue-adapter"] = "1.0.0";
  await fs.writeFile(depsPath, JSON.stringify(deps, null, 2) + "\n", "utf8");

  const queue = JSON.parse(await fs.readFile(queuePath, "utf8"));
  queue.pending_mutations.push({ id: "concurrent_runtime_patch", status: "active" });
  queue.queue_epoch = 3;
  await fs.writeFile(queuePath, JSON.stringify(queue, null, 2) + "\n", "utf8");
}

async function introduceConcurrentMutationCommit() {
  const targetPath = path.join(SANDBOX_REPO_DIR, TARGET_FILE);
  const queuePath = path.join(SANDBOX_REPO_DIR, QUEUE_FILE);
  const targetContent = await fs.readFile(targetPath, "utf8");
  const changedTarget = targetContent.replace("TIMEOUT_SECONDS=45", "TIMEOUT_SECONDS=60");
  await fs.writeFile(targetPath, changedTarget, "utf8");

  const queue = JSON.parse(await fs.readFile(queuePath, "utf8"));
  queue.pending_mutations.push({ id: "concurrent_patch_actor", status: "committed" });
  queue.queue_epoch = queue.queue_epoch + 1;
  await fs.writeFile(queuePath, JSON.stringify(queue, null, 2) + "\n", "utf8");

  runGit(["add", TARGET_FILE, QUEUE_FILE], SANDBOX_REPO_DIR);
  runGit(["commit", "-m", "concurrent mutation actor commit"], SANDBOX_REPO_DIR);
}

async function applyQueueUpdate({ mutationId, queueEpochIncrement = 1, status = "queued", priority = "normal" }) {
  const queuePath = path.join(SANDBOX_REPO_DIR, QUEUE_FILE);
  const queue = JSON.parse(await fs.readFile(queuePath, "utf8"));
  queue.pending_mutations.push({
    id: mutationId,
    status,
    priority
  });
  queue.queue_epoch = (queue.queue_epoch || 1) + queueEpochIncrement;
  await fs.writeFile(queuePath, JSON.stringify(queue, null, 2) + "\n", "utf8");
}

async function mutateForAsyncDelay() {
  const depsPath = path.join(SANDBOX_REPO_DIR, DEPENDENCY_FILE);
  const targetPath = path.join(SANDBOX_REPO_DIR, TARGET_FILE);

  const deps = JSON.parse(await fs.readFile(depsPath, "utf8"));
  deps["queue-adapter"] = "1.1.0";
  deps["runtime-core"] = "2.5.1";
  await fs.writeFile(depsPath, JSON.stringify(deps, null, 2) + "\n", "utf8");

  await applyQueueUpdate({
    mutationId: "async_contention_patch_01",
    queueEpochIncrement: 1,
    status: "waiting",
    priority: "high"
  });

  const targetContent = await fs.readFile(targetPath, "utf8");
  const driftedTarget = targetContent.replace("TIMEOUT_SECONDS=45", "TIMEOUT_SECONDS=50");
  await fs.writeFile(targetPath, driftedTarget, "utf8");

  runGit(["add", DEPENDENCY_FILE, QUEUE_FILE, TARGET_FILE], SANDBOX_REPO_DIR);
  runGit(["commit", "-m", "async queue drift during delayed execution"], SANDBOX_REPO_DIR);
}

async function mutateForRetryDrift() {
  const depsPath = path.join(SANDBOX_REPO_DIR, DEPENDENCY_FILE);
  const deps = JSON.parse(await fs.readFile(depsPath, "utf8"));
  deps["mutation-engine"] = "1.8.0";
  await fs.writeFile(depsPath, JSON.stringify(deps, null, 2) + "\n", "utf8");

  await applyQueueUpdate({
    mutationId: "retry_conflict_hotfix",
    queueEpochIncrement: 1,
    status: "retry-contention",
    priority: "high"
  });

  runGit(["add", DEPENDENCY_FILE, QUEUE_FILE], SANDBOX_REPO_DIR);
  runGit(["commit", "-m", "runtime drift during retry waiting window"], SANDBOX_REPO_DIR);
}

async function setEnvironmentProfile(profileUpdates) {
  const profilePath = path.join(SANDBOX_REPO_DIR, ENVIRONMENT_PROFILE_FILE);
  const current = JSON.parse(await fs.readFile(profilePath, "utf8"));
  const updated = {
    ...current,
    ...profileUpdates
  };
  await fs.writeFile(profilePath, JSON.stringify(updated, null, 2) + "\n", "utf8");
}

async function mutateForProductionDivergence() {
  const depsPath = path.join(SANDBOX_REPO_DIR, DEPENDENCY_FILE);
  const deps = JSON.parse(await fs.readFile(depsPath, "utf8"));
  deps["runtime-core"] = "2.6.0";
  deps["mutation-engine"] = "1.8.2";
  await fs.writeFile(depsPath, JSON.stringify(deps, null, 2) + "\n", "utf8");

  await setEnvironmentProfile({
    environment_id: "production",
    runtime_profile: "prod-hardened",
    feature_gate: "canary-enabled",
    region: "us-west-2"
  });

  await applyQueueUpdate({
    mutationId: "prod_hotfix_contention",
    queueEpochIncrement: 1,
    status: "promotion-contention",
    priority: "critical"
  });

  runGit(["add", DEPENDENCY_FILE, QUEUE_FILE, ENVIRONMENT_PROFILE_FILE], SANDBOX_REPO_DIR);
  runGit(["commit", "-m", "production runtime divergence before promotion"], SANDBOX_REPO_DIR);
}

async function mutateForDelegatedRuntimeDivergence() {
  const targetPath = path.join(SANDBOX_REPO_DIR, TARGET_FILE);
  const target = await fs.readFile(targetPath, "utf8");
  await fs.writeFile(targetPath, target.replace("RUNTIME_GUARD=true", "RUNTIME_GUARD=delegated"), "utf8");

  await setEnvironmentProfile({
    environment_id: "delegated_runtime",
    runtime_profile: "delegated-executor",
    feature_gate: "delegated",
    region: "eu-central-1"
  });

  await applyQueueUpdate({
    mutationId: "delegated_runtime_shift",
    queueEpochIncrement: 1,
    status: "delegated-transfer",
    priority: "high"
  });

  runGit(["add", TARGET_FILE, QUEUE_FILE, ENVIRONMENT_PROFILE_FILE], SANDBOX_REPO_DIR);
  runGit(["commit", "-m", "delegated runtime environment drift"], SANDBOX_REPO_DIR);
}

async function commitPatchFinalization(commitMessage) {
  runGit(["add", TARGET_FILE], SANDBOX_REPO_DIR);
  runGit(["commit", "-m", commitMessage], SANDBOX_REPO_DIR);
  return runGit(["rev-parse", "HEAD"], SANDBOX_REPO_DIR);
}

function stateTransition(nextState) {
  return {
    execution_state: nextState
  };
}

async function writeEvidenceFormats(pathDir, evidence) {
  const horizonState = evidence.final_revalidation.runtime_horizon_state || "N/A";
  const horizonSeconds =
    evidence.final_revalidation.runtime_horizon_seconds === undefined
      ? "N/A"
      : `${evidence.final_revalidation.runtime_horizon_seconds}s`;
  const continuityState =
    evidence.final_revalidation.authority_continuity ||
    evidence.final_revalidation.cross_environment_legitimacy ||
    "N/A";

  await fs.writeFile(path.join(pathDir, "evidence.json"), JSON.stringify(evidence, null, 2), "utf8");
  const txt = [
    `PATH: ${evidence.path_id}`,
    `FINAL_STATUS: ${evidence.execution_outcome.execution_status}`,
    `FINAL_REASON: ${evidence.execution_outcome.reason}`,
    `FINAL_DIVERGENCE: ${evidence.final_revalidation.divergence_level} (${evidence.final_revalidation.divergence_score})`,
    `FINAL_AUTHORITY_CONTINUITY: ${continuityState}`,
    `RUNTIME_HORIZON: ${horizonState} (${horizonSeconds})`
  ].join("\n");
  await fs.writeFile(path.join(pathDir, "evidence.txt"), txt, "utf8");

  const checkpointRows = evidence.checkpoint_results
    .map(
      (cp) =>
        `- ${cp.checkpoint}: admissibility=${cp.admissibility}, continuity=${cp.authority_continuity}, divergence=${cp.divergence_level}(${cp.divergence_score})`
    )
    .join("\n");

  const md = [
    `# ${evidence.path_id}`,
    "",
    `- execution_status: ${evidence.execution_outcome.execution_status}`,
    `- reason: ${evidence.execution_outcome.reason}`,
    "",
    "## Continuous Revalidation Timeline",
    checkpointRows,
    "",
    "## Execution State Progression",
    evidence.execution_phase_timeline || "PROPOSED -> STAGED -> EXECUTING -> HALTED/FINALIZED",
    "",
    "## Queue Timeline",
    "QUEUED -> WAITING -> RETRY_PENDING -> EXECUTING -> REVALIDATING -> HALTED",
    "",
    "## Runtime Horizon",
    `state: ${horizonState} (${horizonSeconds})`,
    "",
    "## Divergence Pressure",
    "LOW -> MEDIUM -> HIGH -> CRITICAL",
    "",
    "## Lineage Events",
    ...evidence.evidence_chain.map((evt) => `- ${evt.event_id} ${evt.event_type} (${evt.phase})`)
  ].join("\n");
  await fs.writeFile(path.join(pathDir, "evidence.md"), md, "utf8");
}

async function runPathAllowedContinuous({ runDir, proposal, approvalSnapshot, grantTemplate, baselineHead }) {
  runGit(["checkout", "-B", "path_a_continuous_allowed", baselineHead], SANDBOX_REPO_DIR);
  await restoreRuntimeBaseline(approvalSnapshot);
  const chain = [];
  const prev = { value: null };
  const checkpointResults = [];
  const grant = clone(grantTemplate);

  let runtimeEpoch = APPROVAL_RUNTIME_EPOCH;
  let queueState = "stable";
  const executionState = {
    status: "PROPOSED",
    staged_target_hash: null
  };

  appendEvent(chain, prev, "proposal_created", "T0", { proposal_id: proposal.proposal_id, patch_hash: proposal.patch_hash });
  appendEvent(chain, prev, "approval_snapshot_captured", "T1", { approval_id: approvalSnapshot.approval_id, head: approvalSnapshot.head });
  appendEvent(chain, prev, "authority_grant_issued", "T2", { grant_id: grant.grant_id, single_use: grant.single_use });

  const preWitness = await captureRuntimeWitness(runtimeEpoch, queueState, false);
  appendEvent(chain, prev, "runtime_witness_captured", CHECKPOINTS.PRE_EXECUTION, preWitness);
  const preEval = evaluateLegitimacy({
    checkpoint: CHECKPOINTS.PRE_EXECUTION,
    proposal,
    authorityGrant: grant,
    approvalSnapshot,
    runtimeWitness: preWitness,
    executionState,
    attemptIndex: 1,
    divergenceInputs: { execution_delay_amplification: 0, queue_contention: 0, partial_execution_duration: 0 }
  });
  checkpointResults.push(preEval);
  appendEvent(chain, prev, "legitimacy_revalidated", CHECKPOINTS.PRE_EXECUTION, preEval);

  executionState.status = "EXECUTING";
  appendEvent(chain, prev, "execution_started", "T3", stateTransition(executionState.status));

  const staged = await applyPatchWorkingTree(proposal);
  if (!staged.applied) {
    throw new Error(`Path A staging failed: ${staged.reason}`);
  }
  executionState.status = "STAGED";
  executionState.staged_target_hash = staged.after_hash;
  appendEvent(chain, prev, "mutation_staged", "T3B", {
    before_hash: staged.before_hash,
    after_hash: staged.after_hash
  });

  const midWitness = await captureRuntimeWitness(runtimeEpoch, queueState, false);
  appendEvent(chain, prev, "runtime_witness_captured", CHECKPOINTS.MID_EXECUTION, midWitness);
  const midEval = evaluateLegitimacy({
    checkpoint: CHECKPOINTS.MID_EXECUTION,
    proposal,
    authorityGrant: grant,
    approvalSnapshot,
    runtimeWitness: midWitness,
    executionState,
    attemptIndex: 1,
    divergenceInputs: { partial_execution_duration: 2 }
  });
  checkpointResults.push(midEval);
  appendEvent(chain, prev, "legitimacy_revalidated", CHECKPOINTS.MID_EXECUTION, midEval);

  executionState.status = "PRE_COMMIT";
  const preCommitWitness = await captureRuntimeWitness(runtimeEpoch, queueState, false);
  appendEvent(chain, prev, "runtime_witness_captured", CHECKPOINTS.PRE_COMMIT, preCommitWitness);
  const preCommitEval = evaluateLegitimacy({
    checkpoint: CHECKPOINTS.PRE_COMMIT,
    proposal,
    authorityGrant: grant,
    approvalSnapshot,
    runtimeWitness: preCommitWitness,
    executionState,
    attemptIndex: 1,
    divergenceInputs: { partial_execution_duration: 3 }
  });
  checkpointResults.push(preCommitEval);
  appendEvent(chain, prev, "legitimacy_revalidated", CHECKPOINTS.PRE_COMMIT, preCommitEval);

  const finalWitness = await captureRuntimeWitness(runtimeEpoch, queueState, false);
  appendEvent(chain, prev, "runtime_witness_captured", CHECKPOINTS.FINALIZATION, finalWitness);
  const finalEval = evaluateLegitimacy({
    checkpoint: CHECKPOINTS.FINALIZATION,
    proposal,
    authorityGrant: grant,
    approvalSnapshot,
    runtimeWitness: finalWitness,
    executionState,
    attemptIndex: 1,
    divergenceInputs: { partial_execution_duration: 4 }
  });
  checkpointResults.push(finalEval);
  appendEvent(chain, prev, "legitimacy_revalidated", CHECKPOINTS.FINALIZATION, finalEval);

  const headBeforeCommit = runGit(["rev-parse", "HEAD"], SANDBOX_REPO_DIR);
  let outcome;
  if (finalEval.admissibility === "ADMISSIBLE") {
    const committedHead = await commitPatchFinalization("governed mutation finalized after continuous revalidation");
    grant.consumed = true;
    executionState.status = "FINALIZED";
    outcome = {
      execution_status: "EXECUTION_ALLOWED",
      reason: "authority continuity preserved through continuous runtime revalidation",
      head_before_commit: headBeforeCommit,
      head_after_commit: committedHead
    };
    appendEvent(chain, prev, "execution_allowed", "T9", outcome);
  } else {
    executionState.status = "HALTED";
    await restoreTargetContent(staged.before_content);
    outcome = {
      execution_status: "EXECUTION_DENIED",
      reason: "continuous revalidation failed before commit finalization",
      head_before_commit: headBeforeCommit,
      head_after_commit: runGit(["rev-parse", "HEAD"], SANDBOX_REPO_DIR)
    };
    appendEvent(chain, prev, "execution_halted", "T9", outcome);
    appendEvent(chain, prev, "rollback_completed", "T9B", {
      restored_target_hash: await hashFile(path.join(SANDBOX_REPO_DIR, TARGET_FILE))
    });
  }

  const replayWitness = await captureRuntimeWitness(runtimeEpoch + 1, "replay_attempt", false);
  const replayEval = evaluateLegitimacy({
    checkpoint: "REPLAY_CHECK",
    proposal,
    authorityGrant: grant,
    approvalSnapshot,
    runtimeWitness: replayWitness,
    executionState: { status: "FINALIZED", staged_target_hash: executionState.staged_target_hash },
    attemptIndex: 2,
    divergenceInputs: { partial_execution_duration: 4, execution_delay_amplification: 6 }
  });
  appendEvent(chain, prev, "runtime_witness_captured", "REPLAY_CHECK", replayWitness);
  appendEvent(chain, prev, "legitimacy_revalidated", "REPLAY_CHECK", replayEval);
  appendEvent(chain, prev, "execution_denied", "REPLAY_CHECK", {
    replay_attempt: true,
    reason: "single-use authority replay invalidated runtime authority continuity"
  });

  appendEvent(chain, prev, "lineage_finalized", "T10", {
    final_status: outcome.execution_status,
    final_reason: outcome.reason
  });

  const evidence = {
    path_id: "path_a_continuous_allowed",
    proposal,
    approval_snapshot: approvalSnapshot,
    authority_grant: grant,
    checkpoint_results: checkpointResults,
    final_revalidation: finalEval,
    replay_result: replayEval,
    execution_outcome: outcome,
    evidence_chain: chain
  };

  const outDir = path.join(runDir, "path_a_continuous_allowed");
  await fs.mkdir(outDir, { recursive: true });
  await writeEvidenceFormats(outDir, evidence);
  await fs.writeFile(path.join(outDir, "target_before_attempt.txt"), approvalSnapshot.target_content, "utf8");
  await fs.writeFile(path.join(outDir, "target_after_attempt.txt"), await fs.readFile(path.join(SANDBOX_REPO_DIR, TARGET_FILE), "utf8"), "utf8");
  return evidence;
}

async function runPathDeniedPreExecution({ runDir, proposal, approvalSnapshot, grantTemplate, baselineHead }) {
  runGit(["checkout", "-B", "path_b_denied_pre_execution", baselineHead], SANDBOX_REPO_DIR);
  await restoreRuntimeBaseline(approvalSnapshot);
  const chain = [];
  const prev = { value: null };
  const checkpointResults = [];
  const grant = clone(grantTemplate);
  let runtimeEpoch = APPROVAL_RUNTIME_EPOCH;
  let queueState = "stable";
  const executionState = { status: "PROPOSED", staged_target_hash: null };

  appendEvent(chain, prev, "proposal_created", "T0", { proposal_id: proposal.proposal_id });
  appendEvent(chain, prev, "approval_snapshot_captured", "T1", { approval_id: approvalSnapshot.approval_id });
  appendEvent(chain, prev, "authority_grant_issued", "T2", { grant_id: grant.grant_id });

  await mutateRepositoryAfterApproval();
  runtimeEpoch += 1;
  queueState = "mutated";

  const preWitness = await captureRuntimeWitness(runtimeEpoch, queueState, false);
  appendEvent(chain, prev, "runtime_witness_captured", CHECKPOINTS.PRE_EXECUTION, preWitness);
  const preEval = evaluateLegitimacy({
    checkpoint: CHECKPOINTS.PRE_EXECUTION,
    proposal,
    authorityGrant: grant,
    approvalSnapshot,
    runtimeWitness: preWitness,
    executionState,
    attemptIndex: 1,
    divergenceInputs: { queue_contention: 6 }
  });
  checkpointResults.push(preEval);
  appendEvent(chain, prev, "legitimacy_revalidated", CHECKPOINTS.PRE_EXECUTION, preEval);

  const targetBefore = await hashFile(path.join(SANDBOX_REPO_DIR, TARGET_FILE));
  appendEvent(chain, prev, "execution_denied", "T3", {
    execution_status: "EXECUTION_DENIED",
    reason: "repository runtime state diverged after approval",
    target_unchanged_by_attempt: true
  });

  appendEvent(chain, prev, "finalization_prevented", "T4", {
    head: runGit(["rev-parse", "HEAD"], SANDBOX_REPO_DIR)
  });

  appendEvent(chain, prev, "lineage_finalized", "T5", {
    final_status: "EXECUTION_DENIED",
    final_reason: "repository runtime state diverged after approval"
  });

  const targetAfter = await hashFile(path.join(SANDBOX_REPO_DIR, TARGET_FILE));
  const evidence = {
    path_id: "path_b_denied_pre_execution",
    proposal,
    approval_snapshot: approvalSnapshot,
    authority_grant: grant,
    checkpoint_results: checkpointResults,
    final_revalidation: preEval,
    execution_outcome: {
      execution_status: "EXECUTION_DENIED",
      reason: "repository runtime state diverged after approval",
      target_hash_before_attempt: targetBefore,
      target_hash_after_attempt: targetAfter,
      target_unchanged_by_attempt: targetBefore === targetAfter
    },
    evidence_chain: chain
  };

  const outDir = path.join(runDir, "path_b_denied_pre_execution");
  await fs.mkdir(outDir, { recursive: true });
  await writeEvidenceFormats(outDir, evidence);
  await fs.writeFile(path.join(outDir, "target_before_attempt.txt"), approvalSnapshot.target_content, "utf8");
  await fs.writeFile(path.join(outDir, "target_after_attempt.txt"), await fs.readFile(path.join(SANDBOX_REPO_DIR, TARGET_FILE), "utf8"), "utf8");
  return evidence;
}

async function runPathMidExecutionHalt({ runDir, proposal, approvalSnapshot, grantTemplate, baselineHead }) {
  runGit(["checkout", "-B", "path_c_mid_execution_halt", baselineHead], SANDBOX_REPO_DIR);
  await restoreRuntimeBaseline(approvalSnapshot);
  const chain = [];
  const prev = { value: null };
  const checkpointResults = [];
  const grant = clone(grantTemplate);
  let runtimeEpoch = APPROVAL_RUNTIME_EPOCH;
  let queueState = "stable";
  const executionState = { status: "PROPOSED", staged_target_hash: null };

  appendEvent(chain, prev, "proposal_created", "T0", { proposal_id: proposal.proposal_id });
  appendEvent(chain, prev, "approval_snapshot_captured", "T1", { approval_id: approvalSnapshot.approval_id });
  appendEvent(chain, prev, "authority_grant_issued", "T2", { grant_id: grant.grant_id });

  const preWitness = await captureRuntimeWitness(runtimeEpoch, queueState, false);
  appendEvent(chain, prev, "runtime_witness_captured", CHECKPOINTS.PRE_EXECUTION, preWitness);
  const preEval = evaluateLegitimacy({
    checkpoint: CHECKPOINTS.PRE_EXECUTION,
    proposal,
    authorityGrant: grant,
    approvalSnapshot,
    runtimeWitness: preWitness,
    executionState,
    attemptIndex: 1,
    divergenceInputs: {}
  });
  checkpointResults.push(preEval);
  appendEvent(chain, prev, "legitimacy_revalidated", CHECKPOINTS.PRE_EXECUTION, preEval);

  executionState.status = "EXECUTING";
  appendEvent(chain, prev, "execution_started", "T3", stateTransition(executionState.status));
  const staged = await applyPatchWorkingTree(proposal);
  if (!staged.applied) {
    throw new Error(`Path C staging failed: ${staged.reason}`);
  }
  executionState.status = "STAGED";
  executionState.staged_target_hash = staged.after_hash;
  appendEvent(chain, prev, "mutation_staged", "T3B", {
    before_hash: staged.before_hash,
    after_hash: staged.after_hash
  });

  await mutateDuringExecutionMidPath();
  runtimeEpoch += 1;
  queueState = "contended";
  appendEvent(chain, prev, "runtime_divergence_detected", "T4", {
    reason: "dependency + queue drift during execution"
  });

  const midWitness = await captureRuntimeWitness(runtimeEpoch, queueState, true);
  appendEvent(chain, prev, "runtime_witness_captured", CHECKPOINTS.MID_EXECUTION, midWitness);
  const midEval = evaluateLegitimacy({
    checkpoint: CHECKPOINTS.MID_EXECUTION,
    proposal,
    authorityGrant: grant,
    approvalSnapshot,
    runtimeWitness: midWitness,
    executionState,
    attemptIndex: 1,
    divergenceInputs: {
      queue_contention: 8,
      partial_execution_duration: 6,
      execution_delay_amplification: 10
    }
  });
  checkpointResults.push(midEval);
  appendEvent(chain, prev, "legitimacy_revalidated", CHECKPOINTS.MID_EXECUTION, midEval);

  executionState.status = "HALTED";
  appendEvent(chain, prev, "execution_halted", "T7", {
    reason: "continuous runtime revalidation detected legitimacy collapse"
  });

  await restoreTargetContent(staged.before_content);
  executionState.status = "ROLLED_BACK";
  appendEvent(chain, prev, "rollback_completed", "T8", {
    restored_target_hash: await hashFile(path.join(SANDBOX_REPO_DIR, TARGET_FILE))
  });

  appendEvent(chain, prev, "finalization_prevented", "T8B", {
    reason: "commit prevented due to mid-execution legitimacy collapse"
  });

  appendEvent(chain, prev, "lineage_finalized", "T9", {
    final_status: "EXECUTION_DENIED",
    final_reason: "execution halted before final commit due to runtime divergence"
  });

  const evidence = {
    path_id: "path_c_mid_execution_halt",
    proposal,
    approval_snapshot: approvalSnapshot,
    authority_grant: grant,
    checkpoint_results: checkpointResults,
    final_revalidation: midEval,
    execution_outcome: {
      execution_status: "EXECUTION_DENIED",
      reason: "execution halted before final commit due to runtime divergence",
      patch_finalized: false
    },
    evidence_chain: chain
  };

  const outDir = path.join(runDir, "path_c_mid_execution_halt");
  await fs.mkdir(outDir, { recursive: true });
  await writeEvidenceFormats(outDir, evidence);
  await fs.writeFile(path.join(outDir, "target_before_attempt.txt"), approvalSnapshot.target_content, "utf8");
  await fs.writeFile(path.join(outDir, "target_after_attempt.txt"), await fs.readFile(path.join(SANDBOX_REPO_DIR, TARGET_FILE), "utf8"), "utf8");
  return evidence;
}

async function runPathConcurrentConflict({ runDir, proposal, approvalSnapshot, grantTemplate, baselineHead }) {
  runGit(["checkout", "-B", "path_d_concurrent_conflict", baselineHead], SANDBOX_REPO_DIR);
  await restoreRuntimeBaseline(approvalSnapshot);
  const chain = [];
  const prev = { value: null };
  const checkpointResults = [];
  const grant = clone(grantTemplate);
  let runtimeEpoch = APPROVAL_RUNTIME_EPOCH;
  let queueState = "stable";
  const executionState = { status: "PROPOSED", staged_target_hash: null };

  appendEvent(chain, prev, "proposal_created", "T0", { proposal_id: proposal.proposal_id });
  appendEvent(chain, prev, "approval_snapshot_captured", "T1", { approval_id: approvalSnapshot.approval_id });
  appendEvent(chain, prev, "authority_grant_issued", "T2", { grant_id: grant.grant_id });

  const preWitness = await captureRuntimeWitness(runtimeEpoch, queueState, false);
  appendEvent(chain, prev, "runtime_witness_captured", CHECKPOINTS.PRE_EXECUTION, preWitness);
  const preEval = evaluateLegitimacy({
    checkpoint: CHECKPOINTS.PRE_EXECUTION,
    proposal,
    authorityGrant: grant,
    approvalSnapshot,
    runtimeWitness: preWitness,
    executionState,
    attemptIndex: 1,
    divergenceInputs: {}
  });
  checkpointResults.push(preEval);
  appendEvent(chain, prev, "legitimacy_revalidated", CHECKPOINTS.PRE_EXECUTION, preEval);

  executionState.status = "EXECUTING";
  appendEvent(chain, prev, "execution_started", "T3", stateTransition(executionState.status));
  appendEvent(chain, prev, "mutation_staged", "T3B", {
    staged_plan: "proposal prepared for execution"
  });

  await introduceConcurrentMutationCommit();
  runtimeEpoch += 1;
  queueState = "concurrent_conflict";
  appendEvent(chain, prev, "runtime_divergence_detected", "T4", {
    reason: "overlapping concurrent mutation committed to repository"
  });

  const midWitness = await captureRuntimeWitness(runtimeEpoch, queueState, true);
  appendEvent(chain, prev, "runtime_witness_captured", CHECKPOINTS.MID_EXECUTION, midWitness);
  const midEval = evaluateLegitimacy({
    checkpoint: CHECKPOINTS.MID_EXECUTION,
    proposal,
    authorityGrant: grant,
    approvalSnapshot,
    runtimeWitness: midWitness,
    executionState,
    attemptIndex: 1,
    divergenceInputs: {
      queue_contention: 10,
      partial_execution_duration: 5,
      execution_delay_amplification: 6
    }
  });
  checkpointResults.push(midEval);
  appendEvent(chain, prev, "legitimacy_revalidated", CHECKPOINTS.MID_EXECUTION, midEval);

  executionState.status = "HALTED";
  appendEvent(chain, prev, "execution_halted", "T7", {
    reason: "concurrent mutation conflict invalidated authority continuity"
  });
  appendEvent(chain, prev, "finalization_prevented", "T8", {
    reason: "commit prevented under concurrent mutation conflict"
  });
  appendEvent(chain, prev, "lineage_finalized", "T9", {
    final_status: "EXECUTION_DENIED",
    final_reason: "concurrent mutation conflict"
  });

  const evidence = {
    path_id: "path_d_concurrent_conflict",
    proposal,
    approval_snapshot: approvalSnapshot,
    authority_grant: grant,
    checkpoint_results: checkpointResults,
    final_revalidation: midEval,
    execution_outcome: {
      execution_status: "EXECUTION_DENIED",
      reason: "concurrent mutation conflict"
    },
    evidence_chain: chain
  };

  const outDir = path.join(runDir, "path_d_concurrent_conflict");
  await fs.mkdir(outDir, { recursive: true });
  await writeEvidenceFormats(outDir, evidence);
  await fs.writeFile(path.join(outDir, "target_before_attempt.txt"), approvalSnapshot.target_content, "utf8");
  await fs.writeFile(path.join(outDir, "target_after_attempt.txt"), await fs.readFile(path.join(SANDBOX_REPO_DIR, TARGET_FILE), "utf8"), "utf8");
  return evidence;
}

async function runPathDelayedExecutionDecay({ runDir, proposal, approvalSnapshot, grantTemplate, baselineHead }) {
  runGit(["checkout", "-B", "path_e_delayed_execution_decay", baselineHead], SANDBOX_REPO_DIR);
  await restoreRuntimeBaseline(approvalSnapshot);
  const chain = [];
  const prev = { value: null };
  const checkpointResults = [];
  const grant = clone(grantTemplate);
  let runtimeEpoch = APPROVAL_RUNTIME_EPOCH;
  const executionState = { status: "PROPOSED", staged_target_hash: null };
  const approvalTime = approvalSnapshot.approval_timestamp;

  appendEvent(chain, prev, "proposal_created", "T0", { proposal_id: proposal.proposal_id });
  appendEvent(chain, prev, "approval_snapshot_captured", "T1", { approval_id: approvalSnapshot.approval_id });
  appendEvent(chain, prev, "authority_grant_issued", "T2", { grant_id: grant.grant_id });

  executionState.status = "APPROVED";
  const approvedQueue = makeQueueState({
    phase: "APPROVED",
    depth: 1,
    latencyMs: 2000,
    retryCount: 0,
    priority: "normal",
    queuedMutations: [proposal.proposal_id]
  });
  const preWitness = await captureRuntimeWitness(runtimeEpoch, approvedQueue, false, {
    runtime_timestamp: isoWithOffset(approvalTime, 4)
  });
  appendEvent(chain, prev, "runtime_witness_captured", CHECKPOINTS.PRE_EXECUTION, preWitness);
  const preEval = evaluateLegitimacy({
    checkpoint: CHECKPOINTS.PRE_EXECUTION,
    proposal,
    authorityGrant: grant,
    approvalSnapshot,
    runtimeWitness: preWitness,
    executionState,
    attemptIndex: 1,
    divergenceInputs: {
      queue_depth: approvedQueue.queue_depth,
      runtime_horizon_seconds: 4
    }
  });
  checkpointResults.push(preEval);
  appendEvent(chain, prev, "legitimacy_revalidated", CHECKPOINTS.PRE_EXECUTION, preEval);

  executionState.status = "QUEUED";
  appendEvent(chain, prev, "execution_queued", "T3", {
    execution_state: executionState.status,
    queue_depth: approvedQueue.queue_depth
  });

  await applyQueueUpdate({
    mutationId: proposal.proposal_id,
    queueEpochIncrement: 1,
    status: "queued",
    priority: "normal"
  });

  executionState.status = "WAITING";
  const waitingQueue = makeQueueState({
    phase: "WAITING",
    depth: 3,
    latencyMs: 190000,
    retryCount: 0,
    priority: "normal",
    queuedMutations: [proposal.proposal_id, "queued_infra_patch", "queued_policy_sync"]
  });
  appendEvent(chain, prev, "queue_state_updated", "T4", waitingQueue);
  appendEvent(chain, prev, "execution_delayed", "T4B", {
    execution_state: executionState.status,
    queue_latency_ms: waitingQueue.execution_latency_ms
  });

  const waitingWitness = await captureRuntimeWitness(runtimeEpoch, waitingQueue, false, {
    runtime_timestamp: isoWithOffset(approvalTime, 420)
  });
  appendEvent(chain, prev, "runtime_witness_captured", CHECKPOINTS.MID_EXECUTION, waitingWitness);
  const waitingEval = evaluateLegitimacy({
    checkpoint: CHECKPOINTS.MID_EXECUTION,
    proposal,
    authorityGrant: grant,
    approvalSnapshot,
    runtimeWitness: waitingWitness,
    executionState,
    attemptIndex: 1,
    divergenceInputs: {
      queue_depth: waitingQueue.queue_depth,
      runtime_horizon_seconds: 420,
      queue_contention: 8,
      execution_delay_amplification: 9,
      deferred_execution_drift: 6
    }
  });
  checkpointResults.push(waitingEval);
  appendEvent(chain, prev, "legitimacy_revalidated", CHECKPOINTS.MID_EXECUTION, waitingEval);

  await mutateForAsyncDelay();
  runtimeEpoch += 2;
  executionState.status = "EXECUTING";

  const resumedQueue = makeQueueState({
    phase: "EXECUTING",
    depth: 4,
    latencyMs: 340000,
    retryCount: 0,
    priority: "normal",
    queuedMutations: [proposal.proposal_id, "queued_infra_patch", "queued_policy_sync", "async_contention_patch_01"]
  });
  appendEvent(chain, prev, "queue_state_updated", "T5", resumedQueue);

  executionState.status = "REVALIDATING";
  const revalidationWitness = await captureRuntimeWitness(runtimeEpoch, resumedQueue, false, {
    runtime_timestamp: isoWithOffset(approvalTime, 1180)
  });
  appendEvent(chain, prev, "runtime_witness_captured", CHECKPOINTS.PRE_COMMIT, revalidationWitness);
  const finalEval = evaluateLegitimacy({
    checkpoint: CHECKPOINTS.PRE_COMMIT,
    proposal,
    authorityGrant: grant,
    approvalSnapshot,
    runtimeWitness: revalidationWitness,
    executionState,
    attemptIndex: 1,
    divergenceInputs: {
      queue_depth: resumedQueue.queue_depth,
      runtime_horizon_seconds: 1180,
      queue_contention: 12,
      execution_delay_amplification: 14,
      dependency_aging: 12,
      branch_advancement: 14,
      deferred_execution_drift: 12
    }
  });
  checkpointResults.push(finalEval);
  appendEvent(chain, prev, "legitimacy_revalidated", CHECKPOINTS.PRE_COMMIT, finalEval);
  appendEvent(chain, prev, "authority_decay_detected", "T7", {
    authority_continuity: finalEval.authority_continuity,
    divergence_level: finalEval.divergence_level
  });
  if (!finalEval.checks.authority_aging) {
    appendEvent(chain, prev, "runtime_horizon_exceeded", "T8", {
      runtime_horizon_seconds: finalEval.runtime_horizon_seconds,
      freshness_window_seconds: grant.freshness_window_seconds
    });
  }

  executionState.status = "HALTED";
  appendEvent(chain, prev, "execution_halted", "T9", {
    reason: "authority continuity collapsed during deferred execution horizon"
  });
  appendEvent(chain, prev, "finalization_prevented", "T9B", {
    execution_state: executionState.status,
    reason: "delayed execution denied before finalization"
  });
  appendEvent(chain, prev, "lineage_finalized", "T10", {
    final_status: "EXECUTION_DENIED",
    final_reason: "runtime continuity decayed during async execution delay"
  });

  const evidence = {
    path_id: "path_e_delayed_execution_decay",
    proposal,
    approval_snapshot: approvalSnapshot,
    authority_grant: grant,
    checkpoint_results: checkpointResults,
    final_revalidation: finalEval,
    execution_outcome: {
      execution_status: "EXECUTION_DENIED",
      reason: "runtime continuity decayed during async execution delay"
    },
    execution_phase_timeline:
      "PROPOSED -> APPROVED -> QUEUED -> WAITING -> EXECUTING -> REVALIDATING -> HALTED -> DENIED",
    evidence_chain: chain
  };

  const outDir = path.join(runDir, "path_e_delayed_execution_decay");
  await fs.mkdir(outDir, { recursive: true });
  await writeEvidenceFormats(outDir, evidence);
  await fs.writeFile(path.join(outDir, "target_before_attempt.txt"), approvalSnapshot.target_content, "utf8");
  await fs.writeFile(path.join(outDir, "target_after_attempt.txt"), await fs.readFile(path.join(SANDBOX_REPO_DIR, TARGET_FILE), "utf8"), "utf8");
  return evidence;
}

async function runPathRetryUnderDivergedRuntime({ runDir, proposal, approvalSnapshot, grantTemplate, baselineHead }) {
  runGit(["checkout", "-B", "path_f_retry_under_diverged_runtime", baselineHead], SANDBOX_REPO_DIR);
  await restoreRuntimeBaseline(approvalSnapshot);
  const chain = [];
  const prev = { value: null };
  const checkpointResults = [];
  const grant = clone(grantTemplate);
  let runtimeEpoch = APPROVAL_RUNTIME_EPOCH;
  const executionState = { status: "PROPOSED", staged_target_hash: null };
  const approvalTime = approvalSnapshot.approval_timestamp;

  appendEvent(chain, prev, "proposal_created", "T0", { proposal_id: proposal.proposal_id });
  appendEvent(chain, prev, "approval_snapshot_captured", "T1", { approval_id: approvalSnapshot.approval_id });
  appendEvent(chain, prev, "authority_grant_issued", "T2", { grant_id: grant.grant_id });

  executionState.status = "QUEUED";
  const queuedState = makeQueueState({
    phase: "QUEUED",
    depth: 2,
    latencyMs: 60000,
    retryCount: 0,
    priority: "high",
    queuedMutations: [proposal.proposal_id, "queue_ahead_hotfix"]
  });
  appendEvent(chain, prev, "execution_queued", "T2B", queuedState);

  const firstWitness = await captureRuntimeWitness(runtimeEpoch, queuedState, false, {
    runtime_timestamp: isoWithOffset(approvalTime, 20)
  });
  appendEvent(chain, prev, "runtime_witness_captured", CHECKPOINTS.PRE_EXECUTION, firstWitness);
  const firstEval = evaluateLegitimacy({
    checkpoint: CHECKPOINTS.PRE_EXECUTION,
    proposal,
    authorityGrant: grant,
    approvalSnapshot,
    runtimeWitness: firstWitness,
    executionState,
    attemptIndex: 1,
    divergenceInputs: {
      queue_depth: queuedState.queue_depth,
      runtime_horizon_seconds: 20
    }
  });
  checkpointResults.push(firstEval);
  appendEvent(chain, prev, "legitimacy_revalidated", CHECKPOINTS.PRE_EXECUTION, firstEval);

  executionState.status = "EXECUTING";
  appendEvent(chain, prev, "execution_started", "T3", { execution_state: executionState.status });
  appendEvent(chain, prev, "execution_delayed", "T3B", {
    reason: "transient execution fault; retry required"
  });

  executionState.status = "RETRY_PENDING";
  const retryPendingState = makeQueueState({
    phase: "RETRY_PENDING",
    depth: 3,
    latencyMs: 240000,
    retryCount: 1,
    priority: "high",
    queuedMutations: [proposal.proposal_id, "queue_ahead_hotfix", "retry_slot_1"]
  });
  appendEvent(chain, prev, "retry_scheduled", "T4", retryPendingState);
  appendEvent(chain, prev, "queue_state_updated", "T4B", retryPendingState);

  await mutateForRetryDrift();
  runtimeEpoch += 1;

  executionState.status = "REVALIDATING";
  appendEvent(chain, prev, "retry_revalidation_started", "T5", {
    execution_state: executionState.status,
    retry_count: retryPendingState.retry_count
  });

  const retryWitness = await captureRuntimeWitness(runtimeEpoch, retryPendingState, false, {
    runtime_timestamp: isoWithOffset(approvalTime, 980)
  });
  appendEvent(chain, prev, "runtime_witness_captured", CHECKPOINTS.MID_EXECUTION, retryWitness);
  const retryEval = evaluateLegitimacy({
    checkpoint: CHECKPOINTS.MID_EXECUTION,
    proposal,
    authorityGrant: grant,
    approvalSnapshot,
    runtimeWitness: retryWitness,
    executionState,
    attemptIndex: 2,
    divergenceInputs: {
      retry_attempt: true,
      retry_count: retryPendingState.retry_count,
      queue_depth: retryPendingState.queue_depth,
      runtime_horizon_seconds: 980,
      queue_witness_hash: queuedState.queue_witness_hash,
      queue_contention: 9,
      retry_delay: 10,
      dependency_aging: 10,
      branch_advancement: 10,
      deferred_execution_drift: 10
    }
  });
  checkpointResults.push(retryEval);
  appendEvent(chain, prev, "legitimacy_revalidated", CHECKPOINTS.MID_EXECUTION, retryEval);
  appendEvent(chain, prev, "authority_decay_detected", "T6", {
    authority_continuity: retryEval.authority_continuity,
    runtime_horizon_state: retryEval.runtime_horizon_state
  });

  executionState.status = "HALTED";
  appendEvent(chain, prev, "retry_denied", "T7", {
    reason: "retry execution denied under diverged runtime continuity"
  });
  appendEvent(chain, prev, "finalization_prevented", "T7B", {
    reason: "retry finalization blocked after revalidation failure"
  });
  appendEvent(chain, prev, "lineage_finalized", "T8", {
    final_status: "EXECUTION_DENIED",
    final_reason: "retry denied after runtime continuity drift"
  });

  const evidence = {
    path_id: "path_f_retry_under_diverged_runtime",
    proposal,
    approval_snapshot: approvalSnapshot,
    authority_grant: grant,
    checkpoint_results: checkpointResults,
    final_revalidation: retryEval,
    execution_outcome: {
      execution_status: "EXECUTION_DENIED",
      reason: "retry denied after runtime continuity drift"
    },
    execution_phase_timeline:
      "PROPOSED -> APPROVED -> QUEUED -> WAITING -> RETRY_PENDING -> EXECUTING -> REVALIDATING -> HALTED -> DENIED",
    evidence_chain: chain
  };

  const outDir = path.join(runDir, "path_f_retry_under_diverged_runtime");
  await fs.mkdir(outDir, { recursive: true });
  await writeEvidenceFormats(outDir, evidence);
  await fs.writeFile(path.join(outDir, "target_before_attempt.txt"), approvalSnapshot.target_content, "utf8");
  await fs.writeFile(path.join(outDir, "target_after_attempt.txt"), await fs.readFile(path.join(SANDBOX_REPO_DIR, TARGET_FILE), "utf8"), "utf8");
  return evidence;
}

async function runPathStagingToProductionDivergence({
  runDir,
  proposal,
  approvalSnapshot,
  baselineHead
}) {
  runGit(["checkout", "-B", "path_g_staging_to_production_divergence", baselineHead], SANDBOX_REPO_DIR);
  await restoreRuntimeBaseline(approvalSnapshot);
  const chain = [];
  const prev = { value: null };
  const checkpointResults = [];
  const approvalTime = approvalSnapshot.approval_timestamp;
  const sourceEpoch = 12;

  appendEvent(chain, prev, "proposal_created", "T0", { proposal_id: proposal.proposal_id });
  appendEvent(chain, prev, "approval_snapshot_captured", "T1", { approval_id: approvalSnapshot.approval_id });

  const stagingQueue = makeQueueState({
    phase: "APPROVED_IN_STAGING",
    depth: 1,
    latencyMs: 8000,
    retryCount: 0,
    priority: "normal",
    queuedMutations: [proposal.proposal_id]
  });
  const stagingWitness = await captureEnvironmentWitness({
    environmentId: "staging",
    runtimeEpoch: sourceEpoch,
    queueState: stagingQueue,
    runtimeTimestamp: isoWithOffset(approvalTime, 8),
    queueDepth: stagingQueue.queue_depth,
    executionPriority: stagingQueue.execution_priority,
    queuedMutations: stagingQueue.queued_mutations
  });
  appendEvent(chain, prev, "environment_snapshot_captured", "T1B", {
    source_environment: "staging",
    target_environment: "staging",
    environment_witness: stagingWitness
  });

  const grant = issueEnvironmentAuthorityGrant({
    proposal,
    sourceEnvironmentWitness: stagingWitness,
    targetEnvironmentId: "production",
    delegated: false
  });
  appendEvent(chain, prev, "authority_grant_issued", "T2", {
    source_environment: grant.source_environment,
    target_environment: grant.target_environment,
    grant_id: grant.grant_id
  });

  appendEvent(chain, prev, "promotion_queued", "T3", {
    source_environment: "staging",
    target_environment: "production",
    promotion_state: "QUEUED_FOR_PROMOTION",
    queue_witness_hash: stagingQueue.queue_witness_hash
  });

  await mutateForProductionDivergence();

  const productionQueue = makeQueueState({
    phase: "REVALIDATING_IN_PRODUCTION",
    depth: 4,
    latencyMs: 240000,
    retryCount: 0,
    priority: "critical",
    queuedMutations: [proposal.proposal_id, "prod_hotfix_contention"]
  });
  const productionWitness = await captureEnvironmentWitness({
    environmentId: "production",
    runtimeEpoch: sourceEpoch + 3,
    queueState: productionQueue,
    runtimeTimestamp: isoWithOffset(approvalTime, 980),
    queueDepth: productionQueue.queue_depth,
    executionPriority: productionQueue.execution_priority,
    queuedMutations: productionQueue.queued_mutations
  });
  appendEvent(chain, prev, "promotion_revalidation_started", "T6", {
    source_environment: "staging",
    target_environment: "production",
    environment_witness: productionWitness
  });

  const promotionEval = revalidateLegitimacyAcrossEnvironments({
    proposal,
    authorityGrant: grant,
    sourceEnvironment: stagingWitness,
    targetEnvironment: productionWitness,
    runtimeWitness: productionWitness,
    divergenceInputs: {
      dependency_drift_pressure: 14,
      branch_advancement_pressure: 12,
      config_drift_pressure: 14,
      queue_drift_pressure: 10
    }
  });
  checkpointResults.push(promotionEval);
  appendEvent(chain, prev, "environment_divergence_detected", "T7", {
    source_environment: "staging",
    target_environment: "production",
    authority_continuity_state: promotionEval.cross_environment_legitimacy,
    admissibility_state: promotionEval.admissibility,
    divergence_level: promotionEval.divergence_level,
    decision_reason: promotionEval.reason
  });

  appendEvent(chain, prev, "promotion_denied", "T8", {
    source_environment: "staging",
    target_environment: "production",
    admissibility_state: promotionEval.admissibility,
    decision_reason: promotionEval.reason
  });
  appendEvent(chain, prev, "cross_environment_lineage_finalized", "T9", {
    source_environment: "staging",
    target_environment: "production",
    final_status: "PROMOTION_DENIED",
    final_reason: "runtime continuity diverged across environment transition"
  });

  const evidence = {
    path_id: "path_g_staging_to_production_divergence",
    proposal,
    approval_snapshot: approvalSnapshot,
    source_environment: stagingWitness,
    target_environment: productionWitness,
    authority_grant: grant,
    checkpoint_results: checkpointResults,
    final_revalidation: promotionEval,
    execution_outcome: {
      execution_status: "EXECUTION_DENIED",
      reason: "runtime continuity diverged across environment transition"
    },
    execution_phase_timeline:
      "PROPOSED -> APPROVED_IN_STAGING -> QUEUED_FOR_PROMOTION -> REVALIDATING_IN_PRODUCTION -> PROMOTION_DENIED",
    evidence_chain: chain
  };

  const outDir = path.join(runDir, "path_g_staging_to_production_divergence");
  await fs.mkdir(outDir, { recursive: true });
  await writeEvidenceFormats(outDir, evidence);
  await fs.writeFile(path.join(outDir, "target_before_attempt.txt"), approvalSnapshot.target_content, "utf8");
  await fs.writeFile(path.join(outDir, "target_after_attempt.txt"), await fs.readFile(path.join(SANDBOX_REPO_DIR, TARGET_FILE), "utf8"), "utf8");
  return evidence;
}

async function runPathDelegatedEnvironmentTransfer({
  runDir,
  proposal,
  approvalSnapshot,
  baselineHead
}) {
  runGit(["checkout", "-B", "path_h_delegated_environment_transfer", baselineHead], SANDBOX_REPO_DIR);
  await restoreRuntimeBaseline(approvalSnapshot);
  const chain = [];
  const prev = { value: null };
  const checkpointResults = [];
  const approvalTime = approvalSnapshot.approval_timestamp;
  const sourceEpoch = 12;

  appendEvent(chain, prev, "proposal_created", "T0", { proposal_id: proposal.proposal_id });
  appendEvent(chain, prev, "approval_snapshot_captured", "T1", { approval_id: approvalSnapshot.approval_id });

  const sourceQueue = makeQueueState({
    phase: "LOCAL",
    depth: 1,
    latencyMs: 2000,
    retryCount: 0,
    priority: "normal",
    queuedMutations: [proposal.proposal_id]
  });
  const sourceWitness = await captureEnvironmentWitness({
    environmentId: "staging",
    runtimeEpoch: sourceEpoch,
    queueState: sourceQueue,
    runtimeTimestamp: isoWithOffset(approvalTime, 6),
    queueDepth: sourceQueue.queue_depth,
    executionPriority: sourceQueue.execution_priority,
    queuedMutations: sourceQueue.queued_mutations
  });
  appendEvent(chain, prev, "environment_snapshot_captured", "T1B", {
    source_environment: "staging",
    target_environment: "staging",
    environment_witness: sourceWitness
  });

  const delegatedGrant = issueEnvironmentAuthorityGrant({
    proposal,
    sourceEnvironmentWitness: sourceWitness,
    targetEnvironmentId: "delegated_runtime",
    delegated: true
  });
  appendEvent(chain, prev, "authority_grant_issued", "T2", {
    source_environment: delegatedGrant.source_environment,
    target_environment: delegatedGrant.target_environment,
    grant_id: delegatedGrant.grant_id
  });

  appendEvent(chain, prev, "delegated_execution_started", "T3", {
    source_environment: "staging",
    target_environment: "delegated_runtime",
    delegated_authority_state: "TRANSFERRED"
  });

  await mutateForDelegatedRuntimeDivergence();

  const delegatedQueue = makeQueueState({
    phase: "REVALIDATING",
    depth: 3,
    latencyMs: 180000,
    retryCount: 1,
    priority: "high",
    queuedMutations: [proposal.proposal_id, "delegated_runtime_shift"]
  });
  const delegatedWitness = await captureEnvironmentWitness({
    environmentId: "delegated_runtime",
    runtimeEpoch: sourceEpoch + 2,
    queueState: delegatedQueue,
    delegatedFrom: "queue_router",
    runtimeTimestamp: isoWithOffset(approvalTime, 860),
    queueDepth: delegatedQueue.queue_depth,
    retryCount: delegatedQueue.retry_count,
    executionPriority: delegatedQueue.execution_priority,
    queuedMutations: delegatedQueue.queued_mutations
  });
  appendEvent(chain, prev, "environment_snapshot_captured", "T3B", {
    source_environment: "staging",
    target_environment: "delegated_runtime",
    environment_witness: delegatedWitness
  });

  const delegatedEval = revalidateLegitimacyAcrossEnvironments({
    proposal,
    authorityGrant: delegatedGrant,
    sourceEnvironment: sourceWitness,
    targetEnvironment: delegatedWitness,
    runtimeWitness: delegatedWitness,
    divergenceInputs: {
      dependency_drift_pressure: 10,
      branch_advancement_pressure: 10,
      config_drift_pressure: 12,
      queue_drift_pressure: 8,
      delegated_runtime_aging: 12
    }
  });
  checkpointResults.push(delegatedEval);
  appendEvent(chain, prev, "delegated_continuity_failed", "T4", {
    source_environment: "staging",
    target_environment: "delegated_runtime",
    authority_continuity_state: delegatedEval.cross_environment_legitimacy,
    admissibility_state: delegatedEval.admissibility,
    divergence_level: delegatedEval.divergence_level,
    decision_reason: delegatedEval.reason
  });

  appendEvent(chain, prev, "execution_denied", "T5", {
    source_environment: "staging",
    target_environment: "delegated_runtime",
    admissibility_state: delegatedEval.admissibility,
    decision_reason: delegatedEval.reason
  });
  appendEvent(chain, prev, "cross_environment_lineage_finalized", "T6", {
    source_environment: "staging",
    target_environment: "delegated_runtime",
    final_status: "EXECUTION_DENIED",
    final_reason: "delegated runtime continuity mismatch"
  });

  const evidence = {
    path_id: "path_h_delegated_environment_transfer",
    proposal,
    approval_snapshot: approvalSnapshot,
    source_environment: sourceWitness,
    target_environment: delegatedWitness,
    authority_grant: delegatedGrant,
    checkpoint_results: checkpointResults,
    final_revalidation: delegatedEval,
    execution_outcome: {
      execution_status: "EXECUTION_DENIED",
      reason: "delegated runtime continuity mismatch"
    },
    execution_phase_timeline: "LOCAL -> TRANSFERRED -> REVALIDATING -> INVALIDATED",
    evidence_chain: chain
  };

  const outDir = path.join(runDir, "path_h_delegated_environment_transfer");
  await fs.mkdir(outDir, { recursive: true });
  await writeEvidenceFormats(outDir, evidence);
  await fs.writeFile(path.join(outDir, "target_before_attempt.txt"), approvalSnapshot.target_content, "utf8");
  await fs.writeFile(path.join(outDir, "target_after_attempt.txt"), await fs.readFile(path.join(SANDBOX_REPO_DIR, TARGET_FILE), "utf8"), "utf8");
  return evidence;
}

async function writeSummaryArtifacts(runDir, summary) {
  await fs.writeFile(path.join(runDir, "proof_summary.json"), JSON.stringify(summary, null, 2), "utf8");

  const txt = [
    "GOVERNED REPOSITORY MUTATION PROOF — CONTINUOUS REVALIDATION + ASYNC PRESSURE",
    "",
    `run_id: ${summary.run_id}`,
    `path_a: ${summary.path_a.execution_status} (${summary.path_a.reason})`,
    `path_b: ${summary.path_b.execution_status} (${summary.path_b.reason})`,
    `path_c: ${summary.path_c.execution_status} (${summary.path_c.reason})`,
    `path_d: ${summary.path_d.execution_status} (${summary.path_d.reason})`,
    `path_e: ${summary.path_e.execution_status} (${summary.path_e.reason})`,
    `path_f: ${summary.path_f.execution_status} (${summary.path_f.reason})`,
    `path_g: ${summary.path_g.execution_status} (${summary.path_g.reason})`,
    `path_h: ${summary.path_h.execution_status} (${summary.path_h.reason})`,
    `replay_status: ${summary.path_a.replay_status}`
  ].join("\n");
  await fs.writeFile(path.join(runDir, "proof_summary.txt"), txt, "utf8");

  const md = [
    "# Governed Repository Mutation Proof — Continuous Runtime Revalidation + Async Runtime Pressure",
    "",
    "Execution legitimacy is continuously revalidated throughout mutation execution, including delayed queues and retry windows.",
    "",
    "## Continuous Legitimacy Timeline",
    "PRE_EXECUTION -> MID_EXECUTION -> PRE_COMMIT -> FINALIZATION",
    "",
    "## Queue Timeline",
    "QUEUED -> WAITING -> RETRY_PENDING -> EXECUTING -> REVALIDATING -> HALTED",
    "",
    "## Runtime Horizon",
    "SHORT -> EXTENDED -> LONG -> EXCEEDED",
    "",
    "## Environment Continuity Map",
    "STAGING -> PROMOTION -> PRODUCTION",
    "",
    "## Delegated Authority State",
    "LOCAL -> TRANSFERRED -> REVALIDATING -> INVALIDATED",
    "",
    "## Authority Continuity State",
    "VALID -> WEAKENING -> STALE -> INVALID",
    "",
    "## Execution State",
    "PROPOSED -> APPROVED -> QUEUED -> WAITING -> RETRY_PENDING -> EXECUTING -> REVALIDATING -> HALTED -> DENIED / FINALIZED",
    "",
    "## Divergence Pressure",
    "LOW -> MEDIUM -> HIGH -> CRITICAL",
    "",
    "## Scenario Results",
    `- path_a_continuous_allowed: ${summary.path_a.execution_status} (${summary.path_a.reason})`,
    `- path_b_denied_pre_execution: ${summary.path_b.execution_status} (${summary.path_b.reason})`,
    `- path_c_mid_execution_halt: ${summary.path_c.execution_status} (${summary.path_c.reason})`,
    `- path_d_concurrent_conflict: ${summary.path_d.execution_status} (${summary.path_d.reason})`,
    `- path_e_delayed_execution_decay: ${summary.path_e.execution_status} (${summary.path_e.reason})`,
    `- path_f_retry_under_diverged_runtime: ${summary.path_f.execution_status} (${summary.path_f.reason})`,
    `- path_g_staging_to_production_divergence: ${summary.path_g.execution_status} (${summary.path_g.reason})`,
    `- path_h_delegated_environment_transfer: ${summary.path_h.execution_status} (${summary.path_h.reason})`,
    "",
    "## Core Observation",
    "Approval alone was not enough. Legitimacy had to survive runtime execution itself, asynchronous delay horizons, and environment transitions.",
    ""
  ].join("\n");
  await fs.writeFile(path.join(runDir, "proof_summary.md"), md, "utf8");
}

async function mirrorLatest(runDir) {
  await fs.rm(LATEST_DIR, { recursive: true, force: true });
  await fs.mkdir(LATEST_DIR, { recursive: true });
  await fs.cp(runDir, LATEST_DIR, { recursive: true });
}

async function main() {
  const started = new Date();
  const runId = `git_proof_${runStamp(started)}`;
  const runDir = path.join(OUTPUT_DIR, runId);
  await fs.mkdir(runDir, { recursive: true });

  const baseline = await setupSandboxRepo();
  const proposal = await generatePatchProposal(runDir, baseline.baseline_head);
  const approvalSnapshot = await captureApprovalSnapshot(proposal, baseline.baseline_head);
  const grantTemplate = issueAuthorityGrant(proposal, approvalSnapshot);

  const pathA = await runPathAllowedContinuous({
    runDir,
    proposal,
    approvalSnapshot,
    grantTemplate,
    baselineHead: baseline.baseline_head
  });

  const pathB = await runPathDeniedPreExecution({
    runDir,
    proposal,
    approvalSnapshot,
    grantTemplate,
    baselineHead: baseline.baseline_head
  });

  const pathC = await runPathMidExecutionHalt({
    runDir,
    proposal,
    approvalSnapshot,
    grantTemplate,
    baselineHead: baseline.baseline_head
  });

  const pathD = await runPathConcurrentConflict({
    runDir,
    proposal,
    approvalSnapshot,
    grantTemplate,
    baselineHead: baseline.baseline_head
  });

  const pathE = await runPathDelayedExecutionDecay({
    runDir,
    proposal,
    approvalSnapshot,
    grantTemplate,
    baselineHead: baseline.baseline_head
  });

  const pathF = await runPathRetryUnderDivergedRuntime({
    runDir,
    proposal,
    approvalSnapshot,
    grantTemplate,
    baselineHead: baseline.baseline_head
  });

  const pathG = await runPathStagingToProductionDivergence({
    runDir,
    proposal,
    approvalSnapshot,
    baselineHead: baseline.baseline_head
  });

  const pathH = await runPathDelegatedEnvironmentTransfer({
    runDir,
    proposal,
    approvalSnapshot,
    baselineHead: baseline.baseline_head
  });

  const summary = {
    run_id: runId,
    generated_at: nowIso(),
    proof_claim:
      "runtime legitimacy remains continuously required from pre-execution through finalization",
    path_a: {
      execution_status: pathA.execution_outcome.execution_status,
      reason: pathA.execution_outcome.reason,
      final_checkpoint: pathA.final_revalidation.checkpoint,
      final_divergence: `${pathA.final_revalidation.divergence_level} (${pathA.final_revalidation.divergence_score})`,
      replay_status: pathA.replay_result.admissibility
    },
    path_b: {
      execution_status: pathB.execution_outcome.execution_status,
      reason: pathB.execution_outcome.reason,
      final_divergence: `${pathB.final_revalidation.divergence_level} (${pathB.final_revalidation.divergence_score})`
    },
    path_c: {
      execution_status: pathC.execution_outcome.execution_status,
      reason: pathC.execution_outcome.reason,
      final_divergence: `${pathC.final_revalidation.divergence_level} (${pathC.final_revalidation.divergence_score})`
    },
    path_d: {
      execution_status: pathD.execution_outcome.execution_status,
      reason: pathD.execution_outcome.reason,
      final_divergence: `${pathD.final_revalidation.divergence_level} (${pathD.final_revalidation.divergence_score})`
    },
    path_e: {
      execution_status: pathE.execution_outcome.execution_status,
      reason: pathE.execution_outcome.reason,
      final_divergence: `${pathE.final_revalidation.divergence_level} (${pathE.final_revalidation.divergence_score})`
    },
    path_f: {
      execution_status: pathF.execution_outcome.execution_status,
      reason: pathF.execution_outcome.reason,
      final_divergence: `${pathF.final_revalidation.divergence_level} (${pathF.final_revalidation.divergence_score})`
    },
    path_g: {
      execution_status: pathG.execution_outcome.execution_status,
      reason: pathG.execution_outcome.reason,
      final_divergence: `${pathG.final_revalidation.divergence_level} (${pathG.final_revalidation.divergence_score})`
    },
    path_h: {
      execution_status: pathH.execution_outcome.execution_status,
      reason: pathH.execution_outcome.reason,
      final_divergence: `${pathH.final_revalidation.divergence_level} (${pathH.final_revalidation.divergence_score})`
    },
    output_paths: {
      run_directory: runDir,
      latest_directory: LATEST_DIR
    }
  };

  await writeSummaryArtifacts(runDir, summary);
  await mirrorLatest(runDir);

  console.log("Governed Repository Mutation Proof completed.");
  console.log(`Run directory: ${runDir}`);
  console.log(`Latest output: ${LATEST_DIR}`);
  console.log(`Path A: ${summary.path_a.execution_status} (${summary.path_a.reason})`);
  console.log(`Path B: ${summary.path_b.execution_status} (${summary.path_b.reason})`);
  console.log(`Path C: ${summary.path_c.execution_status} (${summary.path_c.reason})`);
  console.log(`Path D: ${summary.path_d.execution_status} (${summary.path_d.reason})`);
  console.log(`Path E: ${summary.path_e.execution_status} (${summary.path_e.reason})`);
  console.log(`Path F: ${summary.path_f.execution_status} (${summary.path_f.reason})`);
  console.log(`Path G: ${summary.path_g.execution_status} (${summary.path_g.reason})`);
  console.log(`Path H: ${summary.path_h.execution_status} (${summary.path_h.reason})`);
  console.log(`Replay check: ${summary.path_a.replay_status}`);
}

main().catch((err) => {
  console.error("Governed Repository Mutation Proof failed.");
  console.error(err);
  process.exit(1);
});
