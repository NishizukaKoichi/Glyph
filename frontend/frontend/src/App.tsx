import { useState } from 'react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="App">
      <header className="App-header">
        <h1>Glyph</h1>
        <p className="subtitle">刻まれた印章が、本人性と信頼を運ぶ</p>

        <div className="card">
          <button onClick={() => setCount((count) => count + 1)}>
            count is {count}
          </button>
          <p>
            Phase 7: フロントエンド実装を開始しました
          </p>
        </div>
      </header>
    </div>
  )
}

export default App
