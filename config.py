"""应用配置模块"""

# 页面配置
PAGE_CONFIG = {
    "page_title": "AI Chat with History",
    "page_icon": "💬",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# AI 模型配置
AI_CONFIG = {
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 1000,
    "top_p": 0.9
}

# 文件上传配置
UPLOAD_CONFIG = {
    "allowed_types": ["txt", "csv", "json", "py", "md"],
    "key": "file_uploader_component"
}

# 默认对话标题
DEFAULT_CONVERSATION_TITLE = "新对话"

# 标题截取长度
TITLE_MAX_LENGTH = 30