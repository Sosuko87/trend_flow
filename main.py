import os
import requests
import hashlib
import scratchattach as sa

# 1. GitHub Secrets からログイン情報を取得
username = os.environ.get("SCRATCH_USERNAME")
password = os.environ.get("SCRATCH_PASSWORD")

# 2. 正しくログインしてセッションを作成
session = sa.login(username, password)
project = session.connect_project("1392785288")

def image_change(url)

    # 3. 変更したい画像のURLからデータを取得して、一時ファイルとして保存
    image_url = url
    response = requests.get(image_url)
    image_data = response.content

    # 一度 "temp_costume.png" という名前でローカルに保存する
    with open("temp_costume.png", "wb") as f:
        f.write(image_data)

    # 4. 画像のMD5ハッシュ値を計算
    md5_hash = hashlib.md5(image_data).hexdigest()
    asset_id = md5_hash
    md5ext = f"{asset_id}.png"

    # 5. Scratchサーバーに画像をアップロード
    session.upload_asset("temp_costume.png")

    # 6. Scratch API から project_token を取得して JSON をダウンロード
    headers = {"User-Agent": "Mozilla/5.0"}
    token_res = requests.get(f"https://api.scratch.mit.edu/projects/{project_id}", headers=headers).json()
    project_token = token_res.get("project_token", "")

    json_url = f"https://projects.scratch.mit.edu/{project_id}?token={project_token}"
    project_json = requests.get(json_url, headers=headers).json()

    target_sprite_name = "Sprite1"

    # 7. コスチューム情報の書き換え（KeyError対策）
    for target in project_json["targets"]:
        if target["name"] == target_sprite_name:
            costume = target["costumes"][0]
        
            # Scratch 3.0 の標準構造（直下のプロパティ）を更新
            costume["assetId"] = asset_id
            costume["md5ext"] = md5ext
            costume["dataFormat"] = "png"
        
            # もし 'declaration' キーが存在している場合のみ更新
            if "declaration" in costume:
                costume["declaration"]["assetId"] = asset_id
                costume["declaration"]["md5ext"] = md5ext
                costume["declaration"]["dataFormat"] = "png"
            
            if "declaredPath" in costume:
                costume["declaredPath"] = md5ext
            if "path" in costume:
                costume["path"] = f"files/{md5ext}"
            break

    # 8. 更新したJSONをScratchに保存
    project.set_json(project_json)

    print(f"画像{url}の更新に成功しました")
image_change(https://uploads.scratch.mit.edu/get_image/project/1392601120_144x108.png)