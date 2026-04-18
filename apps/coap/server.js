const coap = require('coap')
const http = require('http')

const DJANGO_HOST = process.env.DJANGO_HOST || 'managementtool'
const DJANGO_PORT = parseInt(process.env.DJANGO_PORT || '8000')
const VALID_DEVICE_TYPES = ['type1', 'type2']

const server = coap.createServer({ type: 'udp4' })

server.on('request', (req, res) => {
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
      'Content-Length': Buffer.byteLength(req.payload),
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

  httpReq.write(req.payload)
  httpReq.end()
})

server.listen(5683, () => {
  console.log(`CoAP bridge listening on UDP/5683 → http://${DJANGO_HOST}:${DJANGO_PORT}`)
})
