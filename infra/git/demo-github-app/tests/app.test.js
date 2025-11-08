import { test, before, after } from 'node:test'
import assert from 'node:assert'
import http from 'node:http'
import request from 'supertest'
import { createApp } from '../src/app.js'

let server

before(() => {
  const app = createApp()
  server = http.createServer(app)
  server.listen(0)
})

after(() => {
  server.close()
})

test('GET /health returns ok', async () => {
  const res = await request(server).get('/health')
  assert.strictEqual(res.status, 200)
  assert.deepStrictEqual(res.body, { status: 'ok' })
})

test('GET /sum adds numbers', async () => {
  const res = await request(server).get('/sum').query({ a: 2, b: 3 })
  assert.strictEqual(res.status, 200)
  assert.deepStrictEqual(res.body, { result: 5 })
})

test('POST /echo echoes body', async () => {
  const res = await request(server).post('/echo').send({ x: 1 })
  assert.strictEqual(res.status, 200)
  assert.deepStrictEqual(res.body, { youSent: { x: 1 } })
})
