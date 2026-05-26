"""设置弹窗模块"""

import streamlit as st


@st.dialog("设置", width="large")
def settings_dialog():
    """设置弹窗，占屏幕宽度 50%"""
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

    # if st.button("关闭", use_container_width=True):
    #     st.session_state.show_settings = False
    #     st.rerun()


def render_settings():
    """渲染设置弹窗"""
    if st.session_state.get("show_settings", False):
        settings_dialog()