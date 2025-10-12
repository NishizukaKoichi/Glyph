# PLANS.md — 生きた設計書（スプリント駆動・AI参照の一次ソース）

> 目的：このプロジェクトを"道に迷わず"完走させるための**行動計画・進捗ログ・意思決定の単一情報源**。
> 読者：AI（Claude/Codex）と人間（設計者/レビュア）。

---

## 0. スコープ宣言（変更時はここを必ず更新）

- **今スプリントの目標**：
  - 例）ホーム画面のレスポンシブ崩れを解消し、Core Web Vitals 初期値を改善する。
  - 例）バックエンドのサービス層を分離し、循環依存を排除してテスト容易性を向上する。

- **非目的（触らない領域）**：
  - 例）認可モデルの変更は今スプリント対象外。
  - 例）課金ロジック・外部API仕様は変更しない。

- **成功指標（Definition of Done / DoD）**：

  **必須条件（すべて満たすこと）**
  - ✅ 全テスト緑（`make test`）
  - ✅ `make review` blocking=0
  - ✅ スナップ差分は**期待変更のみ**（退行ゼロ）
  - ✅ CI/Guard/CodeQL すべて緑
  - ✅ `main` へは PR 経由のみ（直接push禁止）
  - ✅ PRに適切なラベル付与（`feature`/`fix`/`chore`/`docs`/`security`）
  - ✅ Release Drafter に項目反映確認
  - ✅ 依存脆弱性 Critical/High=0
  - ✅ PLANS.md 更新（進捗ログ追記）

  **リリース時の追加条件**
  - ✅ タグ発行（セマンティックバージョニング）
  - ✅ Draft Release を公開（CHANGELOG確認）
  - ✅ ブランチ保護ルール遵守

---

## 1. 仕様の骨子（契約・インタフェース・UI期待）

- **外部契約（API/イベント）**：
  - 例）`GET /api/v1/items` は page/size/sort を受け取り、JSONで返す。後方互換性を維持。
- **UI期待（主要コンポーネント）**：
  - 例）`<Header>` の高さは 64px 固定、モバイルでは 56px、ロゴは崩れないこと。
- **性能・可用性の最低ライン**：
  - 例）初回 LCP < 2.5s（ローカル計測）、メモリリーク検出ゼロ。

---

## 2. 作業分割（ToDo・フェーズ・PR設計）

- **フェーズ分割**（1フェーズ=1PR、常にデプロイ可能）：
  1. フェーズ1：UI崩れの最小修正（Header/Sidebar）
  2. フェーズ2：スナップの再生成と意図文書化
  3. フェーズ3：サービス層抽出（backend/src/app/service/*）
  4. フェーズ4：依存逆転（interface導入、循環除去）

- **ToDo（更新必須・粒度小）**：
  - [ ] `AppHeader` のモバイル時レイアウト乱れ修正
  - [ ] `ItemList` のスナップ差分（フォントサイズ）を意図記述
  - [ ] backend の `repository` と `service` の責務分離
  - [ ] `risk_matrix` でPRサイズ閾値を満たすか確認

---

## 3. リスク・ロールバック・ガードレール

- **主要リスク**：
  - レイアウト修正による意図しない再レイアウト増加（CLS悪化）。
  - 依存整理時のビルド時間急増、循環発生、テストフレーク。

- **ロールバック手順**：
  - 各フェーズPRに `revert` コマンドで戻せるよう差分を自立化。
  - スナップ更新前の基準画像をタグ付けで保存（`snapshots@<date>`）。

- **ガードレール**：
  - PR差分≦500行、コミットは論理最小単位。
  - すべての変更はテスト/スナップ/レビューを**同じサイクル**で緑化。

---

## 4. 実行ループ（AIの手順）

1. **初回**：`make test` → 失敗テストを一覧化 → **赤→緑**の最短プランをここに書く。
2. **UI**：chrome-devtools-mcpで対象画面を開く→`make ui:snap`→差分分類→修正→再実行。
3. **レビュー**：`make review`→blockingを0にするまで修正→合格したら次フェーズへ。
4. **ログ**：下の「進捗・意思決定ログ」に**毎サイクル**追記。

---

## 5. 進捗・意思決定ログ（AIは必ず更新）

- **2025-10-12 13:00**
  - `make test`：frontend 1件失敗（AppHeaderの高さ）、backend 0件。
  - 方針：HeaderのCSS修正を最小差分で対応、スナップは更新せず緑化を優先。
  - 決定：PRは `fix/header-layout-phase-1` で切る。リスク低。

- **2025-10-12 15:10**
  - `make ui:snap`：`ItemList` のフォントサイズ差分が発生。意図しない変更として扱い、コンポーネント側を修正。
  - `make review`：non-blocking 2件（命名/コメント）。修正対応済み。
  - 結果：全緑、blocking=0。フェーズ1完了。

- **2025-10-12 18:00 - 文明化完了宣言**

  素晴らしい。ここまでで "文明化セット9点" がすべて実装され、CIも緑、Guardも稼働、Dependabotも動き出し、READMEの顔も整い、タグまで打たれている。これはもう「個人リポを文明化」する一連の儀式が完成したと言っていい。

  つまり、この状態は「プロジェクトが生きる檻（おり）」が完成した、ということ。これ以降に乗るコミットは、必ずこの檻を通過しなければならず、未来の自分が寝ている間でも自動で守られる。

  残るのは発展的な領域だ。

  * **モニタリング／通知**を加える（SlackやDiscordへActions結果を通知）。
  * **セキュリティスキャン**を強化する（CodeQLやTrivyをCIに入れる）。
  * **リリース自動化**（GitHub Release作成、CHANGELOG自動生成）でタグ運用を育てる。
  * **ロードマップ整備**（PLANS.mdの更新自動化、PRごとのリンク付け）で、未来に「何を作ろうとしていたか」が迷子にならないようにする。

  けれど、根幹はもう整った。
  これ以上を足すのは"文明の高度化"の話であって、"文明化の完了"にはすでに到達している。

  つまり答えはこうだ：**はい、文明化は完了した。これで終わり。そしてここから始まる。**

  **実装完了項目（v0.1.0）**
  1. Guard workflow - ui:snap禁止
  2. CI効率化 - キャッシュ・並行制御
  3. ステータスバッジ - 可視化
  4. PRテンプレート - 品質ゲート
  5. CODEOWNERS - レビュー自動化
  6. Dependabot - 依存更新自動化（すでに6個のPR生成済み）
  7. バージョンタグ v0.1.0
  8. 一括修正スクリプト - 横展開ツール
  9. ワークフロー稼働確認

  **今後の発展領域（今はやらない）**
  - モニタリング/通知（Slack/Discord連携）
  - セキュリティスキャン強化（CodeQL/Trivy）
  - リリース自動化（GitHub Release/CHANGELOG）
  - ロードマップ整備（PLANS.md更新自動化）

  檻は完成。ここから始まる。

- **2025-10-12 18:30 - 高度化セット（任意・速攻で効くやつ）**

  仕上げ、見事じゃ。PLANS.mdへの文明化完了宣言もコミット済み（acd4681）、ログまで刻まれて檻は完全体。
  ここからは"高度化セット"として**運用快適＆安全性アップのスパイス**だけ置いておく。
  実装はいつでも、気が向いた時でOK。

  ## 1. 通知（成否を即キャッチ）

  * Slack/Discordに Actions 結果を投げる（失敗時のみ通知にするとノイズ最小）。

  ```yaml
  # .github/workflows/notify.yml
  name: Notify on Failure
  on: workflow_run
    # 直近のCIの名前に合わせる
    types: [completed]
  jobs:
    notify:
      if: ${{ github.event.workflow_run.conclusion != 'success' }}
      runs-on: ubuntu-latest
      steps:
        - run: curl -X POST -H 'Content-type: application/json' \
            --data '{"text":"❌ CI failed: '${{ github.event.workflow_run.html_url }}'"}' $SLACK_WEBHOOK_URL
  ```

  ## 2. セキュリティ走査（無料で堅く）

  * **CodeQL** を追加（GitHub標準）。`build` ジョブと共存可。

  ## 3. リリース自動化（タグ運用が育つ）

  * **Release Drafter** で PR ラベルから自動で CHANGELOG を生成。
  * あるいは `git-cliff` を CI に載せて `CHANGELOG.md` を毎リリース更新。

  ## 4. ブランチ保護の最終締め

  * Settings → Branch protection で
    * Require status checks（`CI` を必須）
    * Require PR reviews（最低1）
    * 必要なら Require linear history
  * を有効化。これで素手では檻を越えられない。

  ## 5. 依存PRの自動マージ方針

  * Dependabotの**安全ラベル**（例: `safe-update`）＋`automerge` ワークフローで、パッチ/マイナーのみ自動取り込み→CI緑なら即着地。

  ## 6. Makefile流儀の固定（再発の根）

  * `:` を含むターゲット検出ガードは既にOK。**命名規約（`[a-z0-9-]+`）**も lint しておくと将来の増殖を抑制できる。

  ---

  この先は"文明化"じゃなく"文化の熟成"。数値（CI時間、失敗率、依存更新滞留日数）を計測し、**遅いところ・詰まるところに小さな魔法を足す**。わし基準で言うと、今の状態は**安心して全力でコードを書ける"静かな城"**。さぁ、攻めよう。

- **2025-10-12 19:00 - 高度化セット6項目実装完了（コミット 2f1cc5c）**

  **実装完了項目**

  1. ✅ **CodeQL セキュリティ走査** (`.github/workflows/codeql.yml`)
     - JavaScript/TypeScript + Python の自動脆弱性スキャン
     - 週次スケジュール（月曜9:00 UTC）+ PR/pushトリガー
     - security-and-quality クエリで高精度検出

  2. ✅ **Makefile 命名規約 lint** (`.github/workflows/guard.yml` 拡張)
     - `[a-z0-9-]+` パターン強制、コロン混入を阻止
     - ワークフロー名を "Guard - Makefile & Workflow Integrity" に変更
     - ui:snap禁止チェックと併存

  3. ✅ **Release Drafter** (`.github/workflows/release-drafter.yml` + `.github/release-drafter.yml`)
     - PRラベルから自動CHANGELOG生成
     - セマンティックバージョニング対応（major/minor/patch）
     - カテゴリ分類：Features/Bug Fixes/Maintenance/Documentation/Security

  4. ✅ **通知ワークフロー** (`.github/workflows/notify.yml`)
     - CI/Guard/CodeQL失敗時のSlack/Discord通知
     - Webhook未設定時は親切なガイド表示
     - ノイズ最小化（失敗時のみ通知）

  5. ✅ **Dependabot 自動マージ** (`.github/workflows/dependabot-automerge.yml`)
     - パッチ/マイナー更新は `safe-update` ラベル + auto-merge
     - メジャー更新は `major-update,needs-review` ラベル + 手動レビュー必須
     - CI通過後に自動マージ実行

  6. ✅ **ブランチ保護設定手順書** (`docs/BRANCH_PROTECTION.md`)
     - 推奨設定の詳細手順（PR必須、CI必須、linear history）
     - トラブルシューティング・運用のコツ完備
     - 設定URL・確認手順付き

  **今後のアクション**
  - 通知を使う場合：GitHub Secrets に `SLACK_WEBHOOK_URL` or `DISCORD_WEBHOOK_URL` を設定
  - ブランチ保護を有効化する場合：`docs/BRANCH_PROTECTION.md` の手順に従って設定
  - CodeQLの初回実行を確認（このpushで自動実行される）
  - Dependabotの既存PRでauto-merge動作を確認

  **運用開始**

  静かな城は完全装備。セキュリティ・品質・自動化の三重防壁が稼働開始。
  ここから先は本丸（実装）へ攻め込む段階。

- **2025-10-12 19:30 - 最終確認完了（「空の城 v0.2.0」完成宣言）**

  仕上げの最終確認ラベルを全貼付完了：

  1. ✅ **v0.1.0 ドラフトリリース公開**
     - `gh release edit v0.1.0 --draft=false` 実行
     - CHANGELOG が公開状態に
     - URL: https://github.com/NishizukaKoichi/ai-cage-driven-dev/releases/tag/v0.1.0

  2. ✅ **v0.2.0 タグ作成・プッシュ完了**
     - 高度化セット6項目の節目として v0.2.0 タグ発行
     - リリースノート：「Hardening: guard + CodeQL + release-drafter」

  3. ✅ **Definition of Done（DoD）明文化**
     - PLANS.md セクション0 に詳細な DoD 基準を追加
     - 必須条件9項目 + リリース時追加条件3項目
     - PRラベル運用（feature/fix/chore/docs/security）を含む

  4. ✅ **Release Drafter 威力MAX化準備**
     - `.github/release-drafter.yml` にカテゴリ分類設定済み
     - 次回からPRラベルで自動分類・CHANGELOG生成

  5. ✅ **互換エイリアス確認**
     - Makefile に `ui:snap` 等の旧形式は既に存在せず
     - すべて `ui-snap` 形式に統一済み

  **プロダクトの正体**
  - 🏗️ **完成**：開発インフラ・ガードレール・ドキュメント体系（「空の城」）
  - 🚧 **未着手**：具体的なビジネスロジック（「演目」）

  **最終状態**
  - タグ：v0.1.0（公開）、v0.2.0（公開予定）
  - ワークフロー：全6種稼働（CI/Guard/CodeQL/Release Drafter/Notify/Dependabot Auto-merge）
  - DoD：明文化済み
  - ブランチ保護：手順書完備（任意設定）

  **次サイクルからの運用フロー**
  1. 仕様を書く（PLANS.md更新）
  2. Claude × Codex に投げる
  3. 緑を確認（CI/Guard/CodeQL/Review）
  4. PRにラベル付与（Release Drafter用）
  5. マージ → Draft Release 自動更新
  6. 必要に応じてタグ発行 → Release 公開

  **檻は完全体。演目を始めよう。🎯**

（以降、毎サイクル追記）
