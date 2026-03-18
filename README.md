# 概要
HTTPS化したWebアプリケーションをlocal環境で誰でも使用できるようにしました

# 画像の記載
<img width="1899" height="914" alt="image" src="https://github.com/user-attachments/assets/95d9a615-4c2b-400d-afa8-f20dbfd3a4f1" />
<img width="1906" height="925" alt="image (1)" src="https://github.com/user-attachments/assets/c9927c77-0ab9-4496-a438-1101e7863f2f" />



# ソートアルゴリズム可視化・比較 Webアプリ

ソートアルゴリズムの可視化・比較ができる Web アプリです。

C++ によるベンチマーク、Flask API、MySQL、Docker、GitHub Actions を使って構成しています。

今回の主な改善点は、AWS 上で動かしていた構成を、他の人でもローカルで再現しやすい形に整理したことです。

---

# 動作手順

## 必要なもの

事前に次をインストールしてください。

- Python 3.11 以上
- Docker Desktop
- VS Code

---

## プロジェクトを開く

リポジトリを clone したあと、`sort_game` フォルダを開いてください。

- `git clone https://github.com/yuzz87/local-open-sort-public`
- `cd sort_random_game/sort_game`

VS Code を使う場合は、`sort_random_game` ではなく `sort_game` を開くことが重要です。

---

## 初回セットアップ

### Docker Desktop を起動

Docker Desktop を起動した状態にしてください。

確認コマンド:

- `docker --version`
- `docker compose version`

### env ファイルを自動生成

初回実行時に自動生成されますが、手動で行う場合は次を実行してください。

- `python scripts/init_env.py`

これにより、必要に応じて次のファイルが自動作成されます。

- `.env`
- `.env.test`

---

# 一番簡単な実行方法

## VS Code から実行する方法

### テスト実行

- `Ctrl + Shift + P`
- `Tasks: Run Task` を選択
- `Run Tests` を選択

### Web アプリ起動

- `Ctrl + Shift + P`
- `Tasks: Run Task`
- `Run Web App`

### Web アプリ停止

- `Ctrl + Shift + P`
- `Tasks: Run Task`
- `Stop Web App`

---

## ターミナルから実行する方法

### テスト実行

Windows:

- `.\run-tests.ps1`

### Web アプリ起動

Windows:

- `.\run-web.ps1`

### Web アプリ停止

Windows:

- `.\stop-web.ps1`

---

# テスト実行時に起きること

`Run Tests` または `.\run-tests.ps1` を実行すると、自動で次を行います。

- `.env` と `.env.test` を確認
- Docker でテスト用 MySQL コンテナを起動
- schema を適用
- seed を適用
- pytest を実行
- テスト用コンテナを停止

---

# Web アプリ起動時に起きること

`Run Web App` または `.\run-web.ps1` を実行すると、自動で次を行います。

- `.env` を確認
- Docker Compose で `db`、`app`、`nginx` を起動
- `/health` の応答を待つ
- 起動後にブラウザでアクセス可能になる

アクセス先:

- `http://127.0.0.1:8080`

---

# ログイン情報

ローカル確認用の seed ユーザーの情報です。

- email: `test@1234.com`
- password: `app_password`

---

# よくある問題

## PowerShell の実行ポリシーで止まる

次を実行してください。

- `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

## Docker が動かない

Docker Desktop が起動しているか確認してください。

## ModuleNotFoundError: No module named 'app'

`sort_game` ではなく、1つ上のフォルダで実行している可能性があります。

---

# 推奨確認手順

## テスト確認

- `.\run-tests.ps1`

## Web 確認

- `.\run-web.ps1`

ブラウザで次にアクセスします。

- `http://127.0.0.1:8080`

## 停止

- `.\stop-web.ps1`

---

# 対応アルゴリズム

- Bubble Sort
- Selection Sort
- Insertion Sort
- Merge Sort
- Quick Sort
- Heap Sort

---

# 主な機能

- ソートアルゴリズムの可視化
- C++ エンジンによるベンチマーク実行
- 実行結果の保存
- 履歴表示
- 統計表示
- ローカル環境での起動
- Docker を使った DB 分離
- GitHub Actions による CI

---

# local環境の使用技術

## フロントエンド

- HTML
- CSS
- JavaScript

## バックエンド

- Python
- Flask

## ソート処理

- C++

## データベース

- MySQL 8

## 開発環境・コンテナ

- Docker
- Docker Compose

## テスト

- pytest

## CI

- GitHub Actions

## 開発補助

- VS Code Tasks

---

# 工夫した点

目的は、次の状態に近づけることでした。

- 誰でもテストを実行できる
- 誰でも Web アプリを起動できる
- ローカル環境差で詰まりにくい
- GitHub Actions でも同じように通る

---

## 誰でも使いやすい実行方法の整備

目標は、なるべく 1 コマンドで使える状態にすることでした。

役割は次の通りです。

- `run-tests.ps1`
- env 準備
- Docker DB 起動
- schema 適用
- seed 適用
- pytest 実行
- cleanup

- `run-web.ps1`
- env 準備
- local compose 起動
- healthcheck 待ち
- URL 表示

- `stop-web.ps1`
- compose 停止

結果として、次の操作で使えるように整理しました。

- `.\run-tests.ps1`
- `.\run-web.ps1`
- `.\stop-web.ps1`

---

## VS Code からも実行しやすい構成に整理

実施内容:

- `.vscode/tasks.json` を使う方針に整理
- VS Code からテスト・起動・停止を実行できるように整理

効果:

- ターミナル操作に慣れていない人でも使いやすい
- 実行手順を統一しやすい

---

## seed ユーザーを固定して確認しやすくした

実施内容:

- seed に固定ユーザーを入れる方針を整理
- bcrypt ハッシュを固定で SQL に入れる考え方を整理
- ローカル専用なら固定ハッシュでよいと整理

確認用ユーザー:

- email: `test@1234.com`
- password: `app_password`

効果:

- 起動後すぐにログイン確認できる
- 手動確認の手順を減らせる

---

## ローカル MySQL を汚さない方針に変更

問題:

- 他の人のローカル MySQL に `test_user` や test DB を作らせるのは負担が大きい

実施内容:

- Docker の DB コンテナを使う方式へ寄せる方針を整理

効果:

- 他人の MySQL 環境を汚さない
- ローカル MySQL の有無に依存しにくい
- テスト用 DB を使い捨てできる

---

## local 用と test 用の設定を分離した

実施内容:

- `.env.example` から `.env` を生成
- `.env.test.example` から `.env.test` を生成
- local 実行用と test 実行用で設定を分離

効果:

- ローカル起動とテスト実行の責務が分かりやすい
- 設定の衝突を防ぎやすい
- 初回セットアップを簡単にしやすい

---

## healthcheck を使って起動確認を安定化した

実施内容:

- DB コンテナに healthcheck を設定
- app は DB が healthy になるまで待つ構成に整理
- app 側も `/health` で起動確認できるようにした

効果:

- 起動順の問題で失敗しにくい
- 使える状態になってから次へ進める
- ローカルでも CI でも挙動をそろえやすい

---

# CI について

GitHub Actions を使って CI を実装しました。

push / PR を契機に、次を自動化しています。

- テスト用 DB の起動
- schema 適用
- seed 適用
- pytest 実行
- Docker build
- 起動確認

CD は未実装ですが、Docker ベースでデプロイしやすい構成にしています。

---

# まとめ

このプロジェクトでは、ソート可視化アプリとしての機能だけでなく、ローカルでも他の人が動かしやすい形に整理することを重視しました。

特に次の点を改善しました。

- GitHub Actions は Success まで到達
- ローカル MySQL ではなく Docker DB コンテナを使う
- 誰でも実行しやすい `run-tests`、`run-web`、`stop-web` の設計を整えた

その結果、テスト実行、Web アプリ起動、ローカル確認までを比較的再現しやすい構成にまとめることができました。

---

# 補足

- `.env.example` と `.env.test.example` は見本です
- `.env` と `.env.test` は自動生成されます
## AWS HTTPS化環境

### 対応アルゴリズム

- Bubble Sort
- Selection Sort
- Insertion Sort
- Merge Sort
- Quick Sort
- Heap Sort
---

## 主な機能

- ソートアルゴリズムの可視化
- C++ エンジンによるベンチマーク実行
- バトル結果の保存
- 保存済みバトル履歴の取得
- アルゴリズム別統計の集計
- OpenAPI による API ドキュメント表示
- AWS 本番環境での HTTPS 公開
- `/health` によるヘルスチェック対応

---

## 使用技術

### フロントエンド
- HTML
- CSS
- JavaScript

### バックエンド
- Python
- Flask
- Gunicorn
- Nginx

### ソートエンジン
- C++

### データベース
- MySQL 8
- Amazon RDS for MySQL

### API / ドキュメント
- REST API
- OpenAPI 3.0.2
- Flasgger
- Swagger UI

### インフラ
- Docker
- Docker Compose
- AWS EC2
- AWS ALB
- AWS ACM
- AWS Route 53
- AWS VPC

### テスト / 品質管理
- pytest
- pytest-cov
- coverage
- Flask test client
- GitHub Actions

### 開発ツール
- Git
- GitHub
- VS Code
- DBeaver

---

### ER図

<img width="511" height="398" alt="sort_portfolio_in_C++" src="https://github.com/user-attachments/assets/cf35cbd3-fcda-4aed-980e-c214a475db8e" />

### 画像の記載
<img width="1910" height="519" alt="image (2)" src="https://github.com/user-attachments/assets/11e39ce3-3337-4e43-9f6e-25b280e4cd7c" />
<img width="1909" height="827" alt="image (3)" src="https://github.com/user-attachments/assets/ddf521a7-3b9b-4132-a8f3-69c550468523" />



