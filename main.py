import os
import requests
import hashlib
import scratchattach as sa

# 1. GitHub Secrets からログイン情報を取得
username = os.environ.get("SCRATCH_USERNAME")
password = os.environ.get("SCRATCH_PASSWORD")

# 2. 正しくログインしてセッションを作成
session = sa.login(username, password)

project_id = 1392785288"

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

# 5. 【修正箇所】ファイルを指定してScratchサーバーにアップロード
# 引数を filename に変更し、不要になった data_format は消去します
session.upload_asset(filename="temp_costume.png", asset_id=asset_id)

# 6. プロジェクトオブジェクトを接続し、現在のJSONを取得
project = session.connect_project(project_id)
project_json = project.json() # または sa.get_project_json(project_id)

target_sprite_name = "sprite1"

# 7. あなたのJSON構造（"declaration"がある形）に合わせてピンポイントで書き換え
for target in project_json["targets"]:
    if target["name"] == target_sprite_name:
        # あなたが提示してくれた "declaration" の中身を書き換える
        costume_decl = target["costumes"][0]["declaration"]
        
        costume_decl["assetId"] = asset_id
        costume_decl["md5ext"] = md5ext
        costume_decl["dataFormat"] = "png"
        
        # もし下部にあった "declaredPath" や "path" も同じターゲット内にあるなら書き換え
        if "declaredPath" in target["costumes"][0]:
            target["costumes"][0]["declaredPath"] = md5ext
        if "path" in target["costumes"][0]:
            target["costumes"][0]["path"] = f"files/{md5ext}"
        break

# 8. ❌ upload_project_json ではなく、⭕ project.set_json を使う
# これでトークン問題も自動で解決し、保存されます！
project.set_json(project_json)

print("プロジェクトのJSONの変更と保存が成功しました！")
