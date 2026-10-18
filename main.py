import os
import requests
import hashlib
import scratchattach as sa

# 1. GitHub Secrets からログイン情報を取得
username = os.environ.get("SCRATCH_USERNAME")
password = os.environ.get("SCRATCH_PASSWORD")

# 2. 正しくログインしてセッションを作成
session = sa.login(username, password)

project_id = "1392785288"

# 3. 変更したい画像のURLからデータを取得して、一時ファイルとして保存
image_url = "https://uploads.scratch.mit.edu/get_image/project/1392601120_144x108.png"
response = requests.get(image_url)
image_data = response.content

# 一度 "temp_costume.png" という名前でローカルに保存する
with open("temp_costume.png", "wb") as f:
    f.write(image_data)

# 4. 画像のMD5ハッシュ値を計算
md5_hash = hashlib.md5(image_data).hexdigest()
asset_id = md5_hash
md5ext = f"{asset_id}.png"

# 5. 位置引数（キーワード引数名なし）でScratchサーバーにアップロード
session.upload_asset("temp_costume.png")

# 6. プロジェクトオブジェクトを接続し、現在のJSONを取得
project = session.connect_project(project_id)
project_json = project.json()

target_sprite_name = "sprite1"

# 7. JSON構造（"declaration"がある形）に合わせて書き換え
for target in project_json["targets"]:
    if target["name"] == target_sprite_name:
        costume_decl = target["costumes"][0]["declaration"]
        
        costume_decl["assetId"] = asset_id
        costume_decl["md5ext"] = md5ext
        costume_decl["dataFormat"] = "png"
        
        if "declaredPath" in target["costumes"][0]:
            target["costumes"][0]["declaredPath"] = md5ext
        if "path" in target["costumes"][0]:
            target["costumes"][0]["path"] = f"files/{md5ext}"
        break

project.set_json(project_json)

print("プロジェクトのJSONの変更と保存が成功しました！")