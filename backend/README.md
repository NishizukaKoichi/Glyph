# Glyph Backend

Glyph認証ブローカーのバックエンドAPI実装。

## 技術スタック

- **Framework**: FastAPI 0.109+
- **Database**: SQLAlchemy 2.0 (async) + SQLite/PostgreSQL
- **Authentication**:
  - OAuth 2.0 (Google, Microsoft, GitHub, X/Twitter) via Authlib
  - WebAuthn/Passkey via py_webauthn
- **JWT**: python-jose
- **Migrations**: Alembic
- **Testing**: pytest + pytest-asyncio

## クイックスタート

### 1. 依存関係のインストール

```bash
# uvがインストールされていない場合
curl -LsSf https://astral.sh/uv/install.sh | sh

# 依存関係をインストール
uv pip install -e .
```

### 2. データベースマイグレーション

```bash
# マイグレーション実行（初回のみ）
uv run alembic upgrade head
```

### 3. アプリケーション起動

```bash
# 開発サーバー起動
uv run uvicorn app.main:app --reload
```

アプリケーションは `http://localhost:8000` で起動します。

### 4. API ドキュメント

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **OIDC Discovery**: http://localhost:8000/.well-known/openid-configuration

## 主要エンドポイント

### 基本

- `GET /` - ルートエンドポイント
- `GET /health` - ヘルスチェック
- `GET /.well-known/openid-configuration` - OIDC Discovery

### OAuth 認証

- `GET /auth/login/{provider}` - OAuth ログイン開始
  - Providers: `google`, `microsoft`, `github`, `twitter`
- `GET /auth/callback/{provider}` - OAuth コールバック

### WebAuthn 認証

- `POST /auth/webauthn/register/start` - WebAuthn 登録開始
- `POST /auth/webauthn/register/finish` - WebAuthn 登録完了
- `POST /auth/webauthn/authenticate/start` - WebAuthn 認証開始
- `POST /auth/webauthn/authenticate/finish` - WebAuthn 認証完了

## 環境変数

`.env` ファイルを作成して設定：

```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./glyph.db
# 本番環境ではPostgreSQLを使用
# DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/glyph

# JWT
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# OAuth Providers
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
X_CLIENT_ID=your-x-client-id
X_CLIENT_SECRET=your-x-client-secret

# WebAuthn
WEBAUTHN_RP_ID=localhost
WEBAUTHN_RP_NAME=Glyph
WEBAUTHN_ORIGIN=http://localhost:8000

# CORS
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

## テスト

```bash
# 全テスト実行
uv run pytest tests/ -v

# カバレッジ付き
uv run pytest tests/ --cov=app --cov-report=html

# 特定のテストファイル
uv run pytest tests/test_assurance.py -v
```

## データベースマイグレーション

```bash
# 新規マイグレーション作成
uv run alembic revision --autogenerate -m "description"

# マイグレーション適用
uv run alembic upgrade head

# 1つ前にロールバック
uv run alembic downgrade -1

# 現在のリビジョン確認
uv run alembic current

# マイグレーション履歴
uv run alembic history
```

## プロジェクト構造

```
backend/
├── src/
│   └── app/
│       ├── main.py              # FastAPIアプリケーション
│       ├── api/                 # APIエンドポイント
│       │   ├── oauth.py         # OAuth認証
│       │   └── webauthn.py      # WebAuthn認証
│       ├── core/                # コア設定
│       │   ├── config.py        # アプリケーション設定
│       │   └── security.py      # JWT生成・検証
│       ├── db/                  # データベース
│       │   └── base.py          # SQLAlchemyセットアップ
│       ├── models/              # データベースモデル
│       │   ├── user.py          # Userモデル
│       │   ├── auth_factor.py   # AuthFactorモデル
│       │   └── trust_signal.py  # TrustSignalモデル
│       ├── schemas/             # Pydanticスキーマ
│       │   └── token.py         # トークンスキーマ
│       └── services/            # ビジネスロジック
│           ├── assurance.py     # Assurance Score計算
│           ├── trust.py         # Trust Signals計算
│           ├── token.py         # トークン生成
│           ├── oauth.py         # OAuth処理
│           ├── user.py          # ユーザー管理
│           └── webauthn.py      # WebAuthn処理
├── tests/                       # テストコード
├── migrations/                  # Alembicマイグレーション
├── pyproject.toml              # プロジェクト設定
├── alembic.ini                 # Alembicマイグレーション設定
└── README.md                   # このファイル
```

## Glyph トークン構造

Glyphが発行するJWTトークンは以下の構造を持ちます：

```json
{
  "aegis_assurance": {
    "score": 76,
    "level": "beta",
    "factors": ["webauthn", "google"],
    "freshness_days": 18
  },
  "extensions": {
    "trust_signals": {
      "risk": {
        "score": 24,
        "band": "low",
        "updated_at": "2025-10-15T00:00:00Z",
        "ttl_sec": 604800
      }
    }
  }
}
```

### Assurance Levels

- **α (Alpha)**: Score 40+ - 基本的な本人性確認
- **β (Beta)**: Score 70+ - 強化された本人性確認
- **γ (Gamma)**: Score 85+ かつ直近のWebAuthn認証成功

### Factor Weights

- WebAuthn: 35
- Google / Microsoft: 25
- GitHub / X: 15
- Verified Email: 10
- KYC: 40

## 開発

### コードフォーマット

```bash
# Ruffでlint
uv run ruff check .

# Ruffで自動修正
uv run ruff check --fix .
```

### セキュリティチェック

```bash
# Banditでセキュリティスキャン
uv run bandit -r src/

# 依存関係の脆弱性チェック
uv run pip-audit
```

## ライセンス

Apache-2.0
