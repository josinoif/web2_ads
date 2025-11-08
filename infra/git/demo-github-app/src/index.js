import { createApp } from './app.js'

const port = process.env.PORT || 3000
const app = createApp()

app.listen(port, () => {
  // eslint-disable-next-line no-console
  console.log(`Server running on http://localhost:${port}`)
})
