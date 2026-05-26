"""文件服务模块"""

from typing import Optional, Tuple


class FileService:
    """文件服务类"""
    
    @staticmethod
    def read_file(uploaded_file) -> Tuple[Optional[str], Optional[str]]:
        """读取上传的文件内容
        
        Args:
            uploaded_file: Streamlit上传的文件对象
            
        Returns:
            Tuple[文件内容, 错误信息]
        """
        try:
            content = uploaded_file.read().decode("utf-8")
            return content, None
        except UnicodeDecodeError:
            return None, "⚠️ 文件编码错误，请上传纯文本文件（如 .txt, .csv 等 UTF-8 编码）。"
        except Exception as e:
            return None, f"读取文件失败: {e}"
    
    @staticmethod
    def format_file_prompt(file_content: str, file_name: str, user_input: str) -> str:
        """格式化包含文件内容的用户提示
        
        Args:
            file_content: 文件内容
            file_name: 文件名
            user_input: 用户输入
            
        Returns:
            格式化后的提示文本
        """
        return (
            f"用户上传了一个文件：**{file_name}**\n"
            f"文件内容如下：\n```\n{file_content}\n```\n\n"
            f"用户的问题/指令：{user_input}"
        )