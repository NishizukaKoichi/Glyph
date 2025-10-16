import type { AssuranceScore } from '../../types/auth'
import './AssuranceScoreCard.css'

interface AssuranceScoreCardProps {
  score: AssuranceScore
}

export function AssuranceScoreCard({ score }: AssuranceScoreCardProps) {
  const getLevelColor = (level: string) => {
    switch (level) {
      case 'gamma': return '#10b981'
      case 'beta': return '#3b82f6'
      case 'alpha': return '#f59e0b'
      default: return '#6b7280'
    }
  }

  const getLevelName = (level: string) => {
    switch (level) {
      case 'gamma': return 'γ (Gamma) - 最高'
      case 'beta': return 'β (Beta) - 強化'
      case 'alpha': return 'α (Alpha) - 基本'
      default: return '未確認'
    }
  }

  const getScoreDescription = (level: string) => {
    switch (level) {
      case 'gamma':
        return 'WebAuthn + 複数ファクターによる最高レベルの本人性確認'
      case 'beta':
        return '複数の強力な認証ファクターによる信頼性の高い本人性確認'
      case 'alpha':
        return '基本的な認証による本人性確認'
      default:
        return '認証情報が不足しています'
    }
  }

  const percentage = Math.min((score.score / 100) * 100, 100)
  const circumference = 2 * Math.PI * 90
  const offset = circumference * (1 - percentage / 100)

  return (
    <div className="assurance-score-card">
      <h2>Assurance Score</h2>
      
      <div className="score-display">
        <div className="score-circle">
          <svg width="200" height="200" viewBox="0 0 200 200">
            <circle
              cx="100"
              cy="100"
              r="90"
              fill="none"
              stroke="#e5e7eb"
              strokeWidth="12"
            />
            <circle
              cx="100"
              cy="100"
              r="90"
              fill="none"
              stroke={getLevelColor(score.level)}
              strokeWidth="12"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
              transform="rotate(-90 100 100)"
              style={{ transition: 'stroke-dashoffset 1s ease' }}
            />
          </svg>
          <div className="score-value">
            <span className="score-number">{score.score}</span>
            <span className="score-max">/100</span>
          </div>
        </div>

        <div className="score-info">
          <div className="level-badge" style={{ background: getLevelColor(score.level) }}>
            {getLevelName(score.level)}
          </div>
          <p className="level-description">
            {getScoreDescription(score.level)}
          </p>
        </div>
      </div>

      <div className="score-details">
        <div className="detail-item">
          <span className="detail-label">認証ファクター</span>
          <div className="factors-list">
            {score.factors.map((factor, i) => (
              <span key={i} className="factor-badge">
                {factor}
              </span>
            ))}
          </div>
        </div>
        
        <div className="detail-item">
          <span className="detail-label">鮮度</span>
          <span className="detail-value">{score.freshness_days} 日</span>
        </div>
      </div>
    </div>
  )
}
