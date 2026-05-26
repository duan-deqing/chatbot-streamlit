"""辅助函数工具模块"""

import datetime
import streamlit as st
from config import PAGE_CONFIG


def configure_page():
    """配置页面"""
    st.set_page_config(**PAGE_CONFIG)


def get_time_category(created_at: datetime.datetime) -> str:
    """根据创建时间返回时间分类标签
    
    Args:
        created_at: 对话创建时间
        
    Returns:
        分类标签字符串
    """
    now = datetime.datetime.now()
    delta = now - created_at

    if delta.days < 1:
        return "今天"
    elif delta.days < 3:
        return "3天内"
    elif delta.days < 7:
        return "7天内"
    elif delta.days < 30:
        return "30天内"
    else:
        return f"{created_at.year}年{created_at.month}月"