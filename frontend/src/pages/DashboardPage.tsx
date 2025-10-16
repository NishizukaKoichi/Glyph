import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Header } from '../components/layout/Header'
import { AssuranceScoreCard } from '../components/dashboard/AssuranceScoreCard'
import type { GlyphToken } from '../types/auth'
import './DashboardPage.css'

export function DashboardPage() {
  const navigate = useNavigate()
  const [token, setToken] = useState<GlyphToken | null>(null)

  useEffect(() => {
    // Get token from localStorage or session
    const storedToken = localStorage.getItem('glyph_token')
    if (storedToken) {
      try {
        setToken(JSON.parse(storedToken))
      } catch (e) {
        console.error('Failed to parse token:', e)
        navigate('/login')
      }
    } else {
      navigate('/login')
    }
  }, [navigate])

  const handleLogout = () => {
    localStorage.removeItem('glyph_token')
    navigate('/login')
  }

  if (!token) {
    return <div>Loading...</div>
  }

  return (
    <div className="dashboard-page">
      <Header 
        user={{ email: 'user@example.com' }}
        onLogout={handleLogout}
      />
      
      <main className="dashboard-main">
        <div className="dashboard-container">
          <div className="dashboard-header">
            <h1>ダッシュボード</h1>
            <p>あなたの本人性スコアと認証状況</p>
          </div>

          <div className="dashboard-grid">
            <div className="grid-col-full">
              <AssuranceScoreCard score={token.aegis_assurance} />
            </div>

            {token.extensions?.trust_signals && (
              <div className="grid-col-half">
                <div className="card">
                  <h3>Trust Signals</h3>
                  <div className="trust-signal-item">
                    <span className="label">Risk Band:</span>
                    <span className={`badge badge-${token.extensions.trust_signals.risk.band}`}>
                      {token.extensions.trust_signals.risk.band.toUpperCase()}
                    </span>
                  </div>
                  <div className="trust-signal-item">
                    <span className="label">Risk Score:</span>
                    <span className="value">{token.extensions.trust_signals.risk.score}</span>
                  </div>
                  <div className="trust-signal-item">
                    <span className="label">Last Updated:</span>
                    <span className="value">
                      {new Date(token.extensions.trust_signals.risk.updated_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
            )}

            <div className="grid-col-half">
              <div className="card">
                <h3>クイックアクション</h3>
                <div className="quick-actions">
                  <button 
                    className="action-btn"
                    onClick={() => navigate('/factors')}
                  >
                    認証ファクター管理
                  </button>
                  <button 
                    className="action-btn"
                    onClick={() => navigate('/settings')}
                  >
                    Trust Signals設定
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
