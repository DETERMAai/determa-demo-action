function normalize(value) {
  if (value === undefined) {
    throw new Error('SERIALIZATION_VIOLATION')
  }

  if (value === null) {
    return null
  }

  if (typeof value === 'number') {
    if (!Number.isInteger(value)) {
      throw new Error('SERIALIZATION_VIOLATION')
    }
    return value
  }

  if (typeof value === 'string' || typeof value === 'boolean') {
    return value
  }

  if (Array.isArray(value)) {
    return value.map(normalize)
  }

  if (typeof value === 'object') {
    const out = {}
    for (const key of Object.keys(value).sort()) {
      out[key] = normalize(value[key])
    }
    return out
  }

  throw new Error('SERIALIZATION_VIOLATION')
}

function stableJson(value) {
  return JSON.stringify(normalize(value))
}

module.exports = {
  stableJson
}
