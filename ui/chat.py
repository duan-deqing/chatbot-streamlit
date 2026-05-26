"""聊天界面UI模块"""

import streamlit as st
from models import Conversation, ConversationManager
from services.ai_service import AIService
from services.file_service import FileService
from config import UPLOAD_CONFIG, TITLE_MAX_LENGTH


def render_chat_interface(conv_manager: ConversationManager, api_key: str):
    """渲染聊天界面
    
    Args:
        conv_manager: 对话管理器
        api_key: API密钥
    """
    current_conv = conv_manager.get_current()
    if current_conv is None:
        st.error("当前对话不存在，请刷新页面或新建对话。")
        st.stop()
    
    st.title("💬 AI 聊天助手")
    st.caption(f"当前对话：{current_conv.title}")
    
    # 展示历史消息
    for msg in current_conv.messages:
        with st.chat_message(msg.role):
            st.markdown(msg.content)
    
    # 文件上传组件
    uploaded_file = st.file_uploader(
        "📎 上传文件 (支持 .txt, .csv, .json, .py 等文本文件)",
        type=UPLOAD_CONFIG["allowed_types"],
        key=UPLOAD_CONFIG["key"],
        label_visibility="collapsed"
    )
    
    # 显示已上传的文件名提示
    if uploaded_file is not None:
        st.info(f"📄 已上传: `{uploaded_file.name}`，将在发送消息时一并处理。")
    
    # 聊天输入框
    user_input = st.chat_input("输入消息...")
    
    # 处理用户输入
    if user_input:
        _process_user_input(
            user_input, uploaded_file, current_conv, api_key, conv_manager
        )


def _process_user_input(
    user_input: str,
    uploaded_file,
    current_conv: Conversation,
    api_key: str,
    conv_manager: ConversationManager
):
    """处理用户输入
    
    Args:
        user_input: 用户输入
        uploaded_file: 上传的文件
        current_conv: 当前对话
        api_key: API密钥
        conv_manager: 对话管理器
    """
    full_prompt = user_input
    
    # 如果有上传文件，读取内容并合并到用户消息中
    if uploaded_file is not None:
        file_content, error = FileService.read_file(uploaded_file)
        if error:
            st.error(error)
        else:
            full_prompt = FileService.format_file_prompt(
                file_content, uploaded_file.name, user_input
            )
            # 清除文件上传器的状态
            if UPLOAD_CONFIG["key"] in st.session_state:
                del st.session_state[UPLOAD_CONFIG["key"]]
    
    # 将用户消息添加到当前对话
    current_conv.add_message("user", full_prompt)
    
    # 调用 AI 生成回复
    with st.spinner("🤔 AI 思考中..."):
        api_messages = current_conv.get_messages_for_api()
        ai_response = AIService.call_api(api_messages, api_key)
    
    # 将 AI 回复添加到对话
    current_conv.add_message("assistant", ai_response)
    
    # 更新对话标题
    current_conv.update_title_from_first_message(TITLE_MAX_LENGTH)
    
    # 刷新界面以显示新消息
    st.rerun()