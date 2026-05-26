"""辅助函数工具模块"""

import streamlit as st
from config import PAGE_CONFIG


def configure_page():
    """配置页面"""
    st.set_page_config(**PAGE_CONFIG)