import os
import requests
import hashlib
import scratchattach as sa
import time
username = os.environ.get("SCRATCH_USERNAME")
password = os.environ.get("SCRATCH_PASSWORD")


session = sa.login(username, password)
project_id = "1392785288"
sec_project_id = "1392601120"
project = session.connect_project(project_id)
sec_project = session.connect_project(sec_project_id)

def image_change(url):

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

#コメント処理
end = False
offset = 0
while True: 
    comments = sec_project.comments(limit=40, offset=offset)
    if not comments:
        break
        
    for c in comments:
        text = getattr(c, "content", "") or (c.get("content", "") if isinstance(c, dict) else str(c))
        if text.startswith("【仮応募】"):
            comment_result = text[5:]
            comment_id = c.id
            comment_user = c.author().id
            with open("id.txt", "r", encoding="utf-8") as f:
                content = f.read()
                if str(comment_id) in content:
                    end = True
                    break
                elif str(comment_result) in content:
                    sec_project.reply_comment(content=f"【問題発生】▶プロジェクトURL： https://scratch.mit.edu/projects/{comment_result}/ ◀はすでに応募されています。", parent_id=comment_id, commentee_id=comment_user)
                    continue
            try:
                checking = sa.get_project(comment_result)
            except:
                sec_project.reply_comment(content=f"【問題発生】コードが間違っている可能性があります。もう一度お試し下さい。", parent_id=comment_id, commentee_id=comment_user)
                
                continue
            love = checking.loves
            favorite = checking.favorites
            views = checking.views
            date = checking.share_date
            with open("id.txt", "a", encoding="utf-8") as f:
                f.write(f"{comment_result}, {comment_id}\n")
            sec_project.reply_comment(content=f"【応募完了】▶プロジェクトURL： https://scratch.mit.edu/projects/{comment_result}/ ◀", parent_id=comment_id, commentee_id=comment_user)
            time.sleep(0.5)
        elif text.startswith("▼▼▼ここより下のコメントは審査済みです▼▼▼"):
            end = True
            break
    if end:
        break
    offset += 40

if sec_project.comments(limit=1)[0][content] != "▼▼▼ここより下のコメントは審査済みです▼▼▼":
    sec_project.post_comment("▼▼▼ここより下のコメントは審査済みです▼▼▼")

#指数計算