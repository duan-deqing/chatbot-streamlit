"""侧边栏模型选择模块"""

import streamlit as st
from models.ollama_model import OllamaModel


def render_model_selector(model_manager):
    """渲染模型选择器
    
    Args:
        model_manager: 模型管理器
    """
    st.markdown("### 模型选择")
    
    all_models = {}
    
    for key, model in model_manager.get_openai_models().items():
        all_models[key] = f"OpenAI - {model.name}"
    
    ollama_models = model_manager.get_ollama_models()
    ollama_default = ollama_models.get("ollama_default")
    
    if ollama_default and ollama_default.get_cached_status():
        local_models = ollama_default.list_models()
        for model_id in local_models:
            key = f"ollama_{model_id}"
            if key not in ollama_models:
                model_manager.add_ollama_model(model_id)
            all_models[key] = f"Ollama - {model_id}"
    else:
        for key, model in ollama_models.items():
            status = "✓" if model.get_cached_status() else "✗"
            all_models[key] = f"Ollama - {model.name} [{status}]"
    
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


def render_ollama_manager(model_manager):
    """渲染Ollama模型管理
    
    Args:
        model_manager: 模型管理器
    """
    with st.expander("📦 管理 Ollama 模型"):
        ollama_model = model_manager.get_ollama_models().get("ollama_default")
        if ollama_model and ollama_model.get_cached_status():
            st.success("Ollama 服务运行中")
            
            local_models = ollama_model.list_models()
            if local_models:
                st.markdown("**本地已安装模型:**")
                for m in local_models:
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