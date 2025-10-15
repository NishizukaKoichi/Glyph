# ✦ Glyph — 完全仕様書（v1.0・魔法印版）

- Version: 1.0.1
- License: Apache-2.0
- Status: OSSリリース準備完了
- Tagline: Glyph — 刻まれた印章が、本人性と信頼を運ぶ。

---

## 1. 概要

Glyph は、外部 IdP（Google / Microsoft / GitHub / X）と WebAuthn パスキーを束ね、**本人性（Assurance）と社会的信頼（Trust Signals）** を一つの **印章（Glyph）** として刻印する認証ブローカー。

- 誰でも無料でデプロイ可能（Cloudflare 無料枠 / VPS）。
- Assurance Score で「誰なのか」を定量化。
- Trust Signals で「どう扱われているか」を署名付きで配布。
- トークンは常に Glyph（印章）を保持し、RP（サービス提供者）が読み解いて結界を張る。

---

## 2. 発行クレーム（JWT・Glyphの形）

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
        "updated_at": "2025-10-05T00:00:00Z",
        "ttl_sec": 604800
      },
      "provenance": [
        {
          "issuer": "https://srv-a.example.com",
          "kind": "block",
          "count": 3,
          "since": "2025-08-14T12:00:00Z",
          "jws": "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9...",
          "expires_at": "2025-11-14T12:00:00Z",
          "weight": 0.9
        }
      ],
      "consent": {
        "granted": true,
        "scope": {
          "block": { "share": true, "issuers": ["srv-a.example.com"] },
          "mute": { "share": false }
        },
        "retention": { "max_age_days": 180, "auto_decay": true }
      },
      "policy": {
        "decay": { "half_life_days": 90, "min_factor": 0.15 },
        "caps": { "issuer_daily_max": 50 },
        "appeals_url": "https://Glyph.id/appeals"
      },
      "transparency": {
        "receipts_endpoint": "https://Glyph.id/me/trust/receipts",
        "explain_url": "https://Glyph.id/me/trust/explain"
      },
      "legal": {
        "disclaimer_url": "https://Glyph.id/legal/trust-disclaimer",
        "indemnification": true,
        "liability_cap": "signals-are-advisory"
      }
    }
  }
}
```

Glyph のトークンは印章＝二層構造。

- Assurance：印を刻む主体そのもの。
- Trust Signals：印の周囲に刻まれる社会的な模様。

---

## 3. スコア設計

### Assurance（本人性）

`score = Σ(weight × independence × freshness × novelty)`

- WebAuthn = 35, Google / Microsoft = 25, GitHub / X = 15, Verifiedメール = 10, KYC = 40
- レベル区分: α (40+) / β (70+) / γ (85+ かつ 直近 WebAuthn 成功)

### Trust（社会的信頼）

`trust_risk = Σ(weight × independence × freshness × credibility)`

- block = 1.0, mute = 0.4
- independence: 同一クラスタ 0.5 / 異クラスタ 1.0
- freshness: ハーフライフ 90 日
- credibility: 発行者の誤認率や撤回率に基づき 0.6–1.0
- 出力: low / medium / high（帯域優先で誤爆抑制）

---

## 4. 哲学（Glyphの核）

- Glyph は印章であり、中立の運送業者。
- 判断は RP が下す（自動 BAN 禁止、段階防御を推奨）。
- 透明性・撤回・救済を標準装備。
- ユーザー主権：同意粒度を発行者別・種類別に選択可能。

---

## 5. セキュリティ

- 署名鍵: OSS = ファイル / 公式 = KMS・HSM
- Refresh Token 短寿命、将来 DPoP 対応
- 改ざん検出: チェーンハッシュ監査ログ
- 発行者ホワイトリスト & 相互署名

---

## 6. 法務枠組み

- Glyph は common-carrier：信号を運ぶだけ。
- 責任分界：
  - 発行者 → 信号の真偽
  - RP → 信号の利用判断
  - Glyph → 信号の署名検証・配布のみ
- ToS に免責・賠償制限・独立判断義務を明記。

---

## 7. 救済（Appeals）

- 24 時間以内に初回応答。
- 7 日以内に解決。
- 救済手段：receipt 撤回 / score 補正 / 発行者への警告。
- 異議申立て数は発行者 credibility に反映。

---

## 8. スケーラビリティ

- JWKS キャッシュ & 差分計算で高速化。
- 発行者別レート制限 & バッチ検証。
- SLO: 検証 p95 < 25ms（キャッシュ命中時）。

---

## 9. 開発者ガイド

### 危険パターン（禁止）

```javascript
if (token.extensions.trust_signals.risk.band === "high") {
  reject(); // ❌ 自動BAN
}
```

### 推奨（段階防御）

```javascript
if (
  token.extensions.trust_signals.risk.band === "high" &&
  token.aegis_assurance.level !== "gamma"
) {
  routeToManualReview();
}
```

Glyph SDK はアンチパターンを検知して警告を出す。

---

## 10. デザイン（Glyphの象徴）

- シンボル：円環の中に刻まれる六芒星（中立と防御の象徴）
- 色彩：
  - 群青（守り）
  - 水色（透明性）
  - 金色（署名・印章）
- UI：印章風のアニメーション、透明なレイヤーが重なるエフェクト

---

## 11. デプロイ

- OSS: Cloudflare Workers + D1 + KV / VPS (Docker Compose)
- 公式: Fly.io + Neon + Upstash + Vercel + Stripe

---

## 12. ロードマップ

- v1.0: Glyph（Assurance + Trust）/ OIDC / WebAuthn / 同意 UI
- v1.1: 監査ログエクスポート / 公式署名 API
- v2.0: 発行者プログラム（相互署名連合）

---

## 13. 結び

Glyph は印を刻む基盤だ。本人性と社会的信号を一枚の印章に封じ、透明に開示し、RP が自らの防御結界を張る助けとする。

**Glyph = 信を刻む印章。**
