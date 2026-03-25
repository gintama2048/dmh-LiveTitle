import requests
import os
import sys

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://live.bilibili.com/',
}

LAST_TITLE_FILE = "last_title.txt"

def get_real_room_id(short_id):
    url = f"https://api.live.bilibili.com/room/v1/Room/room_init?id={short_id}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()
    if data['code'] == 0:
        return str(data['data']['room_id'])
    else:
        raise Exception(f"获取真实房间号失败: {data}")

def get_live_title(room_id):
    url = f"https://api.live.bilibili.com/room/v1/Room/get_info?room_id={room_id}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()
    if data['code'] == 0:
        return data['data']['title']
    else:
        # 尝试转换短号
        if room_id.isdigit() and len(room_id) <= 10:
            real_id = get_real_room_id(room_id)
            return get_live_title(real_id)
        else:
            raise Exception(f"获取标题失败: {data}")

def send_notification(title, content):
    send_key = os.environ.get('SEND_KEY')
    if not send_key:
        raise Exception("未设置 SEND_KEY 环境变量")
    url = f"https://sctapi.ftqq.com/{send_key}.send"
    data = {"title": title, "desp": content}
    resp = requests.post(url, data=data)
    resp.raise_for_status()
    print("推送成功")

def read_last_title():
    """读取上次保存的标题，文件不存在则返回 None"""
    if os.path.exists(LAST_TITLE_FILE):
        with open(LAST_TITLE_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return None

def write_last_title(title):
    """写入新标题到文件"""
    with open(LAST_TITLE_FILE, 'w', encoding='utf-8') as f:
        f.write(title)

def main():
    room_id = os.environ.get('ROOM_ID')
    if not room_id:
        raise Exception("未设置 ROOM_ID 环境变量")
    print(f"使用房间号: {room_id}")

    # 获取当前标题
    current_title = get_live_title(room_id)
    print(f"当前标题: {current_title}")

    # 读取上次标题
    last_title = read_last_title()
    print(f"上次标题: {last_title}")

    # 判断是否变化
    if last_title == current_title:
        print("标题未变化，不发送通知")
        sys.exit(0)  # 正常退出，不更新文件

    # 标题变化：发送通知，并更新文件
    print("标题已变化，发送通知并更新记录")
    send_notification("B站直播间标题变化", f"新标题：{current_title}")
    write_last_title(current_title)
    # 注意：Git 提交将由 GitHub Actions 的后续步骤完成

if __name__ == "__main__":
    main()
