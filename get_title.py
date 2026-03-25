import requests
import os
import json

# 设置通用请求头，模拟浏览器
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://live.bilibili.com/',
}

def get_real_room_id(short_id):
    """通过短号获取真实房间号"""
    url = f"https://api.live.bilibili.com/room/v1/Room/room_init?id={short_id}"
    try:
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()  # 检查HTTP状态码
        data = resp.json()
        if data['code'] == 0:
            return str(data['data']['room_id'])
        else:
            raise Exception(f"获取真实房间号失败: {data}")
    except Exception as e:
        # 打印响应内容便于调试
        print(f"获取真实房间号出错: {e}")
        print(f"响应内容: {resp.text[:500]}")
        raise

def get_live_title(room_id):
    """获取直播间标题，支持短号或长号"""
    # 尝试直接用传入的 room_id 请求
    url = f"https://api.live.bilibili.com/room/v1/Room/get_info?room_id={room_id}"
    try:
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        if data['code'] == 0:
            return data['data']['title']
        else:
            # 如果 code != 0，可能是短号无效，尝试转长号
            if room_id.isdigit() and len(room_id) <= 10:
                print(f"短号 {room_id} 直接请求失败，尝试转换...")
                real_id = get_real_room_id(room_id)
                return get_live_title(real_id)  # 递归用长号重试
            else:
                raise Exception(f"获取标题失败，API返回: {data}")
    except requests.exceptions.JSONDecodeError:
        print(f"API返回非JSON内容，可能被拦截。响应内容: {resp.text[:500]}")
        raise
    except Exception as e:
        print(f"请求出错: {e}")
        if 'resp' in locals():
            print(f"HTTP状态码: {resp.status_code}")
            print(f"响应内容: {resp.text[:500]}")
        raise

def send_notification(title, content):
    """发送到Server酱"""
    send_key = os.environ.get('SEND_KEY')
    if not send_key:
        raise Exception("未设置 SEND_KEY 环境变量")
    url = f"https://sctapi.ftqq.com/{send_key}.send"
    data = {"title": title, "desp": content}
    try:
        resp = requests.post(url, data=data)
        resp.raise_for_status()
        print("推送成功")
    except Exception as e:
        print(f"推送失败: {e}")
        raise

def main():
    room_id = os.environ.get('ROOM_ID')
    if not room_id:
        raise Exception("未设置 ROOM_ID 环境变量")
    print(f"使用房间号: {room_id}")

    title = get_live_title(room_id)
    print(f"获取到标题: {title}")

    send_notification("B站直播间标题", f"当前标题：{title}")

if __name__ == "__main__":
    main()
