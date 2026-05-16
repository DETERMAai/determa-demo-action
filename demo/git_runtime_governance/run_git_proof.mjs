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

function hashText(input) {
  return crypto.createHash("sha256").update(input, "utf8").digest("hex");
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

function authorityContinuityState(score, replayDetected) {
  if (replayDetected || score >= 80) return "INVALID";
  if (score >= 55) return "STALE";
  if (score >= 30) return "WEAKENING";
  return "VALID";
}

function evaluateLegitimacy(proposal, authorityGrant, approvalSnapshot, runtimeWitness, attemptIndex) {
  const approvalMs = new Date(approvalSnapshot.approval_timestamp).getTime();
  const runtimeMs = new Date(runtimeWitness.runtime_timestamp).getTime();
  const elapsedSeconds = Math.max(0, Math.floor((runtimeMs - approvalMs) / 1000));
  const replayDetected = authorityGrant.consumed || attemptIndex > 1;

  const checks = {
    head_continuity: runtimeWitness.head === approvalSnapshot.head,
    target_hash_continuity: runtimeWitness.target_hash === approvalSnapshot.target_hash,
    freshness: elapsedSeconds <= authorityGrant.freshness_window_seconds,
    replay_status: replayDetected,
    scope_continuity:
      proposal.target_file === authorityGrant.scope.target_file &&
      proposal.patch_hash === authorityGrant.scope.patch_hash,
    dependency_continuity: runtimeWitness.dependency_hash === approvalSnapshot.dependency_hash,
    runtime_epoch_continuity: runtimeWitness.runtime_epoch === approvalSnapshot.runtime_epoch,
    queue_continuity: runtimeWitness.queue_hash === approvalSnapshot.queue_hash
  };

  const penalties = {
    head_continuity: checks.head_continuity ? 0 : 26,
    target_hash_continuity: checks.target_hash_continuity ? 0 : 26,
    freshness: checks.freshness ? 0 : 8,
    replay_status: checks.replay_status ? 24 : 0,
    scope_continuity: checks.scope_continuity ? 0 : 30,
    dependency_continuity: checks.dependency_continuity ? 0 : 18,
    runtime_epoch_continuity: checks.runtime_epoch_continuity ? 0 : 12,
    queue_continuity: checks.queue_continuity ? 0 : 8
  };

  const divergenceScoreRaw = Object.values(penalties).reduce((sum, p) => sum + p, 0);
  const divergenceScore = Math.min(100, divergenceScoreRaw);
  const divergence = divergenceLevel(divergenceScore);
  const authorityContinuity = authorityContinuityState(divergenceScore, checks.replay_status);

  let admissibility = "ADMISSIBLE";
  if (!checks.scope_continuity || checks.replay_status) {
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
  if (!checks.freshness) reasons.push("authority grant freshness window expired");
  if (!checks.scope_continuity) reasons.push("proposal scope no longer matches grant scope");
  if (checks.replay_status) reasons.push("single-use authority grant replay detected");
  if (!reasons.length) reasons.push("authority continuity preserved");

  return {
    admissibility,
    divergence_score: divergenceScore,
    divergence_level: divergence,
    authority_continuity: authorityContinuity,
    elapsed_seconds: elapsedSeconds,
    checks,
    reason: reasons.join("; ")
  };
}

function appendEvent(chain, prevRef, eventType, phase, payload) {
  const eventId = `evt_${String(chain.length + 1).padStart(4, "0")}_${hashText(`${eventType}_${chain.length + 1}`).slice(0, 8)}`;
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

async function writeFileUtf8(filePath, content) {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, content, "utf8");
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
    baseline_target: baselineTarget,
    baseline_dependencies: baselineDeps,
    baseline_queue: baselineQueue,
    baseline_head: runGit(["rev-parse", "HEAD"], SANDBOX_REPO_DIR)
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

  runGit(["checkout", "--", TARGET_FILE], SANDBOX_REPO_DIR);

  const patchDir = path.join(runDir, "proposal");
  await fs.mkdir(patchDir, { recursive: true });
  const patchFile = path.join(patchDir, "mutation.patch");
  await fs.writeFile(patchFile, patchContent, "utf8");

  const patchHash = hashText(patchContent);
  const createdAt = nowIso();

  return {
    proposal_id: `proposal_${patchHash.slice(0, 12)}`,
    target_file: TARGET_FILE,
    patch_hash: patchHash,
    patch_file: patchFile,
    approval_head: baselineHead,
    runtime_epoch: APPROVAL_RUNTIME_EPOCH,
    created_at: createdAt,
    mutation_scope: "runtime.config.worker",
    patch_preview: "MAX_RETRIES=3 -> MAX_RETRIES=5"
  };
}

async function captureApprovalSnapshot(proposal, baselineHead) {
  const targetHash = await hashFile(path.join(SANDBOX_REPO_DIR, TARGET_FILE));
  const dependencyHash = await hashFile(path.join(SANDBOX_REPO_DIR, DEPENDENCY_FILE));
  const queueHash = await hashFile(path.join(SANDBOX_REPO_DIR, QUEUE_FILE));

  return {
    approval_id: `approval_${hashText(`${proposal.proposal_id}_${baselineHead}`).slice(0, 12)}`,
    head: baselineHead,
    target_file: TARGET_FILE,
    target_hash: targetHash,
    dependency_hash: dependencyHash,
    queue_hash: queueHash,
    runtime_epoch: APPROVAL_RUNTIME_EPOCH,
    approval_timestamp: nowIso()
  };
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

async function captureRuntimeWitness(runtimeEpoch, queueState) {
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
    runtime_timestamp: nowIso()
  };
}

async function mutateRepositoryAfterApproval() {
  const depsPath = path.join(SANDBOX_REPO_DIR, DEPENDENCY_FILE);
  const queuePath = path.join(SANDBOX_REPO_DIR, QUEUE_FILE);

  const deps = JSON.parse(await fs.readFile(depsPath, "utf8"));
  deps["runtime-core"] = "2.5.0";
  await fs.writeFile(depsPath, JSON.stringify(deps, null, 2) + "\n", "utf8");

  const queue = JSON.parse(await fs.readFile(queuePath, "utf8"));
  queue.pending_mutations.push({
    id: "queued_hotfix_01",
    status: "pending"
  });
  queue.queue_epoch = 2;
  await fs.writeFile(queuePath, JSON.stringify(queue, null, 2) + "\n", "utf8");

  runGit(["add", DEPENDENCY_FILE, QUEUE_FILE], SANDBOX_REPO_DIR);
  runGit(["commit", "-m", "runtime drift mutation before patch execution"], SANDBOX_REPO_DIR);
}

async function applyPatchAndCommit(patchFile, commitMessage) {
  const apply = safeRunGit(["apply", "--index", patchFile], SANDBOX_REPO_DIR);
  if (!apply.ok) {
    return {
      applied: false,
      error: apply.error || apply.output || "git apply failed"
    };
  }
  runGit(["commit", "-m", commitMessage], SANDBOX_REPO_DIR);
  return {
    applied: true,
    head_after_commit: runGit(["rev-parse", "HEAD"], SANDBOX_REPO_DIR)
  };
}

function evidenceToText(evidence) {
  return [
    `PATH: ${evidence.path_id}`,
    `EXECUTION: ${evidence.execution_outcome.execution_status}`,
    `REASON: ${evidence.execution_outcome.reason}`,
    `ADMISSIBILITY: ${evidence.admissibility_result.admissibility}`,
    `AUTHORITY_CONTINUITY: ${evidence.admissibility_result.authority_continuity}`,
    `DIVERGENCE: ${evidence.admissibility_result.divergence_level} (${evidence.admissibility_result.divergence_score})`,
    `HEAD_APPROVAL: ${evidence.approval_snapshot.head}`,
    `HEAD_RUNTIME: ${evidence.runtime_witness.head}`
  ].join("\n");
}

function evidenceToMarkdown(evidence) {
  return [
    `# ${evidence.path_id}`,
    "",
    `- execution_status: ${evidence.execution_outcome.execution_status}`,
    `- reason: ${evidence.execution_outcome.reason}`,
    `- admissibility: ${evidence.admissibility_result.admissibility}`,
    `- authority_continuity: ${evidence.admissibility_result.authority_continuity}`,
    `- divergence_level: ${evidence.admissibility_result.divergence_level}`,
    `- divergence_score: ${evidence.admissibility_result.divergence_score}`,
    "",
    "## Checks",
    ...Object.entries(evidence.admissibility_result.checks).map(([k, v]) => `- ${k}: ${v}`),
    "",
    "## Lineage Events",
    ...evidence.evidence_chain.map((evt) => `- ${evt.event_id} ${evt.event_type} (prev=${evt.previous_event_id || "null"})`)
  ].join("\n");
}

async function writeEvidenceFormats(pathDir, evidence) {
  await fs.writeFile(path.join(pathDir, "evidence.json"), JSON.stringify(evidence, null, 2), "utf8");
  await fs.writeFile(path.join(pathDir, "evidence.txt"), evidenceToText(evidence), "utf8");
  await fs.writeFile(path.join(pathDir, "evidence.md"), evidenceToMarkdown(evidence), "utf8");
}

async function runPath({
  pathId,
  branchName,
  baselineHead,
  proposal,
  approvalSnapshot,
  authorityGrantTemplate,
  mutateAfterApproval,
  enableReplayProof,
  runDir
}) {
  runGit(["checkout", "-B", branchName, baselineHead], SANDBOX_REPO_DIR);

  const evidenceChain = [];
  const previousEvent = { value: null };
  const authorityGrant = clone(authorityGrantTemplate);
  const pathOutputDir = path.join(runDir, pathId);
  await fs.mkdir(pathOutputDir, { recursive: true });

  appendEvent(evidenceChain, previousEvent, "proposal_created", "P1", {
    proposal_id: proposal.proposal_id,
    patch_hash: proposal.patch_hash,
    target_file: proposal.target_file
  });

  appendEvent(evidenceChain, previousEvent, "approval_snapshot_captured", "P2", {
    approval_id: approvalSnapshot.approval_id,
    head: approvalSnapshot.head,
    target_hash: approvalSnapshot.target_hash,
    dependency_hash: approvalSnapshot.dependency_hash,
    runtime_epoch: approvalSnapshot.runtime_epoch
  });

  appendEvent(evidenceChain, previousEvent, "authority_grant_issued", "P3", {
    grant_id: authorityGrant.grant_id,
    single_use: authorityGrant.single_use,
    freshness_window_seconds: authorityGrant.freshness_window_seconds,
    scope: authorityGrant.scope
  });

  let runtimeEpoch = APPROVAL_RUNTIME_EPOCH;
  let queueState = "stable";
  if (mutateAfterApproval) {
    await mutateRepositoryAfterApproval();
    runtimeEpoch = APPROVAL_RUNTIME_EPOCH + 1;
    queueState = "mutated";
  }

  const runtimeWitness = await captureRuntimeWitness(runtimeEpoch, queueState);
  appendEvent(evidenceChain, previousEvent, "runtime_witness_captured", "P4", {
    head: runtimeWitness.head,
    target_hash: runtimeWitness.target_hash,
    dependency_hash: runtimeWitness.dependency_hash,
    runtime_epoch: runtimeWitness.runtime_epoch,
    queue_hash: runtimeWitness.queue_hash
  });

  const admissibilityResult = evaluateLegitimacy(
    proposal,
    authorityGrant,
    approvalSnapshot,
    runtimeWitness,
    1
  );

  appendEvent(evidenceChain, previousEvent, "admissibility_evaluated", "P5", {
    admissibility: admissibilityResult.admissibility,
    authority_continuity: admissibilityResult.authority_continuity,
    divergence_level: admissibilityResult.divergence_level,
    divergence_score: admissibilityResult.divergence_score,
    reason: admissibilityResult.reason,
    checks: admissibilityResult.checks
  });

  const targetBeforeAttempt = await hashFile(path.join(SANDBOX_REPO_DIR, TARGET_FILE));
  const targetBeforeContent = await fs.readFile(path.join(SANDBOX_REPO_DIR, TARGET_FILE), "utf8");
  let executionOutcome;
  if (admissibilityResult.admissibility === "ADMISSIBLE") {
    const applied = await applyPatchAndCommit(proposal.patch_file, "governed mutation applied");
    if (!applied.applied) {
      executionOutcome = {
        execution_status: "EXECUTION_DENIED",
        reason: "patch application failed despite admissible state",
        patch_applied: false,
        target_hash_before_attempt: targetBeforeAttempt,
        target_hash_after_attempt: targetBeforeAttempt,
        target_changed_by_attempt: false,
        runtime_head_after_attempt: runGit(["rev-parse", "HEAD"], SANDBOX_REPO_DIR)
      };
    } else {
      authorityGrant.consumed = true;
      const targetAfterAttempt = await hashFile(path.join(SANDBOX_REPO_DIR, TARGET_FILE));
      executionOutcome = {
        execution_status: "EXECUTION_ALLOWED",
        reason: "authority continuity preserved",
        patch_applied: true,
        target_hash_before_attempt: targetBeforeAttempt,
        target_hash_after_attempt: targetAfterAttempt,
        target_changed_by_attempt: targetBeforeAttempt !== targetAfterAttempt,
        runtime_head_after_attempt: applied.head_after_commit
      };
    }
  } else {
    const targetAfterAttempt = await hashFile(path.join(SANDBOX_REPO_DIR, TARGET_FILE));
    executionOutcome = {
      execution_status: "EXECUTION_DENIED",
      reason: "repository runtime state diverged after approval",
      patch_applied: false,
      target_hash_before_attempt: targetBeforeAttempt,
      target_hash_after_attempt: targetAfterAttempt,
      runtime_head_after_attempt: runGit(["rev-parse", "HEAD"], SANDBOX_REPO_DIR),
      target_unchanged_by_attempt: targetBeforeAttempt === targetAfterAttempt
    };
  }

  appendEvent(
    evidenceChain,
    previousEvent,
    executionOutcome.execution_status === "EXECUTION_ALLOWED" ? "execution_allowed" : "execution_denied",
    "P6",
    clone(executionOutcome)
  );

  let replayResult = null;
  if (enableReplayProof) {
    const replayWitness = await captureRuntimeWitness(runtimeEpoch + 1, "replay_attempt");
    appendEvent(evidenceChain, previousEvent, "runtime_witness_captured", "P6B", {
      replay_attempt: true,
      head: replayWitness.head,
      target_hash: replayWitness.target_hash,
      dependency_hash: replayWitness.dependency_hash,
      runtime_epoch: replayWitness.runtime_epoch
    });

    replayResult = evaluateLegitimacy(
      proposal,
      authorityGrant,
      approvalSnapshot,
      replayWitness,
      2
    );

    appendEvent(evidenceChain, previousEvent, "admissibility_evaluated", "P6C", {
      replay_attempt: true,
      admissibility: replayResult.admissibility,
      authority_continuity: replayResult.authority_continuity,
      divergence_level: replayResult.divergence_level,
      divergence_score: replayResult.divergence_score,
      reason: replayResult.reason,
      checks: replayResult.checks
    });

    appendEvent(evidenceChain, previousEvent, "execution_denied", "P6D", {
      replay_attempt: true,
      execution_status: "EXECUTION_DENIED",
      reason: "single-use authority replay invalidated runtime authority continuity"
    });
  }

  appendEvent(evidenceChain, previousEvent, "lineage_finalized", "P7", {
    path_id: pathId,
    final_execution_status: executionOutcome.execution_status,
    final_reason: executionOutcome.reason
  });

  const evidence = {
    path_id: pathId,
    proposal,
    approval_snapshot: approvalSnapshot,
    authority_grant: authorityGrant,
    runtime_witness: runtimeWitness,
    admissibility_result: admissibilityResult,
    execution_outcome: executionOutcome,
    replay_result: replayResult,
    evidence_chain: evidenceChain
  };

  await writeEvidenceFormats(pathOutputDir, evidence);
  await fs.writeFile(path.join(pathOutputDir, "target_before_attempt.txt"), targetBeforeContent, "utf8");
  await fs.writeFile(
    path.join(pathOutputDir, "target_after_attempt.txt"),
    await fs.readFile(path.join(SANDBOX_REPO_DIR, TARGET_FILE), "utf8"),
    "utf8"
  );
  return evidence;
}

async function writeSummaryArtifacts(runDir, summary) {
  await fs.writeFile(path.join(runDir, "proof_summary.json"), JSON.stringify(summary, null, 2), "utf8");

  const txt = [
    "GOVERNED REPOSITORY MUTATION PROOF",
    "",
    `run_id: ${summary.run_id}`,
    `path_a_status: ${summary.path_a.execution_status}`,
    `path_a_reason: ${summary.path_a.reason}`,
    `path_b_status: ${summary.path_b.execution_status}`,
    `path_b_reason: ${summary.path_b.reason}`,
    `replay_status: ${summary.path_a.replay_status}`
  ].join("\n");
  await fs.writeFile(path.join(runDir, "proof_summary.txt"), txt, "utf8");

  const md = [
    "# Governed Repository Mutation Proof",
    "",
    "Same patch. Same authority model. Different repository runtime state. Different execution outcome.",
    "",
    "## Path A — Patch Allowed",
    "",
    `- status: ${summary.path_a.execution_status}`,
    `- reason: ${summary.path_a.reason}`,
    "",
    "## Path B — Patch Denied",
    "",
    `- status: ${summary.path_b.execution_status}`,
    `- reason: ${summary.path_b.reason}`,
    "",
    "## Replay Invalidation",
    "",
    `- replay attempt status: ${summary.path_a.replay_status}`,
    `- replay reason: ${summary.path_a.replay_reason}`,
    "",
    "## Runtime Divergence",
    "",
    `- path_a: ${summary.path_a.divergence_level} (${summary.path_a.divergence_score})`,
    `- path_b: ${summary.path_b.divergence_level} (${summary.path_b.divergence_score})`,
    "",
    "## State Visualization",
    "",
    "Authority Continuity",
    "VALID -> WEAKENING -> STALE -> INVALID",
    "",
    "Mutation Admissibility",
    "ADMISSIBLE -> REQUIRES_REVALIDATION -> DENIED",
    "",
    "Runtime Divergence",
    "LOW -> MEDIUM -> HIGH -> CRITICAL",
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

  const pathA = await runPath({
    pathId: "path_a_allowed",
    branchName: "path_a_allowed",
    baselineHead: baseline.baseline_head,
    proposal,
    approvalSnapshot,
    authorityGrantTemplate: grantTemplate,
    mutateAfterApproval: false,
    enableReplayProof: true,
    runDir
  });

  const pathB = await runPath({
    pathId: "path_b_denied",
    branchName: "path_b_denied",
    baselineHead: baseline.baseline_head,
    proposal,
    approvalSnapshot,
    authorityGrantTemplate: grantTemplate,
    mutateAfterApproval: true,
    enableReplayProof: false,
    runDir
  });

  const summary = {
    run_id: runId,
    generated_at: nowIso(),
    proof_claim:
      "identical repository mutation proposals can be allowed or denied based on runtime continuity",
    path_a: {
      execution_status: pathA.execution_outcome.execution_status,
      reason: pathA.execution_outcome.reason,
      divergence_level: pathA.admissibility_result.divergence_level,
      divergence_score: pathA.admissibility_result.divergence_score,
      replay_status: pathA.replay_result ? pathA.replay_result.admissibility : "NOT_RUN",
      replay_reason: pathA.replay_result ? pathA.replay_result.reason : "NOT_RUN"
    },
    path_b: {
      execution_status: pathB.execution_outcome.execution_status,
      reason: pathB.execution_outcome.reason,
      divergence_level: pathB.admissibility_result.divergence_level,
      divergence_score: pathB.admissibility_result.divergence_score
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
  console.log(`Replay check: ${summary.path_a.replay_status} (${summary.path_a.replay_reason})`);
}

main().catch((err) => {
  console.error("Governed Repository Mutation Proof failed.");
  console.error(err);
  process.exit(1);
});
