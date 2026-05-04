const coap = require('coap')
const http = require('http')

const DJANGO_HOST = process.env.DJANGO_HOST || 'managementtool'
const DJANGO_PORT = parseInt(process.env.DJANGO_PORT || '8000')
const VALID_DEVICE_TYPES = ['type1', 'type2']

const server = coap.createServer({ type: 'udp4' })

function getPacketType(packet) {
  if (!packet) {
    return null
  }
  if (packet.ack) {
    return 'ACK'
  }
  if (packet.reset) {
    return 'RST'
  }
  if (packet.confirmable) {
    return 'CON'
  }
  return 'NON'
}

function postDiagnostic(message) {
  const body = JSON.stringify(message)
  const req = http.request(
    {
      hostname: DJANGO_HOST,
      port: DJANGO_PORT,
      path: '/api/internal/last-coap/',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body),
      },
    },
    (res) => {
      res.resume()
    },
  )

  req.on('error', (err) => {
    console.error('CoAP diagnostic forward error:', err.message)
  })

  req.setTimeout(2000, () => {
    req.destroy(new Error('CoAP diagnostic forward timeout'))
  })

  req.write(body)
  req.end()
}

server.on('request', (req, res) => {
  const payload = req.payload || Buffer.alloc(0)
  const packet = req._packet || {}
  const token = packet.token || Buffer.alloc(0)

  postDiagnostic({
    received_at: new Date().toISOString(),
    url: req.url,
    method: req.method,
    coap_type: getPacketType(packet),
    confirmable: packet.confirmable === true,
    ack: packet.ack === true,
    reset: packet.reset === true,
    message_id: packet.messageId ?? null,
    token_hex: token.toString('hex'),
    payload_hex: payload.toString('hex'),
    payload_length: payload.length,
    remote_address: req.rsinfo?.address || null,
    remote_port: req.rsinfo?.port || null,
    headers: req.headers || {},
  })

  const deviceType = req.url.split('/').filter(Boolean).pop()

  if (!VALID_DEVICE_TYPES.includes(deviceType)) {
    console.warn(`Unknown device type in path: ${req.url}`)
    res.code = '4.04'
    return res.end()
  }

  const options = {
    hostname: DJANGO_HOST,
    port: DJANGO_PORT,
    path: `/api/coap/${deviceType}/`,
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(payload),
    },
  }

  const httpReq = http.request(options, (httpRes) => {
    res.code = httpRes.statusCode < 300 ? '2.04' : '5.00'
    res.end()
  })

  httpReq.on('error', (err) => {
    console.error('HTTP forward error:', err.message)
    res.code = '5.00'
    res.end()
  })

  httpReq.write(payload)
  httpReq.end()
})

server.listen(5683, () => {
  console.log(`CoAP bridge listening on UDP/5683 → http://${DJANGO_HOST}:${DJANGO_PORT}`)
})
