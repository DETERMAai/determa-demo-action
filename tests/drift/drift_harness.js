const { canonicalize } = require('../../src/kernel/canonicalize')

function buildVector(orderVariant = false) {
  if (!orderVariant) {
    return {
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
  }

  return {
    rtc: {
      epoch: 1,
      payload_hash: 'ccc333',
      mutation_type: 'merge',
      rtc_id: 'rtc_002'
    },
    capability: null,
    replay_state: {
      finalized_hashes: [],
      lineage_head: 'genesis'
    }
  }
}

function replay(vector) {
  return canonicalize(
    vector.rtc,
    vector.capability,
    vector.replay_state
  )
}

const baseline = replay(buildVector(false))

for (let i = 0; i < 1000; i++) {
  const current = replay(buildVector(false))

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

const reordered = replay(buildVector(true))

if (reordered.replay_hash !== baseline.replay_hash) {
  console.error('ORDERING_DRIFT_DETECTED')
  process.exit(1)
}

console.log('ZERO_DRIFT')
