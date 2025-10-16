import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Header } from '../components/layout/Header'
import { FactorList } from '../components/factors/FactorList'
import type { GlyphToken } from '../types/auth'
import './FactorsPage.css'

export function FactorsPage() {
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
    <div className="factors-page">
      <Header 
        user={{ email: 'user@example.com' }}
        onLogout={handleLogout}
      />
      
      <main className="factors-main">
        <div className="factors-container">
          <div className="factors-header">
            <h1>認証ファクター管理</h1>
            <p>登録されている認証方法の管理と追加</p>
          </div>

          <FactorList factors={token.aegis_assurance.factors} />
        </div>
      </main>
    </div>
  )
}
