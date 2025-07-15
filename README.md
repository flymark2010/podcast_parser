

## 目录结构

- htmls：从 coze 空间下载的播客 html 源文件
- jsons: 从 htmls 中解析出来，并用说话人转换点检测模型检测出每句话的转换点

## 快速开始

1. 更新环境

```bash
pip install uv
uv sync
```

2. 生成文章

```bash
uv run article.py
```