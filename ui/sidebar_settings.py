"""设置弹窗模块

使用 Streamlit 原生 st.dialog 实现设置弹窗。
状态管理：sidebar 中设置按钮将 show_settings 置为 True，
render_settings() 检测到 True 时弹出对话框，渲染完成后立即复位为 False，
避免下一次 rerun（如点击对话卡片）时重复弹出。
"""

import streamlit as st

@st.dialog("设置", width="large")
def settings_dialog():
    """设置弹窗，占屏幕宽度约 50%"""
    # 覆盖 st.dialog 默认宽度，使其撑开至 65vw
    st.markdown("""
    <style>
    [data-testid="stDialog"] > div > div {
        width: 65vw !important;
        height: 93vh !important;
        max-width: 80vw !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.write("设置页面内容区域")
    st.caption("可在此处添加模型参数、主题切换等配置项")

    if st.button("关闭", use_container_width=True):
        st.session_state.show_settings = False
        st.rerun()

def render_settings():
    """渲染设置弹窗入口
    
    由 app.py 在每次 rerun 时调用。
    仅在 show_settings 为 True 时弹出 st.dialog，
    并立即复位 show_settings，防止状态泄漏导致重复弹出。
    """
    if st.session_state.get("show_settings", False):
        settings_dialog()
        st.session_state.show_settings = False