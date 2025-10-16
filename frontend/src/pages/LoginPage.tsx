import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { startRegistration, startAuthentication } from '@simplewebauthn/browser'
import { webauthn, oauth } from '../services/api'
import type { GlyphToken } from '../types/auth'
import './LoginPage.css'

export function LoginPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [token, setToken] = useState<GlyphToken | null>(null)

  const handleSuccess = (result: GlyphToken) => {
    setToken(result)
    localStorage.setItem('glyph_token', JSON.stringify(result))
    // Redirect to dashboard after short delay
    setTimeout(() => {
      navigate('/dashboard')
    }, 1500)
  }

  const handleWebAuthnRegister = async () => {
    if (!email) {
      setError('メールアドレスを入力してください')
      return
    }

    setLoading(true)
    setError('')

    try {
      // Start registration
      const options = await webauthn.registerStart(email)
      
      // Convert options to correct format for browser API
      const publicKeyOptions = {
        challenge: Uint8Array.from(atob(options.challenge), c => c.charCodeAt(0)),
        rp: options.rp,
        user: {
          ...options.user,
          id: Uint8Array.from(atob(options.user.id), c => c.charCodeAt(0)),
        },
        pubKeyCredParams: options.pubKeyCredParams,
        timeout: options.timeout,
        attestation: options.attestation as AttestationConveyancePreference,
        authenticatorSelection: options.authenticatorSelection as AuthenticatorSelectionCriteria,
      }

      // Get credential from authenticator
      const credential = await startRegistration(publicKeyOptions as any)

      // Finish registration
      const result = await webauthn.registerFinish(email, credential)
      handleSuccess(result)
      
    } catch (err: any) {
      setError(err.message || '登録に失敗しました')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleWebAuthnLogin = async () => {
    if (!email) {
      setError('メールアドレスを入力してください')
      return
    }

    setLoading(true)
    setError('')

    try {
      // Start authentication
      const options = await webauthn.authenticateStart(email)

      // Convert options to correct format
      const publicKeyOptions = {
        challenge: Uint8Array.from(atob(options.challenge), c => c.charCodeAt(0)),
        rpId: options.rpId,
        timeout: options.timeout,
        userVerification: options.userVerification as UserVerificationRequirement,
        allowCredentials: options.allowCredentials.map(cred => ({
          ...cred,
          id: Uint8Array.from(atob(cred.id), c => c.charCodeAt(0)),
        })),
      }

      // Get assertion from authenticator
      const credential = await startAuthentication(publicKeyOptions as any)

      // Finish authentication
      const result = await webauthn.authenticateFinish(email, credential)
      handleSuccess(result)

    } catch (err: any) {
      setError(err.message || '認証に失敗しました')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleOAuthLogin = (provider: 'google' | 'microsoft' | 'github' | 'twitter') => {
    oauth.login(provider)
  }

  if (token) {
    return (
      <div className="login-page">
        <div className="login-card success">
          <h2>✓ 認証成功</h2>
          <div className="token-info">
            <h3>Assurance Score</h3>
            <div className="assurance-score">
              <span className="score">{token.aegis_assurance.score}</span>
              <span className="level">{token.aegis_assurance.level}</span>
            </div>
            <div className="factors">
              <strong>認証ファクター:</strong>
              {token.aegis_assurance.factors.map((factor, i) => (
                <span key={i} className="factor">{factor}</span>
              ))}
            </div>
            <div className="freshness">
              Freshness: {token.aegis_assurance.freshness_days} days
            </div>
          </div>
          <button onClick={() => {
            setToken(null)
            setEmail('')
          }}>
            再ログイン
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="glyph-logo">
          <h1>Glyph</h1>
          <p className="tagline">刻まれた印章が、本人性と信頼を運ぶ</p>
        </div>

        {error && <div className="error">{error}</div>}

        <div className="webauthn-section">
          <h2>WebAuthn / Passkey</h2>
          <input
            type="email"
            placeholder="メールアドレス"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={loading}
          />
          <div className="button-group">
            <button
              onClick={handleWebAuthnRegister}
              disabled={loading}
              className="primary"
            >
              {loading ? '処理中...' : '新規登録'}
            </button>
            <button
              onClick={handleWebAuthnLogin}
              disabled={loading}
              className="secondary"
            >
              {loading ? '処理中...' : 'ログイン'}
            </button>
          </div>
        </div>

        <div className="divider">または</div>

        <div className="oauth-section">
          <h2>ソーシャルログイン</h2>
          <div className="oauth-buttons">
            <button
              onClick={() => handleOAuthLogin('google')}
              className="oauth-button google"
              disabled={loading}
            >
              <span>Google</span>
            </button>
            <button
              onClick={() => handleOAuthLogin('microsoft')}
              className="oauth-button microsoft"
              disabled={loading}
            >
              <span>Microsoft</span>
            </button>
            <button
              onClick={() => handleOAuthLogin('github')}
              className="oauth-button github"
              disabled={loading}
            >
              <span>GitHub</span>
            </button>
            <button
              onClick={() => handleOAuthLogin('twitter')}
              className="oauth-button twitter"
              disabled={loading}
            >
              <span>X (Twitter)</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
