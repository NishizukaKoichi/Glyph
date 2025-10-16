import { useState } from 'react'
import './FactorList.css'

interface FactorListProps {
  factors: string[]
}

interface FactorDetail {
  type: string
  icon: string
  description: string
  weight: number
  color: string
}

const FACTOR_DETAILS: Record<string, FactorDetail> = {
  'webauthn': {
    type: 'WebAuthn / Passkey',
    icon: '🔐',
    description: 'FIDO2準拠のハードウェア認証器またはデバイス内蔵認証（Touch ID / Face ID / Windows Hello）',
    weight: 35,
    color: '#10b981'
  },
  'google': {
    type: 'Google OAuth',
    icon: '🔵',
    description: 'Googleアカウントでのソーシャルログイン',
    weight: 25,
    color: '#4285f4'
  },
  'microsoft': {
    type: 'Microsoft OAuth',
    icon: '🟦',
    description: 'Microsoftアカウントでのソーシャルログイン',
    weight: 25,
    color: '#00a4ef'
  },
  'github': {
    type: 'GitHub OAuth',
    icon: '⚫',
    description: 'GitHubアカウントでのソーシャルログイン',
    weight: 15,
    color: '#24292e'
  },
  'twitter': {
    type: 'X (Twitter) OAuth',
    icon: '⚪',
    description: 'X（旧Twitter）アカウントでのソーシャルログイン',
    weight: 15,
    color: '#1da1f2'
  }
}

export function FactorList({ factors }: FactorListProps) {
  const [expandedFactor, setExpandedFactor] = useState<string | null>(null)

  const toggleFactor = (factor: string) => {
    setExpandedFactor(expandedFactor === factor ? null : factor)
  }

  return (
    <div className="factor-list">
      <div className="factor-grid">
        {factors.map((factor, index) => {
          const detail = FACTOR_DETAILS[factor] || {
            type: factor,
            icon: '🔑',
            description: '不明な認証ファクター',
            weight: 0,
            color: '#6b7280'
          }
          const isExpanded = expandedFactor === factor

          return (
            <div
              key={index}
              className={'factor-card' + (isExpanded ? ' expanded' : '')}
              onClick={() => toggleFactor(factor)}
            >
              <div className="factor-header">
                <div className="factor-icon" style={{ background: detail.color }}>
                  {detail.icon}
                </div>
                <div className="factor-info">
                  <h3>{detail.type}</h3>
                  <div className="factor-weight">
                    スコア寄与: <strong>{detail.weight}点</strong>
                  </div>
                </div>
                <div className="factor-status">
                  <span className="status-badge active">有効</span>
                </div>
              </div>

              {isExpanded && (
                <div className="factor-details">
                  <p className="factor-description">{detail.description}</p>
                  <div className="factor-actions">
                    <button className="btn-secondary">
                      削除
                    </button>
                    <button className="btn-primary">
                      設定
                    </button>
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>

      <div className="add-factor-section">
        <h2>新しいファクターを追加</h2>
        <div className="add-factor-grid">
          {Object.entries(FACTOR_DETAILS)
            .filter(([key]) => !factors.includes(key))
            .map(([key, detail]) => (
              <button
                key={key}
                className="add-factor-btn"
                onClick={() => alert(detail.type + ' の追加は未実装です')}
              >
                <span className="add-factor-icon" style={{ background: detail.color }}>
                  {detail.icon}
                </span>
                <span className="add-factor-name">{detail.type}</span>
                <span className="add-factor-weight">+{detail.weight}点</span>
              </button>
            ))}
        </div>
      </div>
    </div>
  )
}
