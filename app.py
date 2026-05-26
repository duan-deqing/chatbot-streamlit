"""主应用入口

Streamlit 应用以 script 方式运行，每次交互都会从头执行整个文件。
因此所有初始化逻辑（页面配置、CSS、Session State）都在模块顶层完成，
然后按顺序渲染各 UI 组件，保证每次 rerun 时状态一致。
"""

from utils.helpers import configure_page
from utils.session import init_session_state
from ui.styles import load_custom_css
from ui.sidebar import render_sidebar
from ui.chat import render_chat_interface
from ui.sidebar_settings import render_settings

# 1. 页面配置（标题、图标、布局等）必须在任何 st. 调用之前执行
configure_page()

# 2. 加载自定义 CSS，覆盖 Streamlit 默认样式
load_custom_css()

# 3. 初始化会话状态（对话管理器、模型管理器、默认值等）
conv_manager, model_manager = init_session_state()

# 4. 渲染左侧边栏（API Key、模型选择、历史记录、设置入口）
render_sidebar(conv_manager, model_manager)

# 5. 渲染主聊天区（消息列表、输入框、文件上传）
render_chat_interface(conv_manager, model_manager)

# 6. 渲染设置弹窗（仅在 show_settings 为 True 时显示）
render_settings()