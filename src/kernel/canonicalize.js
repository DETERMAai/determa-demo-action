const crypto = require('crypto')
const { replayHash } = require('./replay_hash')

function sha(input) {
  return crypto
    .createHash('sha256')
    .update(JSON.stringify(input), 'utf8')
    .digest('hex')
}

function refusal(reason, rtc, capability, replayState) {
  return {
    admissibility: 'NON_CANONICAL',
    reason_code: reason,
    replay_hash: replayHash({
      constitution_version: 'v0',
      rtc,
      capability,
      replay_state: replayState,
      admissibility: 'NON_CANONICAL',
      reason_code: reason
    })
  }
}

function canonicalize(rtc, capability, replayState) {
  if (!capability) {
    return refusal('missing_capability', rtc, capability, replayState)
  }

  if (capability.rtc_hash !== sha(rtc)) {
    return refusal('lineage_mismatch', rtc, capability, replayState)
  }

  if (capability.lineage_head !== replayState.lineage_head) {
    return refusal('lineage_mismatch', rtc, capability, replayState)
  }

  if (capability.epoch !== rtc.epoch) {
    return refusal('epoch_violation', rtc, capability, replayState)
  }

  return {
    admissibility: 'CANONICAL',
    replay_hash: replayHash({
      constitution_version: 'v0',
      rtc,
      capability,
      replay_state: replayState,
      admissibility: 'CANONICAL',
      reason_code: null
    })
  }
}

module.exports = {
  canonicalize
}
