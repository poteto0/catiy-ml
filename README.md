- `detect_cat`: 猫が写っているかどうかを判定する
- `trim_cat`: 猫部分のみトリミングする(`detect_cat`)
- `classify_cat`: 猫の判別を行う(`trim_cat`)
- `status_task`: taskのstatusを見る

他のapiはそれぞれ到達部分までやるイメージ
`classify_cat`: register task, -> {"status": "draft", "taskId": "<uuid>", "has_cat": false, "cats": []}
=> `detect_cat`: false -> {"status": "finish", "taskId": "<uuid>", "has_cat": false, "cats": []}
| yes, status="detect_cat:finish", has_cat=true
=> `trim_cat`: error -> {"status": "trim_cat:failed", "taskId": "<uuid>", "has_cat": true, "cats": []}
| normal, status="trim_cat:finish", cat_images=[<r2-uploaded>...]
=> `classify_cat`: error =>
normal -> {"status": "classify_cat:finish", "taskId": "<uuid>", "has_cat": true, "cats": [{"cat_name": "<cat-name>", "cat_image": "<r2-uploaded>"}]}

### 未定ゾーン

- `upload_immich`

### 他

detect_catもoriginalImageをR2に上げようか。
