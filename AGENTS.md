# AGENTS.md

## Project

Mreminder

Windows向けのシステムトレイ常駐型リマインダーアプリ。

---

## Technology Stack

- Python 3.12
- PySide6
- SQLite3
- PyInstaller
- pystray
- Pillow

---

## Coding Rules

- 必ず型ヒントを書く
- Pythonicなコードを書く
- PEP8を守る
- Ruffエラー0
- Black準拠
- コメントは必要最小限
- docstringを書く
- マジックナンバーは禁止

---

## Architecture

Presentation

↓

Service

↓

Repository

↓

SQLite

UIはDBへ直接アクセスしてはいけない。

RepositoryだけがSQLiteへアクセスする。

---

## UI Rules

- PySide6のみ使用
- Qt Designerは使わない
- コードだけでUIを構築する
- ダークテーマ固定

---

## Database

SQLiteを使用。

JSON保存は禁止。

---

## Notifications

Windows標準通知は使わない。

独自ポップアップ通知を使用する。

---

## Development Rules

実装前に

- 変更内容
- 影響範囲

を確認する。

勝手な設計変更は禁止。

---

## Git

小さくCommitする。

コミットメッセージは

v0.x.x

形式で管理する。