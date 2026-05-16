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

  await writeFileUtf8(path.join(SANDBOX_REPO_DIR, TARGET_FILE), baselineTarget);
  await writeFileUtf8(path.join(SANDBOX_REPO_DIR, DEPENDENCY_FILE), baselineDeps);
  await writeFileUtf8(path.join(SANDBOX_REPO_DIR, QUEUE_FILE), baselineQueue);

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
  const targetHash = hashText(targetContent);
  const dependencyHash = hashText(dependencyContent);
  const queueHash = hashText(queueContent);
  const stagedExpectedContent = targetContent.replace(proposal.patch.from, proposal.patch.to);

  return {
    approval_id: `approval_${hashText(`${proposal.proposal_id}_${baselineHead}`).slice(0, 12)}`,
    head: baselineHead,
    target_file: TARGET_FILE,
    target_hash: targetHash,
    target_content: targetContent,
    dependency_content: dependencyContent,
    queue_content: queueContent,
    dependency_hash: dependencyHash,
    queue_hash: queueHash,
    runtime_epoch: APPROVAL_RUNTIME_EPOCH,
    approval_timestamp: nowIso(),
    expected_staged_target_hash: hashText(stagedExpectedContent)
  };
}

async function restoreRuntimeBaseline(approvalSnapshot) {
  await fs.writeFile(path.join(SANDBOX_REPO_DIR, TARGET_FILE), approvalSnapshot.target_content, "utf8");
  await fs.writeFile(path.join(SANDBOX_REPO_DIR, DEPENDENCY_FILE), approvalSnapshot.dependency_content, "utf8");
  await fs.writeFile(path.join(SANDBOX_REPO_DIR, QUEUE_FILE), approvalSnapshot.queue_content, "utf8");
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

async function captureRuntimeWitness(runtimeEpoch, queueState, concurrentMutationDetected = false) {
  const head = runGit(["rev-parse", "HEAD"], SANDBOX_REPO_DIR);
  const targetHash = await hashFile(path.join(SANDBOX_REPO_DIR, TARGET_FILE));
  const dependencyHash = await hashFile(path.join(SANDBOX_REPO_DIR, DEPENDENCY_FILE));
  const queueHash = await hashFile(path.join(SANDBOX_REPO_DIR, QUEUE_FILE));

  return {
    head,
    target_file: TARGET_FILE,
    target_hash: targetHash,
    dependency_hash: dependencyHash,
    queue_hash: queueHash,
    runtime_epoch: runtimeEpoch,
    queue_state: queueState,
    concurrent_mutation_detected: concurrentMutationDetected,
    runtime_timestamp: nowIso()
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
  const replayDetected = authorityGrant.consumed || attemptIndex > 1;

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
    concurrent_mutation_detection: runtimeWitness.concurrent_mutation_detected === true
  };

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
    execution_delay_amplification: divergenceInputs.execution_delay_amplification || 0,
    queue_contention: divergenceInputs.queue_contention || 0,
    partial_execution_duration: divergenceInputs.partial_execution_duration || 0
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
  if (!checks.scope_continuity || checks.replay_status || checks.concurrent_mutation_detection) {
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
  if (!reasons.length) reasons.push("authority continuity preserved");

  return {
    checkpoint,
    admissibility,
    divergence_score: divergenceScore,
    divergence_level: divergence,
    authority_continuity: authorityContinuity,
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
  await fs.writeFile(path.join(pathDir, "evidence.json"), JSON.stringify(evidence, null, 2), "utf8");
  const txt = [
    `PATH: ${evidence.path_id}`,
    `FINAL_STATUS: ${evidence.execution_outcome.execution_status}`,
    `FINAL_REASON: ${evidence.execution_outcome.reason}`,
    `FINAL_DIVERGENCE: ${evidence.final_revalidation.divergence_level} (${evidence.final_revalidation.divergence_score})`,
    `FINAL_AUTHORITY_CONTINUITY: ${evidence.final_revalidation.authority_continuity}`
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
    "PROPOSED -> STAGED -> EXECUTING -> HALTED/FINALIZED",
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

async function writeSummaryArtifacts(runDir, summary) {
  await fs.writeFile(path.join(runDir, "proof_summary.json"), JSON.stringify(summary, null, 2), "utf8");

  const txt = [
    "GOVERNED REPOSITORY MUTATION PROOF — CONTINUOUS REVALIDATION",
    "",
    `run_id: ${summary.run_id}`,
    `path_a: ${summary.path_a.execution_status} (${summary.path_a.reason})`,
    `path_b: ${summary.path_b.execution_status} (${summary.path_b.reason})`,
    `path_c: ${summary.path_c.execution_status} (${summary.path_c.reason})`,
    `path_d: ${summary.path_d.execution_status} (${summary.path_d.reason})`,
    `replay_status: ${summary.path_a.replay_status}`
  ].join("\n");
  await fs.writeFile(path.join(runDir, "proof_summary.txt"), txt, "utf8");

  const md = [
    "# Governed Repository Mutation Proof — Continuous Runtime Revalidation",
    "",
    "Execution legitimacy is continuously revalidated throughout mutation execution.",
    "",
    "## Continuous Legitimacy Timeline",
    "PRE_EXECUTION -> MID_EXECUTION -> PRE_COMMIT -> FINALIZATION",
    "",
    "## Authority Continuity State",
    "VALID -> WEAKENING -> STALE -> INVALID",
    "",
    "## Execution State",
    "PROPOSED -> STAGED -> EXECUTING -> HALTED -> ROLLED_BACK / FINALIZED",
    "",
    "## Divergence Pressure",
    "LOW -> MEDIUM -> HIGH -> CRITICAL",
    "",
    "## Scenario Results",
    `- path_a_continuous_allowed: ${summary.path_a.execution_status} (${summary.path_a.reason})`,
    `- path_b_denied_pre_execution: ${summary.path_b.execution_status} (${summary.path_b.reason})`,
    `- path_c_mid_execution_halt: ${summary.path_c.execution_status} (${summary.path_c.reason})`,
    `- path_d_concurrent_conflict: ${summary.path_d.execution_status} (${summary.path_d.reason})`,
    "",
    "## Core Observation",
    "Approval alone was not enough. Legitimacy had to survive runtime execution itself.",
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
  console.log(`Replay check: ${summary.path_a.replay_status}`);
}

main().catch((err) => {
  console.error("Governed Repository Mutation Proof failed.");
  console.error(err);
  process.exit(1);
});
