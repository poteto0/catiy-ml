# catiy-ml

Yoloで、画像中の猫を判定するAPI

- 猫の有無判定
- 猫の画像トリミング

## Api

- 判定した猫の画像をcloudflare R2に上げる
- 判定などは時差で行い、タスクステータスを後から問い合わせる設計

## Contribution

- `app/`: application
- `tests/`: ut(不要そうなところはいらない)
- `e2e/`: e2eテスト(ローカルでの実行を想定)

`just ci`が通ったらコミット可能
