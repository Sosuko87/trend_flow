import scratchattach as scratch3
import requests
import hashlib
import os
# 1. Scratchにログインしてセッションを作成
session = scratch3.login("あなたのユーザー名", "あなたのパスワード")

project_id = "1392785288"
project_token = session.get_project_token(project_id)

# 2. 変更したい画像のURLからデータを取得
image_url = "https://uploads.scratch.mit.edu/get_image/project/1392601120_144x108.png"
response = requests.get(image_url)
image_data = response.content

# 3. 画像のMD5ハッシュ値を計算
md5_hash = hashlib.md5(image_data).hexdigest()
asset_id = md5_hash
# Scratch上でのファイル名（例: abcde12345...png）
md5ext = f"{asset_id}.png"

# 4. 画像（アセット）をScratchのサーバーにアップロード
# ※これによりScratch側で画像が認識されます
session.upload_asset(image_data, asset_id=asset_id, data_format="png")

# 5. プロジェクトのJSONを取得して書き換え
project_json = scratch3.get_project_json(project_id)

target_sprite_name = "sprite1"

# 対象のスプライト（またはステージ）を探す
for target in project_json["targets"]:
    if target["name"] == target_sprite_name:
        # 1つ目のコスチューム（インデックス0）の情報を書き換える
        first_costume = target["costumes"][0]
        first_costume["assetId"] = asset_id
        first_costume["md5ext"] = md5ext
        first_costume["dataFormat"] = "png"
        break

# 6. 変更したJSONをプロジェクトにアップロードして保存
session.upload_project_json(project_id, project_json, project_token=project_token)

print("終了")
