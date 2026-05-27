"""聊天界面 UI 模块

负责渲染聊天区域的主要界面：
- 对话标题栏（当前对话 + 当前模型）
- 历史消息滚动展示
- 文件上传组件
- 聊天输入框
- 消息发送与 AI 回复流程
"""

import streamlit as st
from data import Conversation, ConversationManager
from models import ModelManager
from services.ai_service import AIService
from services.file_service import FileService
from config import UPLOAD_CONFIG, TITLE_MAX_LENGTH


def render_chat_interface(conv_manager: ConversationManager, model_manager: ModelManager):
    """渲染聊天界面主入口

    流程：
    1. 获取当前对话，空则提示创建
    2. 获取当前模型（自动注入 API Key），不可用时提示重新选择
    3. 渲染历史消息
    4. 渲染文件上传与输入框
    5. 用户输入时调用 _process_user_input 处理

    Args:
        conv_manager: 对话管理器
        model_manager: 模型管理器
    """
    current_conv = conv_manager.get_current()
    if current_conv is None:
        st.info("👈 请在左侧侧边栏创建一个新对话开始聊天")
        st.stop()

    # 获取当前模型（自动注入供应商/模型级 API Key）
    current_model = model_manager.get_current_model(st.session_state.current_model_key)
    if current_model is None:
        st.warning("⚠️ 当前模型不可用，请在设置中重新选择模型。")
        st.stop()

    # 为每个对话生成唯一的文件上传 key（切换对话时清空上传状态）
    upload_key = f"{UPLOAD_CONFIG['key']}_{current_conv.id}"

    st.title("💬 AI Chat")
    st.caption(f"当前对话：{current_conv.title} | 模型：{current_model.name if current_model else '未选择'}")

    # 历史消息渲染
    for msg in current_conv.messages:
        with st.chat_message(msg.role):
            st.markdown(msg.content)

    # 文件上传组件（key 绑定到当前对话，避免切换对话时状态残留）
    uploaded_file = st.file_uploader(
        "📎 上传文件 (支持 .txt, .csv, .json, .py 等文本文件)",
        type=UPLOAD_CONFIG["allowed_types"],
        key=upload_key,
        label_visibility="collapsed"
    )

    if uploaded_file is not None:
        st.info(f"📄 已上传: `{uploaded_file.name}`，将在发送消息时一并处理。")

    user_input = st.chat_input("输入消息...")

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
    """处理用户输入的核心流程

    流程：
    1. 如果有上传文件，读取并拼接到用户消息前
    2. 将完整消息添加到对话历史
    3. 调用 AI 模型（流式或同步，取决于 enable_streaming 设置）
    4. 将 AI 回复添加到对话历史
    5. 自动生成/更新对话标题
    6. 刷新页面

    Args:
        user_input: 用户输入的原始文本
        uploaded_file: 上传的文件对象（None 表示无文件）
        current_conv: 当前对话实例
        current_model: 当前选中的模型实例（已注入 API Key）
        conv_manager: 对话管理器
        upload_key: 文件上传组件的 session_state key（用于清除状态）
    """
    full_prompt = user_input

    # 处理上传文件：读取内容并拼接格式化提示
    if uploaded_file is not None:
        file_content, error = FileService.read_file(uploaded_file)
        if error:
            st.error(error)
            return
        else:
            full_prompt = FileService.format_file_prompt(
                file_content, uploaded_file.name, user_input
            )
            # 清除文件上传器状态，避免跨消息残留
            if upload_key in st.session_state:
                del st.session_state[upload_key]

    # 保存用户消息到对话历史
    current_conv.add_message("user", full_prompt)

    with st.chat_message("user"):
        st.markdown(full_prompt)

    # 构建 API 格式消息列表
    api_messages = current_conv.get_messages_for_api()

    # 从 setUp 弹窗读取用户配置的参数
    model_params = {
        "temperature": st.session_state.get("temperature", 0.7),
        "max_tokens": st.session_state.get("max_tokens", 1000),
        "top_p": st.session_state.get("top_p", 0.9),
    }

    # 调用 AI 获取回复（支持流式/同步两种模式）
    with st.chat_message("assistant"):
        if st.session_state.get("enable_streaming", True):
            # 流式模式：展示呼吸提示，逐 token 渲染回复
            thinking_placeholder = st.empty()
            thinking_placeholder.caption("💭 思考中...")
            ai_response = st.write_stream(
                AIService.call_model_stream(current_model, api_messages, **model_params)
            )
            thinking_placeholder.empty()
        else:
            # 同步模式：spinner 等待，一次性显示完整回复
            with st.spinner("思考中..."):
                ai_response = AIService.call_model(current_model, api_messages, **model_params)
            st.markdown(ai_response)

    # 保存 AI 回复到对话历史
    current_conv.add_message("assistant", ai_response)

    # 首次对话时自动用用户消息前 30 字生成标题
    current_conv.update_title_from_first_message(TITLE_MAX_LENGTH)

    st.rerun()