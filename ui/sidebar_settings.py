"""设置弹窗模块

使用 Streamlit 原生 st.dialog 实现设置弹窗，按功能区分为标签页。
API Key 配置已整合至模型配置标签页，不再单独展示。

对话框生命周期管理：
- 侧边栏「⚙️ 设置」按钮 → 生成 session token 并设置 show_settings=True
- render_settings() 检测 show_settings → 打开 st.dialog
- 内部操作（刷新检测、添加模型等）触发的 rerun 不关闭对话框
- 「确认」按钮显式关闭 → show_settings=False + rerun
- X 按钮关闭 → _dialog_active 标志检测，避免后续意外重新弹出
"""

import streamlit as st
from ui.sidebar_models import render_model_selector


@st.dialog("设置", width="large")
def settings_dialog(model_manager):
    """设置弹窗内容

    两个标签页：
    1. 模型配置：供应商/模型双级联动 + 自定义模型管理
    2. 参数设置：Temperature、MaxTokens、TopP、流式开关
    """
    # 标记对话框函数体确实执行了（用于 X 按钮检测）
    st.session_state._dialog_active = True

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

    # 确认按钮：显式关闭对话框的唯一入口
    st.divider()
    _, col_close, _ = st.columns([2, 1, 2])
    with col_close:
        if st.button("确认", key="close_settings", use_container_width=True):
            st.session_state.show_settings = False
            st.rerun()


def render_settings(model_manager):
    """对话框渲染入口（app.py 每次 rerun 时调用）

    状态机：
    ┌─────────────┐   打开设置    ┌─────────────┐
    │ show_settings│ ──────────→  │  对话框打开   │
    │   = False   │              │ _dialog_active│
    └─────────────┘              │   = True     │
          ↑                      └──────┬──────┘
          │                             │
          │  确认按钮 / X关闭             │ 内部操作 (rerun)
          │                             ↓
          └────────────────────  show_settings 不变
                                  _dialog_active=True
    """
    if not st.session_state.get("show_settings", False):
        return

    # 防止同一 session 重复弹出（X 关闭后又交互触发）
    session_id = st.session_state.get("_settings_session", "")
    if session_id == st.session_state.get("_closed_session", ""):
        return

    # 重置标记，对话框函数体执行时会设为 True
    st.session_state._dialog_active = False
    settings_dialog(model_manager)

    # X 关闭检测：函数体未执行（_dialog_active 仍为 False）说明对话框被关闭
    if st.session_state.get("show_settings", False) and not st.session_state.get("_dialog_active", False):
        st.session_state._closed_session = session_id
        st.session_state.show_settings = False