"""侧边栏历史记录模块"""

import streamlit as st


def render_history_section(conv_manager):
    """渲染新建对话按钮、历史记录和设置按钮
    
    Args:
        conv_manager: 对话管理器
    """
    current_conv = conv_manager.get_current()
    can_create_new = current_conv is not None and len(current_conv.messages) > 0

    st.markdown(
        '<div class="nc-marker" style="display:none"></div>',
        unsafe_allow_html=True
    )

    if st.button(
        "新建对话",
        key="new_conv_btn",
        use_container_width=True,
        disabled=not can_create_new
    ):
        conv_manager.create_conversation()
        st.rerun()

    st.markdown("#### 历史记录")

    grouped = conv_manager.get_grouped_sorted()
    for category, conversations in grouped.items():
        st.markdown(f"**{category}**")
        for conv in conversations:
            is_active = conv.id == conv_manager.current_id

            if st.button(
                conv.title,
                key=f"hist_{conv.id}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                if not is_active:
                    conv_manager.switch_to(conv.id)
                    st.rerun()

    st.markdown("---")

    