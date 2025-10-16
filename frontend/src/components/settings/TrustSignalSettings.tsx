import { useState } from 'react'
import type { TrustSignal } from '../../types/auth'
import './TrustSignalSettings.css'

interface TrustSignalSettingsProps {
  trustSignals?: TrustSignal
}

interface SignalType {
  id: string
  name: string
  description: string
  provider: string
  enabled: boolean
  icon: string
}

export function TrustSignalSettings({ trustSignals }: TrustSignalSettingsProps) {
  const [signals, setSignals] = useState<SignalType[]>([
    {
      id: 'device_reputation',
      name: 'デバイス評価',
      description: 'デバイスの信頼性スコアを評価し、不正デバイスを検出',
      provider: 'Glyph Internal',
      enabled: true,
      icon: '📱'
    },
    {
      id: 'ip_reputation',
      name: 'IPアドレス評価',
      description: 'IPレピュテーションデータベースを使用した不正アクセス検出',
      provider: 'MaxMind',
      enabled: true,
      icon: '🌐'
    },
    {
      id: 'behavioral_analysis',
      name: '行動分析',
      description: 'ユーザーの通常の行動パターンと比較し、異常を検出',
      provider: 'Glyph ML',
      enabled: false,
      icon: '🧠'
    },
    {
      id: 'velocity_check',
      name: 'ベロシティチェック',
      description: '短時間での複数ログイン試行など、異常な活動を検出',
      provider: 'Glyph Internal',
      enabled: true,
      icon: '⚡'
    }
  ])

  const [privacySettings, setPrivacySettings] = useState({
    share_trust_signals: true,
    anonymize_data: true,
    retention_days: 90
  })

  const toggleSignal = (id: string) => {
    setSignals(signals.map(s =>
      s.id === id ? { ...s, enabled: !s.enabled } : s
    ))
  }

  return (
    <div className="trust-signal-settings">
      <div className="settings-section">
        <h2>Trust Signals 有効化</h2>
        <p className="section-description">
          各Trust Signalの有効/無効を設定できます。有効化されたSignalのみがAssurance Score計算に使用されます。
        </p>

        <div className="signal-list">
          {signals.map(signal => (
            <div key={signal.id} className="signal-item">
              <div className="signal-icon">{signal.icon}</div>
              <div className="signal-info">
                <h3>{signal.name}</h3>
                <p className="signal-description">{signal.description}</p>
                <span className="signal-provider">Provider: {signal.provider}</span>
              </div>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={signal.enabled}
                  onChange={() => toggleSignal(signal.id)}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
          ))}
        </div>
      </div>

      <div className="settings-section">
        <h2>プライバシー設定</h2>
        <p className="section-description">
          Trust Signalsのデータ利用と保存に関する設定
        </p>

        <div className="privacy-controls">
          <div className="privacy-item">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={privacySettings.share_trust_signals}
                onChange={(e) => setPrivacySettings({ ...privacySettings, share_trust_signals: e.target.checked })}
              />
              <span>Trust Signalsをトークンに含める</span>
            </label>
            <p className="privacy-description">
              認証時に発行されるトークンにTrust Signalsを含めます。無効にするとAssurance Scoreのみが含まれます。
            </p>
          </div>

          <div className="privacy-item">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={privacySettings.anonymize_data}
                onChange={(e) => setPrivacySettings({ ...privacySettings, anonymize_data: e.target.checked })}
              />
              <span>データを匿名化する</span>
            </label>
            <p className="privacy-description">
              収集されたTrust Signalsデータを匿名化して保存します。
            </p>
          </div>

          <div className="privacy-item">
            <label className="retention-label">
              データ保持期間: <strong>{privacySettings.retention_days}日</strong>
            </label>
            <input
              type="range"
              min="30"
              max="365"
              value={privacySettings.retention_days}
              onChange={(e) => setPrivacySettings({ ...privacySettings, retention_days: parseInt(e.target.value) })}
              className="retention-slider"
            />
            <p className="privacy-description">
              Trust Signalsデータを保持する期間を設定します（30〜365日）。
            </p>
          </div>
        </div>
      </div>

      {trustSignals && (
        <div className="settings-section current-status">
          <h2>現在のTrust Signals状態</h2>
          <div className="status-grid">
            <div className="status-item">
              <span className="status-label">Risk Band</span>
              <span className={'status-value badge-' + trustSignals.risk.band}>
                {trustSignals.risk.band.toUpperCase()}
              </span>
            </div>
            <div className="status-item">
              <span className="status-label">Risk Score</span>
              <span className="status-value">{trustSignals.risk.score}</span>
            </div>
            <div className="status-item">
              <span className="status-label">最終更新</span>
              <span className="status-value">
                {new Date(trustSignals.risk.updated_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        </div>
      )}

      <div className="settings-actions">
        <button className="btn-save">
          設定を保存
        </button>
        <button className="btn-reset">
          デフォルトに戻す
        </button>
      </div>
    </div>
  )
}
