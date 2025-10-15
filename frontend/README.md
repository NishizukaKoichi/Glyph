# Glyph Frontend

Glyph認証ブローカーのフロントエンド実装（予定）。

## 概要

このディレクトリには、Glyphの将来的なフロントエンド実装のための基本構造が含まれています。

## 計画中の機能

### 認証フロー

- **WebAuthn/Passkey登録**: 
  - デバイス登録UI
  - QRコード表示（モバイル連携）
  - 登録完了確認

- **WebAuthn/Passkey認証**:
  - ワンクリック認証
  - 複数デバイス選択
  - フォールバック（OAuth）

- **OAuth認証**:
  - ソーシャルログインボタン（Google / Microsoft / GitHub / X）
  - OAuth コールバック処理
  - トークン保存・管理

### ダッシュボード

- **Assurance Score表示**:
  - α/β/γ レベル表示
  - 登録済みファクター一覧
  - スコア向上の提案

- **認証ファクター管理**:
  - WebAuthn デバイス一覧・削除
  - OAuth 連携一覧・解除
  - 最終使用日時表示

- **Trust Signals設定**:
  - 同意管理（発行者別・種類別）
  - プライバシー設定
  - 異議申し立て

### Glyph印章UI

- **印章デザイン**:
  - 円環の中に刻まれる六芒星
  - 色彩: 群青（守り）/ 水色（透明性）/ 金色（署名）
  - 印章風アニメーション
  - 透明なレイヤーが重なるエフェクト

## 技術スタック（予定）

- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **State Management**: React Context / Zustand
- **Styling**: Tailwind CSS / styled-components
- **WebAuthn**: @simplewebauthn/browser
- **HTTP Client**: fetch API / axios
- **Routing**: React Router
- **UI Components**: Radix UI / shadcn/ui

## 開発ロードマップ

### Phase 6 (進行中)
- [x] プロジェクト構造作成
- [x] package.json設定
- [ ] npm install実行
- [ ] 基本レイアウトコンポーネント
- [ ] ルーティング設定

### Phase 7 (予定)
- [ ] WebAuthn登録フロー実装
- [ ] WebAuthn認証フロー実装
- [ ] OAuth統合（4プロバイダー）
- [ ] エラーハンドリング

### Phase 8 (予定)
- [ ] ダッシュボード実装
- [ ] 認証ファクター管理画面
- [ ] Trust Signals設定画面
- [ ] レスポンシブデザイン

### Phase 9 (予定)
- [ ] 印章UIアニメーション
- [ ] アクセシビリティ対応
- [ ] 国際化（i18n）
- [ ] PWA対応

## 現在の状態

プロジェクト構造とビルド設定のみ作成済み。
実装は今後のフェーズで進めます。

## プロジェクト構造（予定）

```
frontend/
├── public/
│   └── assets/          # 静的アセット
├── src/
│   ├── components/      # Reactコンポーネント
│   │   ├── auth/        # 認証関連
│   │   ├── dashboard/   # ダッシュボード
│   │   ├── layout/      # レイアウト
│   │   └── common/      # 共通コンポーネント
│   ├── hooks/           # カスタムフック
│   ├── services/        # APIクライアント
│   ├── types/           # TypeScript型定義
│   ├── utils/           # ユーティリティ
│   ├── App.tsx          # ルートコンポーネント
│   └── main.tsx         # エントリーポイント
├── package.json
├── vite.config.ts
├── tsconfig.json
└── README.md            # このファイル
```

## 参考資料

- [Glyph仕様書](../README.md)
- [バックエンドAPI](../backend/README.md)
- [WebAuthn Guide](https://webauthn.guide/)
- [@simplewebauthn/browser](https://simplewebauthn.dev/)

## ライセンス

Apache-2.0
