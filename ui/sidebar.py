"""侧边栏UI模块"""

import streamlit as st
from data_models import ConversationManager
from models import ModelManager
from models.ollama_model import OllamaModel


def _render_model_selector(model_manager: ModelManager):
    """渲染模型选择器
    
    Args:
        model_manager: 模型管理器
    """
    st.markdown("### 🤖 模型选择")
    
    # 获取所有可用模型
    all_models = {}
    
    # OpenAI模型
    for key, model in model_manager.get_openai_models().items():
        all_models[key] = f"OpenAI - {model.name}"
    
    # Ollama模型 - 获取本地可用模型列表
    ollama_models = model_manager.get_ollama_models()
    ollama_default = ollama_models.get("ollama_default")
    
    if ollama_default and ollama_default.get_cached_status():
        local_models = ollama_default.list_models()
        for model_id in local_models:
            key = f"ollama_{model_id}"
            # 如果模型不存在于管理器中，自动添加
            if key not in ollama_models:
                model_manager.add_ollama_model(model_id)
            all_models[key] = f"Ollama - {model_id}"
    else:
        # 显示默认的Ollama选项
        for key, model in ollama_models.items():
            status = "✓" if model.get_cached_status() else "✗"
            all_models[key] = f"Ollama - {model.name} [{status}]"
    
    # 模型选择下拉框
    if all_models:
        selected_key = st.selectbox(
            "选择模型",
            options=list(all_models.keys()),
            format_func=lambda x: all_models[x],
            index=list(all_models.keys()).index(st.session_state.current_model_key) 
                if st.session_state.current_model_key in all_models else 0,
            key="model_selector"
        )
        
        if selected_key:
            st.session_state.current_model_key = selected_key
    else:
        st.warning("没有可用的模型")


def _render_ollama_manager(model_manager: ModelManager):
    """渲染Ollama模型管理
    
    Args:
        model_manager: 模型管理器
    """
    with st.expander("📦 管理 Ollama 模型"):
        # 检查Ollama服务状态
        ollama_model = model_manager.get_ollama_models().get("ollama_default")
        if ollama_model and ollama_model.get_cached_status():
            st.success("Ollama 服务运行中")
            
            # 显示本地可用模型
            local_models = ollama_model.list_models()
            if local_models:
                st.markdown("**本地已安装模型:**")
                for m in local_models:
                    # 检查是否已添加到选择器
                    key = f"ollama_{m}"
                    if key in model_manager.get_ollama_models():
                        st.markdown(f"- {m} ✓")
                    else:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"- {m}")
                        with col2:
                            if st.button("添加", key=f"add_local_{m}", use_container_width=True):
                                model_manager.add_ollama_model(m)
                                st.rerun()
            
            # 手动添加新模型
            st.markdown("---")
            new_model_id = st.text_input(
                "手动添加 Ollama 模型",
                placeholder="输入模型名称，如 qwen2:7b",
                key="new_ollama_model"
            )
            col1, col2 = st.columns(2)
            with col1:
                if st.button("添加模型", key="add_ollama_btn", use_container_width=True):
                    if new_model_id:
                        model_manager.add_ollama_model(new_model_id)
                        st.success(f"已添加模型: {new_model_id}")
                        st.rerun()
                    else:
                        st.warning("请输入模型名称")
            with col2:
                if st.button("🔄 刷新", key="refresh_ollama_btn", use_container_width=True):
                    OllamaModel.refresh_cache()
                    st.rerun()
        else:
            st.warning("Ollama 服务未运行")
            st.markdown("请先启动 Ollama: `ollama serve`")
            if st.button("🔄 重新检测", key="retry_ollama_btn", use_container_width=True):
                OllamaModel.refresh_cache()
                st.rerun()


def render_sidebar(conv_manager: ConversationManager, model_manager: ModelManager) -> str:
    """渲染侧边栏
    
    Args:
        conv_manager: 对话管理器
        model_manager: 模型管理器
        
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
            model_manager.set_openai_api_key(api_key_input)
        
        # 未填 API Key 时的提醒
        if not st.session_state.get("api_key", ""):
            st.warning("⚠️ 使用非本地模型请在上方输入 API Key")

        
        # 模型选择
        _render_model_selector(model_manager)
        
        # Ollama模型管理
        _render_ollama_manager(model_manager)
        
        st.markdown("---")
        
        # 新建对话按钮 - 只有当前对话有消息时才能创建新对话
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
        
        st.markdown("### 📜 历史记录")

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

        if st.button(
            "⚙️ 设置",
            key="settings_btn",
            use_container_width=True
        ):
            st.session_state.show_settings = True
            st.rerun()

    return st.session_state.get("api_key", "")