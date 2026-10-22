import hashlib
import os
import time
from datetime import datetime, timezone
import requests
import scratchattach as sa

username = os.environ.get("SCRATCH_USERNAME")
password = os.environ.get("SCRATCH_PASSWORD")


session = sa.login(username, password)
project_id = "1392785288"
sec_project_id = "1392601120"
project = session.connect_project(project_id)
sec_project = session.connect_project(sec_project_id)


# --- JSON内のリストを変更する関数 ---
def update_list(list_name, new_data, target_sprite_name=None):
    """プロジェクトのJSONからリストを取得し、内容を新しいデータに置き換えます。

    :param list_name: 変更したいScratch上のリスト名
    :param new_data: 設定したい新しいデータ（リストや配列）
    :param target_sprite_name:
    リストが存在するスプライト名（省略時はStage含む全ターゲットから検索）
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    token_res = requests.get(
        f"https://api.scratch.mit.edu/projects/{project_id}", headers=headers
    ).json()
    project_token = token_res.get("project_token", "")

    json_url = (
        f"https://projects.scratch.mit.edu/{project_id}?token={project_token}"
    )
    project_json = requests.get(json_url, headers=headers).json()

    list_found = False

    for target in project_json["targets"]:
        # スプライト名指定がない場合、または名前が一致する場合に対象とする
        if target_sprite_name is None or target["name"] == target_sprite_name:
            if "lists" in target:
                for list_id, list_info in target["lists"].items():
                    # list_info[0] はリスト名、list_info[1] はリストの中身(配列)
                    if list_info[0] == list_name:
                        list_info[1] = list(new_data)
                        list_found = True
                        break
        if list_found:
            break

    if list_found:
        project.set_json(project_json)
        print(f"リスト「{list_name}」の更新に成功しました")
    else:
        print(f"リスト「{list_name}」が見つかりませんでした")


def image_change(url, costume):

    image_url = url
    response = requests.get(image_url)
    image_data = response.content

    # 一度ローカルに保存する
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
    token_res = requests.get(
        f"https://api.scratch.mit.edu/projects/{project_id}", headers=headers
    ).json()
    project_token = token_res.get("project_token", "")

    json_url = (
        f"https://projects.scratch.mit.edu/{project_id}?token={project_token}"
    )
    project_json = requests.get(json_url, headers=headers).json()

    target_sprite_name = "サムネ取得"

    # 7. コスチューム情報の書き換え（KeyError対策）
    for target in project_json["targets"]:
        if target["name"] == target_sprite_name:
            costume = target["costumes"][costume]

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


def time_find(time):
    share_date_utc = datetime.fromisoformat(time.replace("Z", "+00:00"))
    current_time_utc = datetime.now(timezone.utc)
    time_difference = current_time_utc - share_date_utc
    hours_passed = int(time_difference.total_seconds() // 3600)
    return hours_passed


# コメント処理
end = False
offset = 0
while True:
    comments = sec_project.comments(limit=40, offset=offset)
    if not comments:
        break

    for c in comments:
        text = getattr(c, "content", "") or (
            c.get("content", "") if isinstance(c, dict) else str(c)
        )
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
                    sec_project.reply_comment(
                        content=f"【問題発生】▶プロジェクトURL： https://scratch.mit.edu/projects/{comment_result}/ ◀はすでに応募されています。",
                        parent_id=comment_id,
                        commentee_id=comment_user,
                    )
                    continue
            try:
                checking = sa.get_project(comment_result)
            except:
                sec_project.reply_comment(
                    content=f"【問題発生】コードが間違っている可能性があります。もう一度お試し下さい。",
                    parent_id=comment_id,
                    commentee_id=comment_user,
                )

                continue
            with open("id.txt", "a", encoding="utf-8") as f:
                f.write(f"{comment_result}, {comment_id}\n")
            sec_project.reply_comment(
                content=f"【応募完了】▶プロジェクトURL： https://scratch.mit.edu/projects/{comment_result}/ ◀",
                parent_id=comment_id,
                commentee_id=comment_user,
            )
            time.sleep(0.5)
        elif text.startswith("▼▼▼ここより下のコメントは審査済みです▼▼▼"):
            end = True
            break
    if end:
        break
    offset += 40

if sec_project.comments(limit=1)[0].content != "▼▼▼ここより下のコメントは審査済みです▼▼▼":
    sec_project.post_comment("▼▼▼ここより下のコメントは審査済みです▼▼▼")

data = []

# 指数計算
with open("id.txt", "r", encoding="utf-8") as f:
    for line in f:
        p_id, comment_name = line.strip().split(",")
        p = sa.get_project(p_id)
        h = time_find(p.share_date)
        if h < 720:
            l = p.loves
            f = p.favorites
            v = p.views
            r = p.remix_count
            point = (
                ((4 * l + 6 * f) ** 0.9)
                / (max(24, h) + (v / (l + f + 1)))
                * (r**0.5 + 1)
                * 50
            )
            print(f"{l}, {f}, {v}, {h}, {r}, 合計スコア:{point}")
            data.append((point, p_id))
            time.sleep(5)
        else:
            time.sleep(1)

data.sort(reverse=True)
print(data)

# コスチュームの変更処理
top_ids = []
for i, (point, output) in enumerate(data):
    image_change(
        f"https://uploads.scratch.mit.edu/get_image/project/{output}_480x360.png",
        i,
    )
    top_ids.append(output)
    if i == 11:
        break
    time.sleep(3)

# --- 例: ランキングに入ったプロジェクトID一覧をScratchのリスト「ランキング」に反映 ---
# update_list("リスト名", 書き換えたいデータ)
update_list("ランキング", top_ids)