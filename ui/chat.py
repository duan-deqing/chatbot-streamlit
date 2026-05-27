"""聊天界面UI模块"""

import streamlit as st
from data import Conversation, ConversationManager
from models import ModelManager
from services.ai_service import AIService
from services.file_service import FileService
from config import UPLOAD_CONFIG, TITLE_MAX_LENGTH


def render_chat_interface(conv_manager: ConversationManager, model_manager: ModelManager):
    """渲染聊天界面
    
    Args:
        conv_manager: 对话管理器
        model_manager: 模型管理器
    """
    current_conv = conv_manager.get_current()
    if current_conv is None:
        st.info("👈 请在左侧侧边栏创建一个新对话开始聊天")
        st.stop()
    
    # 获取当前模型
    current_model = model_manager.get_current_model(st.session_state.current_model_key)
    if current_model is None:
        st.warning("⚠️ 当前模型不可用，请在设置中重新选择模型。")
        st.stop()
    
    # 为每个对话生成唯一的文件上传 key
    upload_key = f"{UPLOAD_CONFIG['key']}_{current_conv.id}"
    
    st.title("💬 AI Chat")
    st.caption(f"当前对话：{current_conv.title} | 模型：{current_model.name if current_model else '未选择'}")
    
    # 展示历史消息
    for msg in current_conv.messages:
        with st.chat_message(msg.role):
            st.markdown(msg.content)
    
    # 文件上传组件（使用对话特定的 key）
    uploaded_file = st.file_uploader(
        "📎 上传文件 (支持 .txt, .csv, .json, .py 等文本文件)",
        type=UPLOAD_CONFIG["allowed_types"],
        key=upload_key,
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
            user_input, uploaded_file, current_conv, current_model, conv_manager, upload_key
        )


def _process_user_input(
    user_input: str,
    uploaded_file,
    current_conv: Conversation,
    current_model,
    conv_manager: ConversationManager,
    upload_key: str
):
    """处理用户输入
    
    Args:
        user_input: 用户输入
        uploaded_file: 上传的文件
        current_conv: 当前对话
        current_model: 当前模型
        conv_manager: 对话管理器
        upload_key: 文件上传组件的key
    """
    full_prompt = user_input
    
    # 如果有上传文件，读取内容并合并到用户消息中
    if uploaded_file is not None:
        file_content, error = FileService.read_file(uploaded_file)
        if error:
            st.error(error)
            return
        else:
            full_prompt = FileService.format_file_prompt(
                file_content, uploaded_file.name, user_input
            )
            # 清除该对话的文件上传器状态
            if upload_key in st.session_state:
                del st.session_state[upload_key]
    
    # 将用户消息添加到当前对话
    current_conv.add_message("user", full_prompt)
    
    # 立即显示用户消息
    with st.chat_message("user"):
        st.markdown(full_prompt)
    
    # 调用 AI 获取回复
    api_messages = current_conv.get_messages_for_api()

    model_params = {
        "temperature": st.session_state.get("temperature", 0.7),
        "max_tokens": st.session_state.get("max_tokens", 1000),
        "top_p": st.session_state.get("top_p", 0.9),
    }

    with st.chat_message("assistant"):
        if st.session_state.get("enable_streaming", True):
            thinking_placeholder = st.empty()
            thinking_placeholder.caption("💭 思考中...")
            ai_response = st.write_stream(
                AIService.call_model_stream(current_model, api_messages, **model_params)
            )
            thinking_placeholder.empty()
        else:
            with st.spinner("思考中..."):
                ai_response = AIService.call_model(current_model, api_messages, **model_params)
            st.markdown(ai_response)
    
    # 将 AI 回复添加到对话
    current_conv.add_message("assistant", ai_response)
    
    # 更新对话标题
    current_conv.update_title_from_first_message(TITLE_MAX_LENGTH)
    
    # 刷新界面以确保状态同步
    st.rerun()