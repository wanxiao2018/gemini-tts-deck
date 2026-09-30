# 贡献指南 · Gemini TTS Deck

[English](./CONTRIBUTING.md) · [简体中文](./CONTRIBUTING_zh.md)

感谢你对 **Gemini TTS Deck** 的关注与支持！无论是提交 Bug 报告、优化文档还是开发新特性，我们都热烈欢迎来自社区的贡献。

---

## 🛠 本地开发指引

### 1. 准备环境
本项目使用极速 Python 包管理工具 [`uv`](https://github.com/astral-sh/uv)：

```bash
# 克隆代码仓库
git clone https://github.com/wanxiao2018/gemini-tts-deck.git
cd gemini-tts-deck

# 创建并同步虚拟环境
uv venv .venv
uv pip install -e .
```

### 2. 配置密钥
复制配置示例文件并填入您的 API Key：
```bash
cp .env.example .env
# 编辑 .env 文件填入 GEMINI_API_KEY
```

### 3. 本地启动与测试
- **Web 控制台 (Deck)**：
  ```bash
  # macOS / Linux / 命令行
  uv run python run.py

  # Windows 用户（一键双击）
  直接双击运行 run.bat
  ```
- **命令行发声测试**：
  ```bash
  uv run python cli.py "你好，欢迎使用 Gemini TTS Deck。" --play
  ```

---

## 🤝 贡献流程 (Pull Request)

1. **Fork** 本代码仓库到你的 GitHub 账号；
2. 基于 `main` 分支拉取新的特性分支：`git checkout -b feature/your-feature-name`；
3. 提交修改并书写清晰的 Commit 信息：
   - `feat:` 新增功能
   - `fix:` 修复缺陷
   - `docs:` 文档调整
   - `refactor:` 代码重构
4. 推送分支：`git push origin feature/your-feature-name`；
5. 在 GitHub 上发起 Pull Request 并详细描述变更内容。

---

## 💡 欢迎的贡献方向

- [ ] 多角色台词对话（Multi-speaker dialogue）排版与生成
- [ ] Docker / Docker-Compose 一键部署方案
- [ ] 更多拟真微表情标签与提示词预设
- [ ] 界面多语言国际化切换支持 (i18n)
