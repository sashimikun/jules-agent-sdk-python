[English](README.md)

# Python用Jules Agent SDK

> **免責事項**: これは、Jules API SDKラッパーのオープンソース実装であり、Googleとは一切関係ありません。公式APIについては、https://developers.google.com/jules/api/ をご覧ください。

Jules API用のPython SDKです。Julesのセッション、アクティビティ、ソースを簡単に操作できるインターフェースを提供します。

![Jules](jules.png)

## クイックスタート

### インストール

```bash
pip install jules-agent-sdk
```

### 基本的な使い方

```python
from jules_agent_sdk import JulesClient

# APIキーで初期化
client = JulesClient(api_key="your-api-key")

# ソースの一覧を取得
sources = client.sources.list_all()
print(f"{len(sources)}個のソースが見つかりました")

# セッションの作成
session = client.sessions.create(
    prompt="認証モジュールにエラーハンドリングを追加する",
    source=sources[0].name,
    starting_branch="main"
)

print(f"セッションが作成されました: {session.id}")
print(f"確認用URL: {session.url}")

client.close()
```

## 設定

APIキーを環境変数として設定します:

```bash
export JULES_API_KEY="your-api-key-here"
```

APIキーは[Julesダッシュボード](https://jules.google.com)から取得してください。

## 機能

### APIカバレッジ
- **セッション**: 作成、取得、一覧表示、計画の承認、メッセージ送信、完了待機
- **アクティビティ**: 取得、自動ページネーション付き一覧表示
- **ソース**: 取得、自動ページネーション付き一覧表示


## ドキュメント

- **[クイックスタート](docs/QUICKSTART.md)** - 入門ガイド
- **[完全なドキュメント](docs/README.md)** - 完全なAPIリファレンス
- **[開発ガイド](docs/DEVELOPMENT.md)** - 貢献者向け

## 使用例

### コンテキストマネージャ（推奨）

```python
from jules_agent_sdk import JulesClient

with JulesClient(api_key="your-api-key") as client:
    sources = client.sources.list_all()

    session = client.sessions.create(
        prompt="認証のバグを修正",
        source=sources[0].name,
        starting_branch="main"
    )

    print(f"作成されました: {session.id}")
```

### Async/Awaitのサポート

```python
import asyncio
from jules_agent_sdk import AsyncJulesClient

async def main():
    async with AsyncJulesClient(api_key="your-api-key") as client:
        sources = await client.sources.list_all()

        session = await client.sessions.create(
            prompt="単体テストを追加",
            source=sources[0].name,
            starting_branch="main"
        )

        # 完了を待つ
        completed = await client.sessions.wait_for_completion(session.id)
        print(f"完了: {completed.state}")

asyncio.run(main())
```

### エラーハンドリング

```python
from jules_agent_sdk import JulesClient
from jules_agent_sdk.exceptions import (
    JulesAuthenticationError,
    JulesNotFoundError,
    JulesValidationError,
    JulesRateLimitError
)

try:
    client = JulesClient(api_key="your-api-key")
    session = client.sessions.create(
        prompt="私のタスク",
        source="sources/invalid-id"
    )
except JulesAuthenticationError:
    print("無効なAPIキーです")
except JulesNotFoundError:
    print("ソースが見つかりません")
except JulesValidationError as e:
    print(f"検証エラー: {e.message}")
except JulesRateLimitError as e:
    retry_after = e.response.get("retry_after_seconds", 60)
    print(f"レート制限を受けました。{retry_after}秒後にもう一度お試しください")
finally:
    client.close()
```

### カスタム設定

```python
client = JulesClient(
    api_key="your-api-key",
    timeout=60,              # リクエストのタイムアウト（秒）（デフォルト: 30）
    max_retries=5,           # 最大リトライ回数（デフォルト: 3）
    retry_backoff_factor=2.0 # バックオフ乗数（デフォルト: 1.0）
)
```

以下のエラーに対して自動的にリトライが行われます:
- ネットワークエラー（接続の問題、タイムアウト）
- サーバーエラー（5xxステータスコード）

以下のエラーに対してはリトライは行われません:
- クライアントエラー（4xxステータスコード）
- 認証エラー

## APIリファレンス

### セッション

```python
# セッションの作成
session = client.sessions.create(
    prompt="タスクの説明",
    source="sources/source-id",
    starting_branch="main",
    title="任意のタイトル",
    require_plan_approval=False
)

# セッションの取得
session = client.sessions.get("session-id")

# セッションの一覧表示
result = client.sessions.list(page_size=10)
sessions = result["sessions"]

# 計画の承認
client.sessions.approve_plan("session-id")

# メッセージの送信
client.sessions.send_message("session-id", "追加の指示")

# 完了待機
completed = client.sessions.wait_for_completion(
    "session-id",
    poll_interval=5,
    timeout=600
)
```

### アクティビティ

```python
# アクティビティの取得
activity = client.activities.get("session-id", "activity-id")

# アクティビティの一覧表示（ページネーション付き）
result = client.activities.list("session-id", page_size=20)

# すべてのアクティビティを一覧表示（自動ページネーション）
all_activities = client.activities.list_all("session-id")
```

### ソース

```python
# ソースの取得
source = client.sources.get("source-id")

# ソースの一覧表示（ページネーション付き）
result = client.sources.list(page_size=10)

# すべてのソースを一覧表示（自動ページネーション）
all_sources = client.sources.list_all()
```

## ロギング

リクエストの詳細を確認するには、ロギングを有効にします:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jules_agent_sdk")
```

## テスト

```bash
# すべてのテストを実行
pytest

# カバレッジ付きで実行
pytest --cov=jules_agent_sdk

# 特定のテストを実行
pytest tests/test_client.py -v
```

## プロジェクト構成

```
jules-api-python-sdk/
├── src/jules_agent_sdk/
│   ├── client.py              # メインクライアント
│   ├── async_client.py        # 非同期クライアント
│   ├── base.py                # リトライ機能付きHTTPクライアント
│   ├── models.py              # データモデル
│   ├── sessions.py            # セッションAPI
│   ├── activities.py          # アクティビティAPI
│   ├── sources.py             # ソースAPI
│   └── exceptions.py          # カスタム例外
├── tests/                     # テストスイート
├── examples/                  # 使用例
│   ├── simple_test.py         # クイックスタート
│   ├── interactive_demo.py    # 完全なデモ
│   ├── async_example.py       # 非同期の便用
│   └── plan_approval_example.py
├── docs/                      # ドキュメント
└── README.md
```

## 貢献

開発のセットアップとガイドラインについては、[DEVELOPMENT.md](docs/DEVELOPMENT.md)を参照してください。

## ライセンス

MITライセンス - 詳細は[LICENSE](LICENSE)ファイルをご覧ください。

## サポート

- **ドキュメント**: [docs/](docs/)フォルダを参照してください
- **例**: [examples/](examples/)フォルダを参照してください
- **問題**: GitHubでIssueを開いてください

## 次のステップ

1. `python examples/simple_test.py`を実行して試してください
2. 詳細については[docs/QUICKSTART.md](docs/QUICKSTART.md)をお読みください
3. その他のユースケースについては[examples/](examples/)フォルダを確認してください