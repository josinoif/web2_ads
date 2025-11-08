import express from 'express'

export function createApp () {
  const app = express()
  app.use(express.json())

  app.get('/health', (req, res) => {
    res.json({ status: 'ok' })
  })

  app.get('/sum', (req, res) => {
    const a = Number(req.query.a ?? 0)
    const b = Number(req.query.b ?? 0)
    res.json({ result: a + b })
  })

  app.post('/echo', (req, res) => {
    res.json({ youSent: req.body })
  })

  return app
}
