const crypto = require('crypto')
const { stableJson } = require('./stable_json')

function replayHash(payload) {
  return crypto
    .createHash('sha256')
    .update(stableJson(payload), 'utf8')
    .digest('hex')
}

module.exports = {
  replayHash
}
