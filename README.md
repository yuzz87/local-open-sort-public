# 概要
HTTPS化したWebアプリケーションをlocal環境で誰でも使用できるようにしました

# 動画などを記載

# 動作手順
必要なもの

事前に次をインストールしてください。

Python 3.11 以上

Docker Desktop

VS Code

プロジェクトを開く

リポジトリを clone したあと、sort_game フォルダを開いてください。

git clone <このリポジトリのURL>
cd sort_random_game/sort_game

VS Code を使う場合は、sort_random_game ではなく sort_game を開くのが重要です。

初回セットアップ
1. Python パッケージをインストール
pip install -r requirements.txt

requirements-dev.txt がある場合は、必要に応じてこちらも入れてください。

pip install -r requirements-dev.txt
2. Docker Desktop を起動

Docker Desktop を起動した状態にしてください。

確認:

docker --version
docker compose version
3. env ファイルを自動生成

初回実行時に自動生成されますが、手動で行う場合はこれです。

python scripts/init_env.py

これで次のファイルが必要なら自動作成されます。

.env

.env.test

一番簡単な実行方法
VS Code から実行する方法
テスト実行

Ctrl + Shift + P

Tasks: Run Task を選択

Run Tests を選択

Web アプリ起動

Ctrl + Shift + P

Tasks: Run Task

Run Web App

Web アプリ停止

Ctrl + Shift + P

Tasks: Run Task

Stop Web App

ターミナルから実行する方法
テスト実行

Windows:

.\run-tests.ps1
Web アプリ起動

Windows:

.\run-web.ps1
Web アプリ停止

Windows:

.\stop-web.ps1
テスト実行時に起きること

Run Tests または .\run-tests.ps1 を実行すると、自動で次を行います。

.env と .env.test を確認

Docker でテスト用 MySQL コンテナを起動

schema を適用

seed を適用

pytest を実行

テスト用コンテナを停止

Web アプリ起動時に起きること

Run Web App または .\run-web.ps1 を実行すると、自動で次を行います。

.env を確認

Docker Compose で db, app, nginx を起動

/health の応答を待つ

起動後にブラウザでアクセス可能になる

アクセス先:

http://127.0.0.1:8080
ログイン情報

ローカル確認用の seed ユーザーの情報：
email: test@1234.com
password: app_password


Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
3. Docker が動かない

Docker Desktop が起動しているか確認してください。

4. ModuleNotFoundError: No module named 'app'

sort_game ではなく、1つ上のフォルダで実行している可能性があります。

推奨確認手順
テスト確認
.\run-tests.ps1
Web 確認
.\run-web.ps1

ブラウザで:

http://127.0.0.1:8080
停止
.\stop-web.ps1
開発者向け補足

.env.example と .env.test.example は見本です

.env と .env.test は自動生成されます

# 対応アルゴリズム

# 主な機能

# local環境の使用技術

# 工夫した点

目的は、次の状態に近づけることでした。

誰でも
- テストを実行できる
- Webアプリを起動できる
- ローカル環境差で詰まりにくい
- GitHub Actions でも同じように通る

11. 誰でも使いやすい実行方法の整備
目標

「なるべく 1 コマンドで使える」状態にすることでした。

役割

run-tests.ps1
env 準備 → Docker DB 起動 → schema/seed → pytest → cleanup

run-web.ps1
env 準備 → local compose 起動 → healthcheck 待ち → URL 表示

stop-web.ps1
compose 停止

結果
ユーザー向けに

.\run-tests.ps1
.\run-web.ps1
.\stop-web.ps1

で操作できる設計を整理しました。


実施内容
.vscode/tasks.json を載せる方針


seed に固定ユーザーを入れる方針を整理

bcrypt ハッシュを固定で SQL に入れる考え方を整理

「ローカル専用なら固定ハッシュでよい」と整理

email: test@1234.com

password: app_password

15. ローカル MySQL を汚さない方針への変更
問題

他の人のローカル MySQL に test_user や test DB を作らせるのは負担が大きい

実施内容

Docker の DB コンテナを使う方式へ寄せる方針を整理しました。

効果

他人の MySQL 環境を汚さない

ローカル MySQL の有無に依存しにくい

テスト用 DB を使い捨てできる

1. GitHub Actions は Success まで到達
7. ローカル MySQL ではなく Docker DB コンテナを使う
8. 誰でも実行しやすい run-tests / run-web / stop-web の設計を整えた

GitHub Actions を使って CI を実装しました。
push / PR を契機に、テスト用DBの起動、schema/seed適用、pytest、Docker build、起動確認を自動化しています。
CD は未実装ですが、Docker ベースでデプロイしやすい構成にしています。


# AWS HTTPS化環境

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