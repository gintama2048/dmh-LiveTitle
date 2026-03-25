import requests
import os

def get_real_room_id(short_id):
    """通过短号获取真实房间号"""
    url = f"https://api.live.bilibili.com/room/v1/Room/room_init?id={short_id}"
    resp = requests.get(url).json()
    if resp['code'] == 0:
        return str(resp['data']['room_id'])
    else:
        raise Exception(f"获取真实房间号失败: {resp}")

def get_live_title(room_id):
    """获取直播间标题，支持短号或长号"""
    url = f"https://api.live.bilibili.com/room/v1/Room/get_info?room_id={room_id}"
    resp = requests.get(url).json()
    if resp['code'] == 0:
        return resp['data']['title']
    
    # 如果失败，尝试将短号转成长号
    if room_id.isdigit() and len(room_id) <= 10:
        real_id = get_real_room_id(room_id)
        return get_live_title(real_id)
    else:
        raise Exception(f"获取标题失败: {resp}")

def send_notification(title, content):
    """发送到Server酱"""
    send_key = os.environ.get('SEND_KEY')
    if not send_key:
        raise Exception("未设置 SEND_KEY 环境变量")
    url = f"https://sctapi.ftqq.com/{send_key}.send"
    data = {"title": title, "desp": content}
    resp = requests.post(url, data=data)
    if resp.status_code != 200:
        raise Exception(f"推送失败: {resp.text}")

def main():
    room_id = os.environ.get('ROOM_ID')
    if not room_id:
        raise Exception("未设置 ROOM_ID 环境变量")
    
    title = get_live_title(room_id)
    send_notification("B站直播间标题", f"当前标题：{title}")
    print("发送成功")

if __name__ == "__main__":
    main()
