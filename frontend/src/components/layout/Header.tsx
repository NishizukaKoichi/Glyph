import { Link } from 'react-router-dom'
import './Header.css'

interface HeaderProps {
  user?: {
    email: string
  }
  onLogout?: () => void
}

export function Header({ user, onLogout }: HeaderProps) {
  return (
    <header className="app-header">
      <div className="header-content">
        <Link to="/" className="logo">
          <h1>Glyph</h1>
        </Link>
        
        {user && (
          <nav className="header-nav">
            <Link to="/dashboard" className="nav-link">
              ダッシュボード
            </Link>
            <Link to="/factors" className="nav-link">
              認証ファクター
            </Link>
            <Link to="/settings" className="nav-link">
              設定
            </Link>
            <div className="user-menu">
              <span className="user-email">{user.email}</span>
              {onLogout && (
                <button onClick={onLogout} className="logout-btn">
                  ログアウト
                </button>
              )}
            </div>
          </nav>
        )}
      </div>
    </header>
  )
}
