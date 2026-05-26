"""UI样式模块"""

import streamlit as st


def load_custom_css():
    """加载自定义CSS样式"""
    st.markdown("""
    <style>
        /* 隐藏Streamlit默认的导航栏 */
        div[data-testid="stSidebarNav"] {display: none;}
        
        /* 侧边栏按钮卡片样式 - 未选中状态 */
        .stSidebar .stButton button[kind="secondary"] {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 12px;
            padding: 12px 14px;
            margin: 6px 0;
            text-align: left;
            white-space: normal;
            word-break: break-word;
            height: auto;
            min-height: 70px;
            color: #333;
        }
        .stSidebar .stButton button[kind="secondary"]:hover {
            background-color: #e9ecef;
            border-color: #dee2e6;
        }
        
        /* 侧边栏按钮卡片样式 - 选中状态 */
        .stSidebar .stButton button[kind="primary"] {
            background-color: #e3f2fd;
            border: 1px solid #90caf9;
            border-radius: 12px;
            padding: 12px 14px;
            margin: 6px 0;
            text-align: left;
            white-space: normal;
            word-break: break-word;
            height: auto;
            min-height: 70px;
            color: #1565c0;
            font-weight: 500;
        }
        
        /* 调整chat input和file uploader间距 */
        .stFileUploader {
            margin-bottom: 0.5rem;
        }
        /* 优化聊天区域显示 */
        .stChatMessage {
            padding: 0.75rem 1rem;
        }
    </style>
    """, unsafe_allow_html=True)