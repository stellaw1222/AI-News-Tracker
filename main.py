import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import tracker
from streamlit_autorefresh import st_autorefresh

# Page Config
st.set_page_config(
    page_title="AI动态追踪",
    page_icon="🤖",
    layout="wide",
)

# Custom Styling
st.markdown("""
    <style>
    .stApp {
        background-color: #f8f9fa;
    }
    .news-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
        border-left: 5px solid #007bff;
        transition: transform 0.2s ease-in-out;
    }
    .news-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    }
    .news-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    .news-meta {
        font-size: 0.875rem;
        color: #6c757d;
        margin-bottom: 1rem;
    }
    .news-summary {
        font-size: 1rem;
        color: #4a4a4a;
        line-height: 1.6;
    }
    .badge {
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-right: 8px;
    }
    .badge-sv { background-color: #e3f2fd; color: #0d47a1; }
    .badge-dom { background-color: #fce4ec; color: #880e4f; }
    .badge-launch { background-color: #e8f5e9; color: #1b5e20; }
    .badge-early { background-color: #fff3e0; color: #e65100; }
    .badge-official { background-color: #e0f7fa; color: #006064; border: 1px solid #00acc1; }
    .badge-opensource { background-color: #f3e5f5; color: #4a148c; border: 1px solid #ce93d8; }
    .badge-community { background-color: #fff3e0; color: #e65100; border: 1px solid #ffcc80; }
    .tag {
        display: inline-block;
        padding: 2px 8px;
        margin-right: 4px;
        margin-bottom: 4px;
        border-radius: 12px;
        font-size: 0.75rem;
        background-color: #f0f0f0;
        color: #555;
        border: 1px solid #ddd;
    }
    .hot-high { color: #d32f2f; font-weight: bold; }
    .hot-med { color: #f57c00; font-weight: bold; }
    .hot-low { color: #757575; }
    </style>
""", unsafe_allow_html=True)

# App Logic
def main():
    st.title("AI动态追踪")
    st.subheader("Capturing global AI product trends in real-time.")

    # Sidebar
    st.sidebar.header("📊 系统状态 (System Status)")
    
    # Live Indicator
    st.sidebar.markdown("""
        <div style="display: flex; align-items: center;">
            <div style="width: 10px; height: 10px; background-color: #28a745; border-radius: 50%; margin-right: 8px; animation: pulse 1.5s infinite;"></div>
            <span style="color: #28a745; font-weight: bold;">正在实时追踪全球 AI 动态...</span>
        </div>
        <style>
            @keyframes pulse {
                0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.7); }
                70% { transform: scale(1); box-shadow: 0 0 0 5px rgba(40, 167, 69, 0); }
                100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(40, 167, 69, 0); }
            }
        </style>
    """, unsafe_allow_html=True)
    
    # 1. 最近更新时间 (Last Update Time)
    last_update_placeholder = st.sidebar.empty()
    
    # 2. 近 7 天新增动态数 (Metrics)
    metrics_placeholder = st.sidebar.empty()
    
    # 3. 刷新/更新按钮 (Refresh Button)
    if st.sidebar.button("🔄 立即刷新数据", use_container_width=True):
        st.cache_data.clear()
        with st.spinner("正在同步全球 AI 信源..."):
            # Simulate a small delay for "liveness" effect
            import time
            time.sleep(1)
        st.sidebar.success("✅ 数据已同步至最新")
    
    # Auto-refresh every 5 minutes (300,000 milliseconds)
    st_autorefresh(interval=300 * 1000, key="data_refresh")
    
    st.sidebar.markdown("---")
    
    # 4. 数据源列表 (Data Sources List)
    with st.sidebar.expander("🌐 正在追踪的信源列表", expanded=False):
        for region, sources in tracker.SOURCES.items():
            st.markdown(f"**{region}**")
            for name in sources.keys():
                st.markdown(f"- {name}")

    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ 筛选设置")
    region_filter = st.sidebar.multiselect(
        "地区筛选",
        ["海外", "国内"],
        default=["海外", "国内"]
    )
    
    time_filter = st.sidebar.selectbox(
        "时间范围",
        ["Last 24 Hours", "Last 3 Days", "Last 7 Days", "All Time"],
        index=2
    )
    
    # Load Data
    @st.cache_data(ttl=300) # Data expires every 5 minutes
    def get_data():
        return tracker.fetch_news()

    with st.spinner("Fetching latest AI news..."):
        df = get_data()
        now_time = datetime.now().strftime('%H:%M:%S')
        last_update_placeholder.markdown(f"**上次同步时间**: `{now_time}`")
        
        # Calculate metric for last 7 days
        seven_days_ago = datetime.now() - timedelta(days=7)
        new_count = len(df[df['published'] > seven_days_ago])
        metrics_placeholder.metric("📅 近 7 天新增动态", f"{new_count} 条", delta="+新发布")

    if df.empty:
        st.warning("No news found. Please check your internet connection or the source URLs.")
        return

    # Filter Logic
    filtered_df = df[df['region'].isin(region_filter)].copy()
    
    # Time filtering
    now = datetime.now()
    if time_filter == "Last 24 Hours":
        filtered_df = filtered_df[filtered_df['published'] > (now - timedelta(days=1))]
    elif time_filter == "Last 3 Days":
        filtered_df = filtered_df[filtered_df['published'] > (now - timedelta(days=3))]
    elif time_filter == "Last 7 Days":
        filtered_df = filtered_df[filtered_df['published'] > (now - timedelta(days=7))]
    
    if filtered_df.empty:
        st.info("No news found for the selected filters. Try broadening your time range.")
        return

    # Main Dashboard
    col1, col2 = st.columns([1, 0.01]) # Adjust columns to use mostly full width for news

    with col1:
        st.markdown("### 📰 精选信号 (Filtered Signals)")
        for idx, row in filtered_df.iterrows():
            region_badge = "badge-sv" if row['region'] == "海外" else "badge-dom"
            
            # Source Type Badge
            source_type = row.get('source_type', 'Community')
            if source_type == "Official":
                st_class = "badge-official"
                st_icon = "📢"
            elif source_type == "Open Source":
                st_class = "badge-opensource"
                st_icon = "📦"
            else:
                st_class = "badge-community"
                st_icon = "👥"
            
            # Hot Level
            hot_level = row.get('hot_level', '低')
            hot_class = "hot-high" if hot_level == "高" else ("hot-med" if hot_level == "中" else "hot-low")
            hot_icon = "🔥" if hot_level == "高" else ("⚡" if hot_level == "中" else "🧊")
            
            # Product Directions
            directions = row.get('product_direction', [])
            if isinstance(directions, str): directions = [directions] # Handle legacy
            tags_html = "".join([f'<span class="tag">{d}</span>' for d in directions])

            st.markdown(f"""
                <div class="news-card">
                    <div class="news-title">
                        <a href="{row['link']}" target="_blank" style="text-decoration: none; color: inherit;">{row['title']}</a>
                    </div>
                    <div class="news-meta">
                        <span class="badge {region_badge}">{row['region']}</span>
                        <span class="badge {st_class}">{st_icon} {source_type}</span>
                        <span class="{hot_class}">{hot_icon} 热度: {hot_level}</span>
                        <span style="margin-left: 10px; color: #999;">{row['source']}</span> | 
                        <span>{row['published'].strftime('%m-%d %H:%M')}</span>
                    </div>
                    <div style="margin-bottom: 8px;">
                        {tags_html}
                    </div>
                    <div class="news-summary">
                        {row['summary'][:300]}...
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with col2:
        st.write("") # Empty placeholder

if __name__ == "__main__":
    main()
