const fs = require('fs')
const path = require('path')
const { canonicalize } = require('../../src/kernel/canonicalize')

const vectorDir = path.resolve(__dirname, '../../constitution/vectors')
const files = fs.readdirSync(vectorDir).filter(f => f.endsWith('.json'))

let failed = false

for (const file of files) {
  const vector = JSON.parse(
    fs.readFileSync(path.join(vectorDir, file), 'utf8')
  )

  const result = canonicalize(
    vector.rtc,
    vector.capability,
    vector.replay_state
  )

  if (result.admissibility !== vector.expected.admissibility) {
    console.error(`VECTOR_FAIL ${file} admissibility mismatch`)
    failed = true
    continue
  }

  if (
    vector.expected.reason_code &&
    result.reason_code !== vector.expected.reason_code
  ) {
    console.error(`VECTOR_FAIL ${file} reason mismatch`)
    failed = true
    continue
  }

  console.log(`VECTOR_OK ${file}`)
}

if (failed) {
  process.exit(1)
}
