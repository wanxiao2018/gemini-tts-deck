import sys
import time
import threading
import webbrowser
from pathlib import Path

# 添加当前目录到 sys.path
APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))

import uvicorn


def open_browser(url: str, delay: float = 1.0):
    """延迟并在后台自动打开默认浏览器"""
    time.sleep(delay)
    print(f"\n[*] 正在为您在浏览器中打开应用: {url}")
    webbrowser.open(url)


def main():
    host = "127.0.0.1"
    port = 8000
    url = f"http://{host}:{port}"

    print("=" * 60)
    print("  Gemini 3.8 Flash 文本转语音 (TTS) Studio")
    print("=" * 60)
    print(f"[*] 服务地址: {url}")
    print("[*] 正在启动本地 Web 界面...")

    # 启动后台线程打开浏览器
    threading.Thread(target=open_browser, args=(url, 1.2), daemon=True).start()

    # 启动 FastAPI 服务
    try:
        uvicorn.run("app:app", host=host, port=port, reload=False, log_level="info")
    except KeyboardInterrupt:
        print("\n[*] 服务已停止。")


if __name__ == "__main__":
    main()
