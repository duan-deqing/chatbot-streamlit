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
            background-color: transparent;
            border: none;
            border-radius: 8px;
            padding: 6px 12px;
            margin: 0;
            text-align: left;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            height: auto;
            min-height: unset;
            line-height: 1.4;
            font-size: 14px;
            color: #555;
            width: 100%;
            display: block;
        }
        .stSidebar .stButton button[kind="secondary"]:hover {
            background-color: #f0f0f0;
            color: #333;
        }
        
        /* 侧边栏按钮卡片样式 - 选中状态 */
        .stSidebar .stButton button[kind="primary"] {
            background-color: #e8e8e8;
            border: none;
            border-radius: 8px;
            padding: 6px 12px;
            margin: 0;
            text-align: left;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            height: auto;
            min-height: unset;
            line-height: 1.4;
            font-size: 14px;
            color: #222;
            font-weight: 500;
            width: 100%;
            display: block;
        }
        .stSidebar .stButton button[kind="primary"]:hover {
            background-color: #e0e0e0;
        }
        
        /* 调整chat input和file uploader间距 */
        .stFileUploader {
            margin-bottom: 0.5rem;
        }
        /* 优化聊天区域显示 */
        .stChatMessage {
            padding: 0.75rem 1rem;
        }

        /* 新建对话按钮 - 通过标记元素定位并添加SVG图标 */
        .stSidebar [data-testid="stMarkdownContainer"]:has(.nc-marker) + .stButton button {
            display: flex !important;
            align-items: center;
            justify-content: center !important;
            gap: 6px;
            padding: 7px 12px !important;
            border-radius: 8px;
            border: none !important;
            background: #eef1ff !important;
            color: #4d6bfe !important;
            font-size: 14px;
            line-height: 1.5;
            white-space: nowrap;
            min-height: unset !important;
            height: auto !important;
        }
        .stSidebar [data-testid="stMarkdownContainer"]:has(.nc-marker) + .stButton button:hover {
            background: #dce0fa !important;
        }
        .stSidebar [data-testid="stMarkdownContainer"]:has(.nc-marker) + .stButton button:disabled {
            opacity: 0.4;
        }
        .stSidebar [data-testid="stMarkdownContainer"]:has(.nc-marker) + .stButton button:disabled:hover {
            background: #eef1ff !important;
        }
        .stSidebar [data-testid="stMarkdownContainer"]:has(.nc-marker) + .stButton button::before {
            content: "";
            display: inline-block;
            width: 16px;
            height: 16px;
            flex-shrink: 0;
            opacity: 0.6;
            background-color: currentColor;
            mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cline x1='12' y1='5' x2='12' y2='19'/%3E%3Cline x1='5' y1='12' x2='19' y2='12'/%3E%3C/svg%3E");
            -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cline x1='12' y1='5' x2='12' y2='19'/%3E%3Cline x1='5' y1='12' x2='19' y2='12'/%3E%3C/svg%3E");
            mask-size: contain;
            -webkit-mask-size: contain;
            mask-repeat: no-repeat;
            -webkit-mask-repeat: no-repeat;
        }
    </style>
    """, unsafe_allow_html=True)