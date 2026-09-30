import sys
import os
import argparse
import subprocess
from pathlib import Path

# 确保能导入同目录下的 core
sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import GeminiTTSClient, PRESET_VOICES, SUPPORTED_MODELS, OUTPUT_DIR


def list_voices():
    print("\n=== Gemini 3.8 Flash TTS 支持的预置音色 ===")
    for v in PRESET_VOICES:
        tags = " / ".join(v["tags"])
        print(f"• {v['name']:<8} [{v['gender']}] ({tags})")
        print(f"  说明: {v['description']}")
    print("\n支持的模型:")
    for m in SUPPORTED_MODELS:
        print(f"• {m['id']:<25} - {m['name']} ({m['tag']})")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Gemini TTS Deck 命令行文本转语音工具 (CLI)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 直接朗读文本并播放
  uv run python cli.py "你好，这是 Gemini 语音合成测试。" --play

  # 指定音色并保存到文件
  uv run python cli.py "夜幕低沉，星光微亮。" -v Charon -o night.wav --play

  # 从文件读取文本并朗读
  uv run python cli.py -f article.txt -o article.wav

  # 查看所有可用音色
  uv run python cli.py --list-voices
        """
    )

    parser.add_argument("text", nargs="?", help="待转换的文本内容 (使用 '-' 可从管道标准输入读取)")
    parser.add_argument("-f", "--file", help="从指定文本文件读取待转换文本")
    parser.add_argument("-v", "--voice", default="Puck", help="选择音色 (默认: Puck, 可选: Aoede, Charon, Kore 等)")
    parser.add_argument("-m", "--model", default="gemini-3.8-flash-tts", help="选择模型 (默认: gemini-3.8-flash-tts)")
    parser.add_argument("-s", "--style", help="朗读语气/风格指令 (例如: '语气温暖亲切' 或 '新闻播音范')")
    parser.add_argument("-o", "--output", help="音频输出文件路径 (默认保存在 output/ 目录)")
    parser.add_argument("-k", "--key", help="Gemini API Key (默认读取环境变量 GEMINI_API_KEY)")
    parser.add_argument("-p", "--play", action="store_true", help="生成后自动调用系统播放器播放音频 (支持 macOS / Windows / Linux)")
    parser.add_argument("--list-voices", action="store_true", help="列出所有可用的音色与模型")

    args = parser.parse_args()

    if args.list_voices:
        list_voices()
        return

    # 获取输入文本
    content = ""
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"错误: 文件未找到: {args.file}", file=sys.stderr)
            sys.exit(1)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
    elif args.text == "-":
        content = sys.stdin.read().strip()
    elif args.text:
        content = args.text.strip()

    if not content:
        print("错误: 请提供待转换的文本或使用 -f 指定文件，输入 --help 查看使用帮助。", file=sys.stderr)
        sys.exit(1)

    print(f"[*] 准备转换文本 (共 {len(content)} 字符)...")
    print(f"[*] 选用模型: {args.model}")
    print(f"[*] 选用音色: {args.voice}")

    client = GeminiTTSClient(api_key=args.key)

    try:
        result = client.generate_speech_sync(
            text=content,
            voice=args.voice,
            model=args.model,
            style_prompt=args.style,
            custom_api_key=args.key,
            output_filename=args.output
        )

        output_path = OUTPUT_DIR / result["filename"]
        mp3_path = OUTPUT_DIR / result["mp3_filename"]

        # 如果用户指定了 .mp3 输出文件
        if args.output and args.output.endswith(".mp3"):
            import shutil
            shutil.copyfile(mp3_path, args.output)
            final_play_path = Path(args.output)
            print(f"\n[✓] 语音合成与 MP3 转码成功!")
            print(f"    导出文件: {args.output}")
        else:
            final_play_path = output_path
            print(f"\n[✓] 语音合成成功!")
            print(f"    WAV 路径: {output_path} ({result['size_kb']} KB)")
            if mp3_path.exists():
                print(f"    MP3 路径: {mp3_path} ({result.get('mp3_size_kb', 0)} KB)")

        # 全平台播放支持 (macOS / Windows / Linux)
        if args.play:
            print("[*] 正在播放音频 (按 Ctrl+C 可停止)...")
            try:
                if sys.platform == "darwin":
                    subprocess.run(["afplay", str(final_play_path)], check=True)
                elif sys.platform == "win32":
                    os.startfile(str(final_play_path))
                else:
                    import shutil
                    for player in ["xdg-open", "paplay", "aplay"]:
                        if shutil.which(player):
                            subprocess.run([player, str(final_play_path)], check=True)
                            break
                    else:
                        print(f"提示: 请使用播放器打开音频文件播放: {final_play_path}")
            except KeyboardInterrupt:
                print("\n[*] 播放已中断")
            except Exception as pe:
                print(f"提示: 播放音频失败: {pe}")

    except Exception as e:
        print(f"\n[✗] 语音合成失败: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
