#!/usr/bin/env node

const fs = require('fs')
const path = require('path')
const { canonicalize } = require('../src/kernel/canonicalize')
const { replayHash } = require('../src/kernel/replay_hash')

function usage() {
  console.error('Usage: determa replay <vector.json>')
  process.exit(2)
}

function loadJson(filePath) {
  const absolute = path.resolve(process.cwd(), filePath)
  return JSON.parse(fs.readFileSync(absolute, 'utf8'))
}

function runReplay(vectorPath) {
  const vector = loadJson(vectorPath)
  const result = canonicalize(vector.rtc, vector.capability, vector.replay_state)
  const rtcHash = replayHash({ constitution_version: 'v0', rtc: vector.rtc })

  const artifact = {
    constitution_version: 'v0',
    rtc_hash: rtcHash,
    admissibility: result.admissibility,
    reason_code: result.reason_code || null,
    replay_hash: result.replay_hash
  }

  if (result.admissibility === 'CANONICAL') {
    console.log('CANONICAL')
  } else {
    console.log('NON_CANONICAL')
    console.log(`reason=${result.reason_code}`)
  }

  console.log(`replay_hash=${result.replay_hash}`)
  console.log(JSON.stringify(artifact, null, 2))
}

const [, , command, vectorPath] = process.argv

if (command !== 'replay' || !vectorPath) {
  usage()
}

try {
  runReplay(vectorPath)
} catch (error) {
  console.error(`CONSTITUTIONAL_RUNTIME_ERROR ${error.message}`)
  process.exit(1)
}
