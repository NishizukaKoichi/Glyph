import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Header } from '../components/layout/Header'
import { TrustSignalSettings } from '../components/settings/TrustSignalSettings'
import type { GlyphToken } from '../types/auth'
import './SettingsPage.css'

export function SettingsPage() {
  const navigate = useNavigate()
  const [token, setToken] = useState<GlyphToken | null>(null)

  useEffect(() => {
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
    <div className="settings-page">
      <Header
        user={{ email: 'user@example.com' }}
        onLogout={handleLogout}
      />

      <main className="settings-main">
        <div className="settings-container">
          <div className="settings-header">
            <h1>設定</h1>
            <p>Trust SignalsとGlyphの動作設定</p>
          </div>

          <TrustSignalSettings trustSignals={token.extensions?.trust_signals} />
        </div>
      </main>
    </div>
  )
}
