"""侧边栏UI模块"""

import streamlit as st
from models import ConversationManager


def render_sidebar(conv_manager: ConversationManager) -> str:
    """渲染侧边栏
    
    Args:
        conv_manager: 对话管理器
        
    Returns:
        当前API密钥
    """
    with st.sidebar:
        st.title("🤖 AI Chat")
        
        # API Key 输入
        api_key_input = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.get("api_key", ""),
            help="输入你的 OpenAI API 密钥，用于调用 GPT 模型",
            placeholder="sk-..."
        )
        if api_key_input:
            st.session_state.api_key = api_key_input
        
        # 未填 API Key 时的提醒
        if not st.session_state.get("api_key", ""):
            st.warning("⚠️ 请在上方输入 OpenAI API Key 以开始对话")
        
        st.markdown("---")
        
        # 新建对话按钮
        if st.button("➕ 新建对话", use_container_width=True):
            conv_manager.create_conversation()
            st.rerun()
        
        st.markdown("### 📜 历史记录")
        
        # 显示所有历史对话 (最新在上方)
        for conv in conv_manager.get_all_sorted(reverse=True):
            is_active = conv.id == conv_manager.current_id
            msg_count = len(conv.messages)
            
            # 使用按钮实现卡片，通过key标识选中状态
            button_label = f"**{conv.title}**\n\n{msg_count} 条消息"
            
            if st.button(
                button_label,
                key=f"hist_{conv.id}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                if not is_active:
                    conv_manager.switch_to(conv.id)
                    st.rerun()
    
    return st.session_state.get("api_key", "")