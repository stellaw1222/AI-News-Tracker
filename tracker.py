import feedparser
import pandas as pd
from datetime import datetime
import time
import requests
from bs4 import BeautifulSoup

# RSS Sources optimized for specific signals
SOURCES = {
    "Silicon Valley": {
        "OpenAI News": "https://openai.com/news/rss.xml",
        "Google AI Blog": "http://googleaiblog.blogspot.com/atom.xml",
        "Anthropic News": "https://www.anthropic.com/index.xml",
        "GitHub Trending": "https://mrss.dokyme.com/github/trending/daily/all",
        "Product Hunt": "https://www.producthunt.com/feed",
        "Hacker News": "https://news.ycombinator.com/rss",
    },
    "Domestic (China)": {
        "Baidu Intelligent Cloud": "https://cloud.baidu.com/doc/WENXINWORKSHOP/index.html", # Placeholder for actual RSS if available, otherwise use a news aggregator for Baidu
        "Aliyun Tongyi": "https://developer.aliyun.com/rss/article?type=2", # General Aliyun feed, might need filtering
        "Zhipu AI": "https://www.zhipuai.cn/news", # Placeholder
        "ByteDance Seed": "https://seed.bytedance.com/", # Placeholder
        # Since specific official blogs for Chinese companies often lack RSS, we use high-quality aggregators with filters
        "36Kr (Baidu/Ali/Zhipu/ByteDance)": "https://36kr.com/feed", 
        "QbitAI (Domestic AI)": "https://www.qbitai.com/feed",
    }
}

# Signal Keywords
SIGNAL_KEYWORDS = {
    "Launch": ["launch", "release", "announcing", "introducing", "v1", "v2", "available", "发布", "上线", "正式推出", "正式上线", "面世", "公测", "开放"],
    "Early Signal": ["show hn", "new tool", "startup", "alpha", "beta", "demo", "pre-seed", "seed", "trending", "github", "初创", "起步", "内测", "演示"],
    "Domestic Dynamic": ["百度", "文心", "千帆", "阿里", "通义", "灵码", "智谱", "chatglm", "字节", "豆包", "seed", "大模型", "国产"]
}

def is_valid_signal(title, summary, region, source_name):
    text = (title + " " + summary).lower()
    
    # Always accept from official sources (High Signal)
    if "OpenAI" in source_name or "Google" in source_name or "Anthropic" in source_name:
        return True
    
    # Domestic Specific Logic
    if region == "Domestic (China)":
        # If it's a general aggregator like 36Kr/QbitAI, strictly filter for the requested companies
        if "36Kr" in source_name or "QbitAI" in source_name:
            return any(kw in text for kw in SIGNAL_KEYWORDS["Domestic Dynamic"])
        return True # Assume other specific domestic sources are valid if we found them
    
    # GitHub Trending is always an early signal
    if "GitHub" in source_name:
        return True
        
    # For general aggregators (PH, HN), use strict signal keywords
    return any(kw in text for kw in SIGNAL_KEYWORDS["Launch"]) or \
           any(kw in text for kw in SIGNAL_KEYWORDS["Early Signal"])

# Tagging Logic
TAG_RULES = {
    "Product_Direction": {
        "Agent": ["agent", "autonomous", "智能体", "copilot", "assistant", "auto-gpt", "babyagi"],
        "Coding": ["code", "coding", "copilot", "cursor", "devin", "ide", "programming", "代码", "编程", "补全"],
        "Multi-modal": ["multi-modal", "vision", "audio", "speech", "image", "multimodal", "多模态", "视觉", "语音"],
        "Video": ["video", "sora", "runway", "pika", "luma", "generation", "视频", "生成"],
        "Enterprise": ["enterprise", "business", "b2b", "workflow", "efficiency", "slack", "teams", "企业", "办公", "效率", "协同"],
        "Search": ["search", "rag", "retrieval", "perplexity", "bing", "google", "搜索", "检索"]
    },
    "Source_Type": {
        "Official": ["OpenAI", "Google", "Anthropic", "Baidu", "Aliyun", "Zhipu", "ByteDance", "Official", "Blog"],
        "Open Source": ["GitHub", "Hacker News", "Open Source", "Repo", "Library", "开源"],
        "Community": ["Product Hunt", "Reddit", "Twitter", "Indie Hacker"]
    }
}

def analyze_tags(entry, source_name, region):
    text = (entry.title + " " + entry.get('summary', '')).lower()
    tags = {
        "Region": "国内" if region == "Domestic (China)" else "海外",
        "Source_Type": "社区", # Default
        "Product_Direction": [],
        "Hot_Level": "低" # Default
    }
    
    # 1. Source Type
    for s_type, keywords in TAG_RULES["Source_Type"].items():
        # Check source name first
        if any(kw.lower() in source_name.lower() for kw in keywords):
            tags["Source_Type"] = s_type
            break
        # Fallback to text check for "Open Source"
        if s_type == "Open Source" and "open source" in text:
            tags["Source_Type"] = "Open Source"

    # 2. Product Direction
    for direction, keywords in TAG_RULES["Product_Direction"].items():
        if any(kw in text for kw in keywords):
            tags["Product_Direction"].append(direction)
    if not tags["Product_Direction"]:
        tags["Product_Direction"].append("General AI")

    # 3. Hot Level (Heuristic)
    # Official news is always High
    if tags["Source_Type"] == "Official":
        tags["Hot_Level"] = "高"
    # GitHub Trending is High
    elif "GitHub" in source_name:
         tags["Hot_Level"] = "高"
    # Keywords indicating major impact
    elif any(kw in text for kw in ["major", "breakthrough", "sota", "revolutionary", "重磅", "炸裂", "史诗级"]):
        tags["Hot_Level"] = "高"
    # Launch keywords are Medium
    elif any(kw in text for kw in SIGNAL_KEYWORDS["Launch"]):
        tags["Hot_Level"] = "中"
        
    return tags

def fetch_news():
    all_news = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    for region, region_sources in SOURCES.items():
        for source_name, url in region_sources.items():
            try:
                print(f"Fetching {source_name}...")
                
                # Special handling for non-RSS placeholders or difficult feeds would go here
                # For now, we assume valid RSS/Atom feeds or aggregators
                
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code != 200: continue
                
                feed = feedparser.parse(response.content)
                if not feed.entries: continue
                
                for entry in feed.entries[:20]:
                    published = entry.get('published_parsed') or entry.get('updated_parsed')
                    pub_date = datetime.fromtimestamp(time.mktime(published)) if published else datetime.now()
                    
                    summary = entry.get('summary', entry.get('description', ''))
                    if summary:
                        soup = BeautifulSoup(summary, "html.parser")
                        summary = soup.get_text()[:300]
                    
                    # Apply Signal Filtering
                    if is_valid_signal(entry.title, summary, region, source_name):
                        # Analyze Tags
                        tags = analyze_tags(entry, source_name, region)
                        
                        # Flatten tags for DataFrame
                        all_news.append({
                            "title": entry.title,
                            "link": entry.link,
                            "source": source_name,
                            "region": tags["Region"], # Use tagged region
                            "published": pub_date,
                            "summary": summary,
                            "source_type": tags["Source_Type"],
                            "product_direction": tags["Product_Direction"],
                            "hot_level": tags["Hot_Level"]
                        })
            except Exception as e:
                print(f"Error fetching {source_name}: {e}")
                
    df = pd.DataFrame(all_news)
    if not df.empty:
        df = df.sort_values(by="published", ascending=False).drop_duplicates(subset=['title'])
    return df

if __name__ == "__main__":
    news = fetch_news()
    print(news.head())
