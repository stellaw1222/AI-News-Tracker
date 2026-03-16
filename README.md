# AI Dynamic Tracker 

一款旨在捕捉国内外 AI 产品最新动态的小工具，专为“捕捉硅谷一手信息”和“国内应用落地”而设计。

## 技术栈
- **Frontend**: Streamlit (Python)
- **Data Engine**: RSS Aggregation (feedparser)
- **Styling**: Custom CSS (Tailwind Style)
- **Language**: Python 3.13+

## 快速启动
1. 安装依赖:
   ```bash
   pip install streamlit feedparser pandas requests beautifulsoup4
   ```
2. 运行应用:
   ```bash
   streamlit run main.py
   ```

## 核心文件
- `main.py`: Streamlit 应用主逻辑与 UI。
- `tracker.py`: 数据抓取与 RSS 处理引擎。
- `requirements.txt`: 项目依赖列表。
