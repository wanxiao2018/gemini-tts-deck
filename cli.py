import sys
import os
import argparse
import subprocess
from pathlib import Path

# Ensure core engine can be imported from current directory
sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import GeminiTTSClient, PRESET_VOICES, SUPPORTED_MODELS, OUTPUT_DIR


def is_zh_locale() -> bool:
    env_lang = (os.environ.get("LANG", "") + os.environ.get("LC_ALL", "")).lower()
    return "zh" in env_lang


def list_voices():
    is_zh = is_zh_locale()
    if is_zh:
        print("\n=== Gemini 3.8 Flash TTS 支持的预置音色 ===")
        for v in PRESET_VOICES:
            tags = " / ".join(v["tags"])
            print(f"• {v['name']:<8} [{v['gender']}] ({tags})")
            print(f"  说明: {v['description']}")
        print("\n支持的模型:")
        for m in SUPPORTED_MODELS:
            print(f"• {m['id']:<25} - {m['name']} ({m['tag']})")
        print()
    else:
        print("\n=== Gemini 3.8 Flash TTS Supported Preset Voices ===")
        for v in PRESET_VOICES:
            tags = " / ".join(v.get("tags_en", v["tags"]))
            gender = v.get("gender_en", v["gender"])
            desc = v.get("description_en", v["description"])
            print(f"• {v['name']:<8} [{gender}] ({tags})")
            print(f"  Description: {desc}")
        print("\nSupported Models:")
        for m in SUPPORTED_MODELS:
            tag = m.get("tag_en", m["tag"])
            desc = m.get("description_en", m["description"])
            print(f"• {m['id']:<25} - {m['name']} ({tag})")
            print(f"  Description: {desc}")
        print()


def main():
    is_zh = is_zh_locale()
    desc = "Gemini TTS Deck 命令行文本转语音工具 (CLI)" if is_zh else "Gemini TTS Deck - Command Line Text-to-Speech CLI Tool"
    epilog = """
示例:
  # 直接朗读文本并播放
  uv run python cli.py "你好，这是 Gemini 语音合成测试。" --play

  # 指定音色并保存到文件
  uv run python cli.py "夜幕低沉，星光微亮。" -v Charon -o night.wav --play

  # 从文件读取文本并朗读
  uv run python cli.py -f article.txt -o article.wav

  # 查看所有可用音色
  uv run python cli.py --list-voices
    """ if is_zh else """
Examples:
  # Directly synthesize text and play audio
  uv run python cli.py "Hello, this is a Gemini TTS test." --play

  # Choose voice and save output
  uv run python cli.py "The stars are quiet tonight." -v Charon -o night.wav --play

  # Synthesize text from a file
  uv run python cli.py -f article.txt -o article.wav

  # List all available voices and models
  uv run python cli.py --list-voices
    """

    parser = argparse.ArgumentParser(
        description=desc,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog
    )

    if is_zh:
        parser.add_argument("text", nargs="?", help="待转换的文本内容 (使用 '-' 可从管道标准输入读取)")
        parser.add_argument("-f", "--file", help="从指定文本文件读取待转换文本")
        parser.add_argument("-v", "--voice", default="Puck", help="选择音色 (默认: Puck, 可选: Aoede, Charon, Kore 等)")
        parser.add_argument("-m", "--model", default="gemini-3.8-flash-tts", help="选择模型 (默认: gemini-3.8-flash-tts)")
        parser.add_argument("-s", "--style", help="朗读语气/风格指令 (例如: '语气温暖亲切' 或 '新闻播音范')")
        parser.add_argument("-o", "--output", help="音频输出文件路径 (默认保存在 output/ 目录)")
        parser.add_argument("-k", "--key", help="Gemini API Key (默认读取环境变量 GEMINI_API_KEY)")
        parser.add_argument("-p", "--play", action="store_true", help="生成后自动调用系统播放器播放音频 (支持 macOS / Windows / Linux)")
        parser.add_argument("--list-voices", action="store_true", help="列出所有可用的音色与模型")
    else:
        parser.add_argument("text", nargs="?", help="Text to synthesize (use '-' to read from stdin)")
        parser.add_argument("-f", "--file", help="Read input text from specified file path")
        parser.add_argument("-v", "--voice", default="Puck", help="Voice preset (default: Puck; options: Aoede, Charon, Kore, etc.)")
        parser.add_argument("-m", "--model", default="gemini-3.8-flash-tts", help="Model ID (default: gemini-3.8-flash-tts)")
        parser.add_argument("-s", "--style", help="Delivery/style instruction (e.g., 'warm and gentle tone')")
        parser.add_argument("-o", "--output", help="Audio output destination path (saved in output/ by default)")
        parser.add_argument("-k", "--key", help="Gemini API Key (defaults to GEMINI_API_KEY env var)")
        parser.add_argument("-p", "--play", action="store_true", help="Auto-play audio with system player upon completion")
        parser.add_argument("--list-voices", action="store_true", help="List all available voices and models")

    args = parser.parse_args()

    if args.list_voices:
        list_voices()
        return

    # Retrieve input text
    content = ""
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            err_msg = f"错误: 文件未找到: {args.file}" if is_zh else f"Error: File not found: {args.file}"
            print(err_msg, file=sys.stderr)
            sys.exit(1)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
    elif args.text == "-":
        content = sys.stdin.read().strip()
    elif args.text:
        content = args.text.strip()

    if not content:
        err_msg = "错误: 请提供待转换的文本或使用 -f 指定文件，输入 --help 查看使用帮助。" if is_zh else "Error: Please provide text to convert or specify a file with -f. Run with --help for details."
        print(err_msg, file=sys.stderr)
        sys.exit(1)

    prep_msg = f"[*] 准备转换文本 (共 {len(content)} 字符)..." if is_zh else f"[*] Synthesizing speech ({len(content)} chars)..."
    model_msg = f"[*] 选用模型: {args.model}" if is_zh else f"[*] Selected model: {args.model}"
    voice_msg = f"[*] 选用音色: {args.voice}" if is_zh else f"[*] Selected voice: {args.voice}"
    print(prep_msg)
    print(model_msg)
    print(voice_msg)

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

        # Handle .mp3 output destination if specified
        if args.output and args.output.endswith(".mp3"):
            import shutil
            shutil.copyfile(mp3_path, args.output)
            final_play_path = Path(args.output)
            if is_zh:
                print(f"\n[✓] 语音合成与 MP3 转码成功!")
                print(f"    导出文件: {args.output}")
            else:
                print(f"\n[✓] Speech synthesis & MP3 transcode succeeded!")
                print(f"    Exported to: {args.output}")
        else:
            final_play_path = output_path
            if is_zh:
                print(f"\n[✓] 语音合成成功!")
                print(f"    WAV 路径: {output_path} ({result['size_kb']} KB)")
                if mp3_path.exists():
                    print(f"    MP3 路径: {mp3_path} ({result.get('mp3_size_kb', 0)} KB)")
            else:
                print(f"\n[✓] Speech synthesis succeeded!")
                print(f"    WAV output: {output_path} ({result['size_kb']} KB)")
                if mp3_path.exists():
                    print(f"    MP3 output: {mp3_path} ({result.get('mp3_size_kb', 0)} KB)")

        # Cross-platform audio playback (macOS / Windows / Linux)
        if args.play:
            play_start = "[*] 正在播放音频 (按 Ctrl+C 可停止)..." if is_zh else "[*] Playing audio (Press Ctrl+C to stop)..."
            print(play_start)
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
                        hint = f"提示: 请使用播放器打开音频文件播放: {final_play_path}" if is_zh else f"Note: Please use an external audio player to open: {final_play_path}"
                        print(hint)
            except KeyboardInterrupt:
                stopped = "\n[*] 播放已中断" if is_zh else "\n[*] Playback interrupted"
                print(stopped)
            except Exception as pe:
                fail_hint = f"提示: 播放音频失败: {pe}" if is_zh else f"Note: Audio playback failed: {pe}"
                print(fail_hint)

    except Exception as e:
        err_msg = f"\n[✗] 语音合成失败: {str(e)}" if is_zh else f"\n[✗] Speech synthesis failed: {str(e)}"
        print(err_msg, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
