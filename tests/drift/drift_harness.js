const { canonicalize } = require('../../src/kernel/canonicalize')

const baseVector = {
  rtc: {
    rtc_id: 'rtc_002',
    mutation_type: 'merge',
    payload_hash: 'ccc333',
    epoch: 1
  },
  capability: null,
  replay_state: {
    lineage_head: 'genesis',
    finalized_hashes: []
  }
}

function replay() {
  return canonicalize(
    baseVector.rtc,
    baseVector.capability,
    baseVector.replay_state
  )
}

const baseline = replay()

for (let i = 0; i < 1000; i++) {
  const current = replay()

  if (current.replay_hash !== baseline.replay_hash) {
    console.error('DRIFT_DETECTED replay_hash divergence')
    process.exit(1)
  }

  if (current.admissibility !== baseline.admissibility) {
    console.error('DRIFT_DETECTED admissibility divergence')
    process.exit(1)
  }

  if (current.reason_code !== baseline.reason_code) {
    console.error('DRIFT_DETECTED refusal divergence')
    process.exit(1)
  }
}

console.log('ZERO_DRIFT')
