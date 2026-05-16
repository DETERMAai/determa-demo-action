import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SANDBOX_DIR = path.join(__dirname, "sandbox");
const OUTPUT_DIR = path.join(__dirname, "output");
const LATEST_DIR = path.join(OUTPUT_DIR, "latest");

const TEMPLATE_TARGET_PATH = path.join(SANDBOX_DIR, "target_config_template.txt");
const DEFAULT_BASELINE_CONTENT = [
  "service=worker",
  "max_retries=3",
  "timeout_seconds=45",
  "feature_flag_runtime_guard=true"
].join("\n") + "\n";

const DEPENDENCY_SNAPSHOT = {
  "runtime-core": "2.4.1",
  "mutation-engine": "1.7.3",
  "queue-adapter": "0.9.8"
};

const BASE_RUNTIME_EPOCH = 2107;
const FRESHNESS_WINDOW_SECONDS = 600;

function isoNow() {
  return new Date().toISOString();
}

function toRunStamp(date) {
  const y = date.getUTCFullYear();
  const m = String(date.getUTCMonth() + 1).padStart(2, "0");
  const d = String(date.getUTCDate()).padStart(2, "0");
  const hh = String(date.getUTCHours()).padStart(2, "0");
  const mm = String(date.getUTCMinutes()).padStart(2, "0");
  const ss = String(date.getUTCSeconds()).padStart(2, "0");
  return `${y}${m}${d}_${hh}${mm}${ss}`;
}

function hashString(input) {
  return crypto.createHash("sha256").update(input, "utf8").digest("hex");
}

async function hashFile(filePath) {
  const content = await fs.readFile(filePath, "utf8");
  return hashString(content);
}

function clone(obj) {
  return JSON.parse(JSON.stringify(obj));
}

function issueGrant(scope, issuedAt, seed) {
  const grantId = `grant_${hashString(`${scope.target_file}_${seed}`).slice(0, 12)}`;
  return {
    grant_id: grantId,
    issued_at: issuedAt,
    freshness_window_seconds: FRESHNESS_WINDOW_SECONDS,
    scope,
    single_use: true,
    consumed: false
  };
}

function appendEvent(chain, type, payload, phase, prevIdRef) {
  const eventId = `evt_${String(chain.length + 1).padStart(4, "0")}_${hashString(`${type}_${phase}_${chain.length}`).slice(0, 8)}`;
  const event = {
    event_id: eventId,
    previous_event_id: prevIdRef.value,
    phase,
    timestamp: isoNow(),
    event_type: type,
    payload
  };
  chain.push(event);
  prevIdRef.value = eventId;
}

function evaluateAdmissibility({
  proposal,
  approvalSnapshot,
  grant,
  runtimeWitness,
  attemptIndex
}) {
  const approvalTime = new Date(approvalSnapshot.approval_timestamp).getTime();
  const witnessTime = new Date(runtimeWitness.runtime_timestamp).getTime();
  const elapsedSeconds = Math.floor((witnessTime - approvalTime) / 1000);

  const checks = {
    target_file_hash_continuity: runtimeWitness.target_file_hash === approvalSnapshot.target_file_hash,
    runtime_epoch_continuity: runtimeWitness.runtime_epoch === approvalSnapshot.runtime_epoch,
    grant_freshness: elapsedSeconds <= grant.freshness_window_seconds,
    single_use_grant_status: grant.single_use && grant.consumed === false,
    patch_scope_validity:
      proposal.target_file === grant.scope.target_file &&
      proposal.mutation_scope === grant.scope.mutation_scope,
    replay_status: attemptIndex > 1 || grant.consumed === true
  };

  const reasons = [];
  if (!checks.target_file_hash_continuity) reasons.push("target file hash mismatch");
  if (!checks.patch_scope_validity) reasons.push("patch scope mismatch");
  if (checks.replay_status) reasons.push("replay detected");
  if (!checks.runtime_epoch_continuity) reasons.push("runtime epoch drifted");
  if (!checks.grant_freshness) reasons.push("grant freshness expired");
  if (!checks.single_use_grant_status) reasons.push("single-use grant already consumed");

  let admissibility = "ADMISSIBLE";
  if (!checks.target_file_hash_continuity || !checks.patch_scope_validity || checks.replay_status) {
    admissibility = "DENIED";
  } else if (!checks.runtime_epoch_continuity || !checks.grant_freshness || !checks.single_use_grant_status) {
    admissibility = "REQUIRES_REVALIDATION";
  }

  return {
    admissibility,
    checks,
    reason: reasons.length ? reasons.join("; ") : "authority continuity preserved",
    elapsed_seconds_from_approval: elapsedSeconds
  };
}

async function applyPatchIfAllowed(targetPath, proposal) {
  const before = await fs.readFile(targetPath, "utf8");
  if (!before.includes(proposal.patch.from)) {
    return {
      applied: false,
      reason: "patch precondition not found in target content",
      before_hash: hashString(before),
      after_hash: hashString(before)
    };
  }

  const after = before.replace(proposal.patch.from, proposal.patch.to);
  await fs.writeFile(targetPath, after, "utf8");
  return {
    applied: true,
    reason: "patch applied under admissible runtime legitimacy",
    before_hash: hashString(before),
    after_hash: hashString(after)
  };
}

async function buildRuntimeWitness(targetPath, runtimeEpoch, dependencySnapshot, patchScope) {
  return {
    target_file_hash: await hashFile(targetPath),
    runtime_epoch: runtimeEpoch,
    dependency_snapshot: clone(dependencySnapshot),
    runtime_timestamp: isoNow(),
    patch_scope: patchScope
  };
}

async function runPath({
  pathId,
  runDir,
  proposal,
  approvalSnapshot,
  mutateBeforeEvaluation,
  baselineContent
}) {
  const pathDir = path.join(runDir, pathId);
  await fs.mkdir(pathDir, { recursive: true });
  const targetPath = path.join(pathDir, "target_config.txt");
  await fs.writeFile(targetPath, baselineContent, "utf8");

  const evidenceChain = [];
  const prevEvent = { value: null };
  const grant = issueGrant(
    {
      target_file: proposal.target_file,
      mutation_scope: proposal.mutation_scope
    },
    isoNow(),
    `${pathId}_${proposal.proposal_id}`
  );

  appendEvent(
    evidenceChain,
    "proposal_created",
    {
      proposal_id: proposal.proposal_id,
      target_file: proposal.target_file,
      patch: proposal.patch
    },
    "P1",
    prevEvent
  );

  appendEvent(
    evidenceChain,
    "approval_snapshot_captured",
    {
      approval_id: approvalSnapshot.approval_id,
      target_file_hash: approvalSnapshot.target_file_hash,
      runtime_epoch: approvalSnapshot.runtime_epoch,
      approval_timestamp: approvalSnapshot.approval_timestamp
    },
    "P2",
    prevEvent
  );

  appendEvent(
    evidenceChain,
    "authority_grant_issued",
    {
      grant_id: grant.grant_id,
      freshness_window_seconds: grant.freshness_window_seconds,
      single_use: grant.single_use,
      scope: grant.scope
    },
    "P3",
    prevEvent
  );

  if (mutateBeforeEvaluation) {
    const mutated = baselineContent + "runtime_override=true\n";
    await fs.writeFile(targetPath, mutated, "utf8");
  }

  const runtimeEpoch = mutateBeforeEvaluation ? BASE_RUNTIME_EPOCH + 1 : BASE_RUNTIME_EPOCH;
  const runtimeWitness = await buildRuntimeWitness(
    targetPath,
    runtimeEpoch,
    DEPENDENCY_SNAPSHOT,
    proposal.mutation_scope
  );

  appendEvent(
    evidenceChain,
    "runtime_witness_captured",
    {
      target_file_hash: runtimeWitness.target_file_hash,
      runtime_epoch: runtimeWitness.runtime_epoch,
      runtime_timestamp: runtimeWitness.runtime_timestamp
    },
    "P4",
    prevEvent
  );

  const admissibilityResult = evaluateAdmissibility({
    proposal,
    approvalSnapshot,
    grant,
    runtimeWitness,
    attemptIndex: 1
  });

  appendEvent(
    evidenceChain,
    "admissibility_evaluated",
    {
      admissibility: admissibilityResult.admissibility,
      reason: admissibilityResult.reason,
      checks: admissibilityResult.checks
    },
    "P5",
    prevEvent
  );

  const preAttemptHash = await hashFile(targetPath);
  let executionOutcome = null;

  if (admissibilityResult.admissibility === "ADMISSIBLE") {
    const patchResult = await applyPatchIfAllowed(targetPath, proposal);
    grant.consumed = patchResult.applied;
    executionOutcome = {
      execution_status: "EXECUTION_ALLOWED",
      reason: "authority continuity preserved",
      patch_applied: patchResult.applied,
      patch_result: patchResult
    };

    appendEvent(
      evidenceChain,
      "execution_allowed",
      {
        status: executionOutcome.execution_status,
        reason: executionOutcome.reason,
        before_hash: patchResult.before_hash,
        after_hash: patchResult.after_hash
      },
      "P6",
      prevEvent
    );
  } else {
    const postAttemptHash = await hashFile(targetPath);
    executionOutcome = {
      execution_status: "EXECUTION_DENIED",
      reason: "runtime state diverged after approval",
      patch_applied: false,
      admissibility: admissibilityResult.admissibility,
      pre_attempt_hash: preAttemptHash,
      post_attempt_hash: postAttemptHash,
      unchanged_by_attempt: preAttemptHash === postAttemptHash
    };

    appendEvent(
      evidenceChain,
      "execution_denied",
      {
        status: executionOutcome.execution_status,
        reason: executionOutcome.reason,
        admissibility: admissibilityResult.admissibility,
        pre_attempt_hash: preAttemptHash,
        post_attempt_hash: postAttemptHash,
        unchanged_by_attempt: executionOutcome.unchanged_by_attempt
      },
      "P6",
      prevEvent
    );
  }

  appendEvent(
    evidenceChain,
    "proof_finalized",
    {
      path_id: pathId,
      final_status: executionOutcome.execution_status,
      final_reason: executionOutcome.reason
    },
    "P7",
    prevEvent
  );

  const finalTargetHash = await hashFile(targetPath);

  const evidence = {
    proof_path: pathId,
    proposal: clone(proposal),
    approval_snapshot: clone(approvalSnapshot),
    authority_grant: clone(grant),
    runtime_witness: runtimeWitness,
    admissibility_result: admissibilityResult,
    execution_outcome: executionOutcome,
    final_target_hash: finalTargetHash,
    evidence_chain: evidenceChain
  };

  await fs.writeFile(path.join(pathDir, "evidence.json"), JSON.stringify(evidence, null, 2), "utf8");
  return evidence;
}

async function writeReport(runDir, summary) {
  const md = [
    "# Controlled Real Mutation Proof Report",
    "",
    `Run ID: ${summary.run_id}`,
    "",
    "## Proof Claim",
    "",
    "Same patch. Same approval structure. Different runtime state. Different execution outcome.",
    "",
    "## Path A (Admissible)",
    "",
    `- status: ${summary.path_a.execution_status}`,
    `- reason: ${summary.path_a.reason}`,
    `- target hash changed by patch: ${summary.path_a.target_hash_changed}`,
    "",
    "## Path B (Denied)",
    "",
    `- status: ${summary.path_b.execution_status}`,
    `- reason: ${summary.path_b.reason}`,
    `- patch applied: ${summary.path_b.patch_applied}`,
    `- target unchanged by denied attempt: ${summary.path_b.target_unchanged_by_attempt}`,
    "",
    "## Runtime Difference",
    "",
    `- Path A runtime hash == approval hash: ${summary.path_a.hash_continuity}`,
    `- Path B runtime hash == approval hash: ${summary.path_b.hash_continuity}`,
    "",
    "## Evidence Files",
    "",
    "- path_a/evidence.json",
    "- path_b/evidence.json",
    "- proof_summary.json",
    ""
  ].join("\n");

  await fs.writeFile(path.join(runDir, "CONTROLLED_REAL_MUTATION_PROOF_REPORT.md"), md, "utf8");
}

async function mirrorLatest(runDir) {
  await fs.rm(LATEST_DIR, { recursive: true, force: true });
  await fs.mkdir(LATEST_DIR, { recursive: true });

  const entries = await fs.readdir(runDir, { withFileTypes: true });
  for (const entry of entries) {
    const src = path.join(runDir, entry.name);
    const dst = path.join(LATEST_DIR, entry.name);
    if (entry.isDirectory()) {
      await fs.cp(src, dst, { recursive: true });
    } else {
      await fs.copyFile(src, dst);
    }
  }
}

async function main() {
  const startedAt = new Date();
  const runId = `proof_${toRunStamp(startedAt)}`;
  const runDir = path.join(OUTPUT_DIR, runId);

  await fs.mkdir(SANDBOX_DIR, { recursive: true });
  await fs.mkdir(runDir, { recursive: true });

  let baselineContent = DEFAULT_BASELINE_CONTENT;
  try {
    baselineContent = await fs.readFile(TEMPLATE_TARGET_PATH, "utf8");
    if (!baselineContent.endsWith("\n")) baselineContent += "\n";
  } catch {
    await fs.writeFile(TEMPLATE_TARGET_PATH, DEFAULT_BASELINE_CONTENT, "utf8");
    baselineContent = DEFAULT_BASELINE_CONTENT;
  }

  const approvalModelPath = path.join(SANDBOX_DIR, "approval_model_target_config.txt");
  await fs.writeFile(approvalModelPath, baselineContent, "utf8");

  const proposal = {
    proposal_id: `proposal_${hashString("controlled_real_mutation_patch").slice(0, 12)}`,
    target_file: "sandbox/target_config.txt",
    mutation_scope: "runtime.config.worker",
    patch: {
      operation: "line_replace",
      from: "max_retries=3",
      to: "max_retries=5"
    }
  };

  const approvalSnapshot = {
    approval_id: `approval_${hashString(`${proposal.proposal_id}_${BASE_RUNTIME_EPOCH}`).slice(0, 12)}`,
    target_file_hash: await hashFile(approvalModelPath),
    runtime_epoch: BASE_RUNTIME_EPOCH,
    dependency_snapshot: clone(DEPENDENCY_SNAPSHOT),
    approval_timestamp: isoNow()
  };

  const pathA = await runPath({
    pathId: "path_a_admissible",
    runDir,
    proposal,
    approvalSnapshot,
    mutateBeforeEvaluation: false,
    baselineContent
  });

  const pathB = await runPath({
    pathId: "path_b_denied",
    runDir,
    proposal,
    approvalSnapshot,
    mutateBeforeEvaluation: true,
    baselineContent
  });

  const summary = {
    run_id: runId,
    started_at: startedAt.toISOString(),
    proof_claim:
      "same patch + same approval structure + different runtime state => different execution outcome",
    path_a: {
      execution_status: pathA.execution_outcome.execution_status,
      reason: pathA.execution_outcome.reason,
      patch_applied: pathA.execution_outcome.patch_applied,
      target_hash_changed:
        pathA.execution_outcome.patch_result.before_hash !== pathA.execution_outcome.patch_result.after_hash,
      hash_continuity: pathA.admissibility_result.checks.target_file_hash_continuity
    },
    path_b: {
      execution_status: pathB.execution_outcome.execution_status,
      reason: pathB.execution_outcome.reason,
      patch_applied: pathB.execution_outcome.patch_applied,
      target_unchanged_by_attempt: pathB.execution_outcome.unchanged_by_attempt,
      hash_continuity: pathB.admissibility_result.checks.target_file_hash_continuity
    },
    outputs: {
      run_directory: runDir,
      latest_directory: LATEST_DIR
    }
  };

  await fs.writeFile(path.join(runDir, "proof_summary.json"), JSON.stringify(summary, null, 2), "utf8");
  await writeReport(runDir, summary);
  await mirrorLatest(runDir);

  console.log("Controlled Real Mutation Proof completed.");
  console.log(`Run directory: ${runDir}`);
  console.log(`Latest output: ${LATEST_DIR}`);
  console.log(`Path A: ${summary.path_a.execution_status} (${summary.path_a.reason})`);
  console.log(`Path B: ${summary.path_b.execution_status} (${summary.path_b.reason})`);
}

main().catch((error) => {
  console.error("Controlled Real Mutation Proof failed.");
  console.error(error);
  process.exit(1);
});
