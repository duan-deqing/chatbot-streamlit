"""主应用入口"""

import streamlit as st
from utils.helpers import configure_page
from utils.session import init_session_state
from ui.styles import load_custom_css
from ui.sidebar import render_sidebar
from ui.chat import render_chat_interface

# 页面配置
configure_page()

# 加载自定义CSS
load_custom_css()

# 初始化Session State
conv_manager, model_manager = init_session_state()

# 渲染侧边栏
api_key = render_sidebar(conv_manager, model_manager)

# 渲染聊天界面
render_chat_interface(conv_manager, model_manager)