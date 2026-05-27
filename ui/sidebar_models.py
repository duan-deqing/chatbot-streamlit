"""侧边栏模型选择模块

采用双级联动机制：先选供应商，再选具体模型。
本地模型（Ollama）始终固定在供应商列表第一位。

核心流程：
1. render_model_selector() 渲染两个 selectbox（供应商 → 模型名称）
2. 选择变化时自动更新 st.session_state.current_model_key
3. 根据供应商类型展示对应子面板（OpenAI Key / Ollama 同步 / 自定义模型管理）
"""

import streamlit as st
from models.ollama_model import OllamaModel

# session_state key 常量
PROVIDER_LABEL_KEY = "_selected_provider"     # 当前选中供应商的 key
EDITING_CUSTOM_KEY = "_editing_custom_model"  # 正在编辑的自定义模型 key（空=新建模式）
FORM_SHOW_KEY = "_show_custom_form"           # 是否展开自定义模型表单


def render_model_selector(model_manager):
    """渲染双级联动模型选择器

    两个 selectbox 并列排列：
    - 左侧「供应商」：Ollama 固定第一、自定义居中、OpenAI 末尾
    - 右侧「模型名称」：根据供应商动态加载模型列表

    选择变化自动写入 st.session_state.current_model_key，
    供 chat.py 获取当前使用的模型。

    Args:
        model_manager: ModelManager 实例
    """
    st.markdown("### 模型选择")

    providers = model_manager.get_providers()

    # 初始化供应商选择（首次进入时根据 current_model_key 回正）
    if PROVIDER_LABEL_KEY not in st.session_state:
        current_key = st.session_state.get("current_model_key", "")
        for p_key, _ in providers:
            models = model_manager.get_models_by_provider(p_key)
            if any(m[0] == current_key for m in models):
                st.session_state[PROVIDER_LABEL_KEY] = p_key
                break
        else:
            st.session_state[PROVIDER_LABEL_KEY] = providers[0][0] if providers else ""

    provider_options = [p[1] for p in providers]
    provider_keys = [p[0] for p in providers]

    current_provider_idx = 0
    if st.session_state[PROVIDER_LABEL_KEY] in provider_keys:
        current_provider_idx = provider_keys.index(st.session_state[PROVIDER_LABEL_KEY])

    col_p, col_m = st.columns([1, 1])

    # 供应商选择框
    with col_p:
        selected_provider_display = st.selectbox(
            "供应商",
            options=provider_options,
            index=current_provider_idx,
            key="provider_selector",
            label_visibility="visible"
        )
        selected_provider_idx = provider_options.index(selected_provider_display)
        selected_provider_key = provider_keys[selected_provider_idx]
        st.session_state[PROVIDER_LABEL_KEY] = selected_provider_key

    # 根据供应商获取模型列表（Ollama 会触发自动检测）
    provider_models = model_manager.get_models_by_provider(selected_provider_key)

    model_options = [m[1] for m in provider_models]
    model_keys = [m[0] for m in provider_models]

    if not model_options:
        st.warning("该供应商下没有可用模型")
        _render_custom_model_section(model_manager)
        return

    # 模型名称选择框（回正到上次选择的模型）
    current_model_idx = 0
    current_model_key = st.session_state.get("current_model_key", "")
    if current_model_key in model_keys:
        current_model_idx = model_keys.index(current_model_key)

    with col_m:
        selected_model_display = st.selectbox(
            "模型名称",
            options=model_options,
            index=current_model_idx,
            key="model_selector",
            label_visibility="visible"
        )

    selected_model_idx = model_options.index(selected_model_display)
    selected_model_key = model_keys[selected_model_idx]
    st.session_state.current_model_key = selected_model_key

    # 根据供应商类型展示不同的子面板
    if selected_provider_key == "openai":
        _render_openai_api_key(model_manager)

    if selected_provider_key == "ollama":
        _render_ollama_sync(model_manager)

    _render_custom_model_section(model_manager)


def _render_openai_api_key(model_manager):
    """渲染 OpenAI API Key 输入区域

    展示当前 Key 的脱敏状态，提供输入框保存 / 清空。
    Key 保存为供应商级（所有 OpenAI 模型共享）。
    """
    st.divider()
    st.markdown("#### OpenAI API Key")
    current_key = model_manager.get_provider_api_key("openai")

    col1, col2 = st.columns([3, 1])
    with col1:
        api_key_input = st.text_input(
            "API Key",
            type="password",
            value=current_key,
            placeholder="sk-...",
            key="openai_api_key_input",
            label_visibility="collapsed"
        )
    with col2:
        if st.button("保存", key="save_openai_key", use_container_width=True):
            if api_key_input:
                model_manager.set_openai_api_key(api_key_input)
                st.success("已保存")
                st.rerun()
            else:
                model_manager.set_openai_api_key("")
                st.warning("已清空")

    current_key = model_manager.get_provider_api_key("openai")
    if current_key:
        masked = current_key[:8] + "****" + current_key[-4:]
        st.success(f"已配置: `{masked}`")
    else:
        st.warning("⚠️ 请配置 OpenAI API Key")


def _render_ollama_sync(model_manager):
    """渲染 Ollama 本地模型同步面板

    显示服务状态、已安装模型列表、手动添加输入框、刷新按钮。
    模型已由 ModelManager.get_models_by_provider 自动检测并注册，
    此面板仅提供状态查看和手动兜底操作。
    """
    st.divider()
    st.markdown("#### 本地模型同步")
    ollama_default = model_manager.get_ollama_default()

    if ollama_default and ollama_default.get_cached_status():
        st.success("🟢 Ollama 服务运行中")

        local_models = ollama_default.list_models()
        if local_models:
            st.caption("已检测到以下本地模型（自动加载）：")
            st.markdown("  \n".join(f"- {m}" for m in local_models))
        else:
            st.caption("未检测到已安装的模型，请通过 `ollama pull <model>` 获取。")

        # 手动添加（兜底：模型不在自动检测列表中时使用）
        col1, col2 = st.columns(2)
        with col1:
            manual_id = st.text_input(
                "手动添加（不在列表中时使用）",
                placeholder="如 qwen2:7b",
                key="manual_ollama_input",
                label_visibility="collapsed"
            )
        with col2:
            if st.button("添加", key="manual_ollama_add", use_container_width=True):
                if manual_id:
                    model_manager.add_ollama_model(manual_id)
                    st.success(f"已添加 {manual_id}")
                    st.rerun()

        # 刷新按钮（强制使 5 分钟缓存失效）
        if st.button("🔄 刷新检测", key="refresh_ollama", use_container_width=True):
            OllamaModel.refresh_cache()
            st.rerun()
    else:
        st.warning("🔴 Ollama 服务未运行")
        st.caption("请先启动 `ollama serve`")
        if st.button("🔄 重新检测", key="retry_ollama_detect", use_container_width=True):
            OllamaModel.refresh_cache()
            st.rerun()


def _render_custom_model_section(model_manager):
    """渲染自定义模型管理区域

    列出所有自定义模型（带 ⚙️ 图标区分），每个模型有 ✏️ 编辑和 🗑️ 删除按钮。
    底部「添加自定义模型」按钮展开/收起新建表单。
    """
    st.divider()
    st.markdown("#### 自定义模型")

    custom_models = model_manager.get_custom_models()

    if custom_models:
        for key, config in custom_models.items():
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.markdown(f"⚙️ **{config.name}**")
                st.caption(f"{config.provider} | `{config.model_id}` | `{config.base_url}`")
            with col2:
                if st.button("✏️", key=f"edit_custom_{key}", help="编辑"):
                    st.session_state[EDITING_CUSTOM_KEY] = key
                    st.session_state[FORM_SHOW_KEY] = True
                    st.rerun()
            with col3:
                if st.button("🗑️", key=f"del_custom_{key}", help="删除"):
                    model_manager.delete_custom_model(key)
                    # 如果删除的正是当前选中的模型，回退到默认
                    if st.session_state.get("current_model_key") == key:
                        st.session_state.current_model_key = "openai_gpt-3.5-turbo"
                    st.success("已删除")
                    st.rerun()
    else:
        st.caption("暂无自定义模型")

    # 折叠开关
    if st.button("➕ 添加自定义模型", key="toggle_custom_form", use_container_width=True):
        st.session_state[FORM_SHOW_KEY] = not st.session_state.get(FORM_SHOW_KEY, False)
        if not st.session_state[FORM_SHOW_KEY]:
            st.session_state.pop(EDITING_CUSTOM_KEY, None)
        st.rerun()

    if st.session_state.get(FORM_SHOW_KEY, False):
        _render_custom_model_form(model_manager)


def _render_custom_model_form(model_manager):
    """渲染自定义模型添加/编辑表单（st.form 实现）

    必填项：供应商名称、模型 ID、Base URL
    可选项：显示名称、API Key

    支持两种模式：
    - 新建模式：EDITING_CUSTOM_KEY 为空
    - 编辑模式：EDITING_CUSTOM_KEY 指向已有模型的 key，表单预填原值
    """
    editing_key = st.session_state.get(EDITING_CUSTOM_KEY, "")
    is_editing = bool(editing_key and editing_key in model_manager.get_custom_models())

    st.markdown("---")
    st.markdown("##### 编辑自定义模型" if is_editing else "##### 新建自定义模型")

    existing_config = model_manager.get_custom_models().get(editing_key) if is_editing else None

    with st.form(key="custom_model_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            provider_name = st.text_input(
                "供应商名称 *",
                value=existing_config.provider if existing_config else "",
                placeholder="如 DeepSeek, Groq",
                key="custom_provider"
            )
            model_id = st.text_input(
                "模型 ID *",
                value=existing_config.model_id if existing_config else "",
                placeholder="如 deepseek-chat",
                key="custom_model_id"
            )
        with col2:
            display_name = st.text_input(
                "显示名称",
                value=existing_config.name if existing_config else "",
                placeholder="如 DeepSeek Chat",
                key="custom_display_name"
            )
            base_url = st.text_input(
                "Base URL *",
                value=existing_config.base_url if existing_config else "",
                placeholder="https://api.deepseek.com/v1",
                key="custom_base_url"
            )

        api_key = st.text_input(
            "API Key",
            type="password",
            value=existing_config.api_key if existing_config else "",
            placeholder="sk-...（可选）",
            key="custom_api_key"
        )

        col_save, col_cancel = st.columns(2)
        with col_save:
            label = "💾 保存修改" if is_editing else "💾 添加模型"
            if st.form_submit_button(label, use_container_width=True):
                if not provider_name or not model_id or not base_url:
                    st.error("供应商名称、模型 ID 和 Base URL 为必填项。")
                else:
                    if is_editing:
                        model_manager.edit_custom_model(
                            editing_key,
                            name=display_name or model_id,
                            model_id=model_id,
                            provider=provider_name,
                            base_url=base_url,
                            api_key=api_key
                        )
                        st.success("已更新")
                    else:
                        model_manager.add_custom_model(
                            name=display_name or model_id,
                            model_id=model_id,
                            provider=provider_name,
                            base_url=base_url,
                            api_key=api_key
                        )
                        st.success("已添加")
                    # 保存后关闭表单
                    st.session_state.pop(EDITING_CUSTOM_KEY, None)
                    st.session_state[FORM_SHOW_KEY] = False
                    st.rerun()
        with col_cancel:
            if st.form_submit_button("取消", use_container_width=True):
                st.session_state.pop(EDITING_CUSTOM_KEY, None)
                st.session_state[FORM_SHOW_KEY] = False
                st.rerun()


def render_ollama_manager(model_manager):
    """保留旧接口兼容（已整合到 render_model_selector 中）"""
    pass