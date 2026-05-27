"""设置弹窗模块

使用 Streamlit 原生 st.dialog 实现设置弹窗，按功能区分为标签页。
API Key 配置已整合至模型配置标签页，不再单独展示。
"""

import streamlit as st
from ui.sidebar_models import render_model_selector


@st.dialog("设置", width="large")
def settings_dialog(model_manager):
    """设置弹窗
    
    Args:
        model_manager: 模型管理器实例
    """
    st.markdown("""
    <style>
    [data-testid="stDialog"] > div > div {
        width: 65vw !important;
        max-width: 80vw !important;
    }
    </style>
    """, unsafe_allow_html=True)

    tab_model, tab_chat = st.tabs(["模型配置", "参数设置"])

    with tab_model:
        render_model_selector(model_manager)

    with tab_chat:
        st.markdown("### 模型参数")
        st.slider(
            "Temperature（创造性）",
            min_value=0.0,
            max_value=2.0,
            value=st.session_state.get("temperature", 0.7),
            step=0.05,
            key="temperature",
            help="越高越有创造性，越低越保守。"
        )
        st.slider(
            "Max Tokens（最大输出长度）",
            min_value=100,
            max_value=4096,
            value=st.session_state.get("max_tokens", 1000),
            step=100,
            key="max_tokens",
            help="单次回复的最大 token 数。"
        )
        st.slider(
            "Top P（核采样）",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.get("top_p", 0.9),
            step=0.05,
            key="top_p",
            help="累积概率阈值，1.0 表示考虑所有词。"
        )

        st.divider()
        st.markdown("### 输出模式")
        st.checkbox(
            "🔄 启用流式输出",
            value=st.session_state.get("enable_streaming", True),
            key="enable_streaming",
            help="开启后 AI 回复会逐字显示，带来更快的首字响应体验。"
        )

    st.divider()
    _, col_close, _ = st.columns([2, 1, 2])
    with col_close:
        if st.button("确认", key="close_settings", use_container_width=True):
            st.session_state.show_settings = False
            st.rerun()


def render_settings(model_manager):
    """渲染设置弹窗入口
    
    由 app.py 在每次 rerun 时调用。
    仅在 show_settings 为 True 时弹出 st.dialog，
    并立即复位 show_settings，防止状态泄漏导致重复弹出。
    
    Args:
        model_manager: 模型管理器实例
    """
    if st.session_state.get("show_settings", False):
        settings_dialog(model_manager)
        st.session_state.show_settings = False