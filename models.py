"""数据模型模块"""

import uuid
import datetime
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Message:
    """消息数据模型"""
    role: str
    content: str
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)


@dataclass
class Conversation:
    """对话数据模型"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "新对话"
    messages: List[Message] = field(default_factory=list)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    
    def add_message(self, role: str, content: str) -> Message:
        """添加消息到对话"""
        message = Message(role=role, content=content)
        self.messages.append(message)
        return message
    
    def get_messages_for_api(self) -> List[dict]:
        """获取用于API调用的消息格式"""
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]
    
    def update_title_from_first_message(self, max_length: int = 30) -> None:
        """根据第一条用户消息更新标题"""
        if self.title == "新对话" and self.messages:
            first_msg = self.messages[0].content
            self.title = first_msg[:max_length] + ("..." if len(first_msg) > max_length else "")


@dataclass
class ConversationManager:
    """对话管理器"""
    conversations: List[Conversation] = field(default_factory=list)
    current_id: Optional[str] = None
    
    def create_conversation(self) -> Conversation:
        """创建新对话"""
        conv = Conversation()
        self.conversations.append(conv)
        self.current_id = conv.id
        return conv
    
    def get_current(self) -> Optional[Conversation]:
        """获取当前对话"""
        for conv in self.conversations:
            if conv.id == self.current_id:
                return conv
        return None
    
    def switch_to(self, conversation_id: str) -> Optional[Conversation]:
        """切换到指定对话"""
        for conv in self.conversations:
            if conv.id == conversation_id:
                self.current_id = conversation_id
                return conv
        return None
    
    def get_all_sorted(self, reverse: bool = True) -> List[Conversation]:
        """获取所有对话（按创建时间排序）"""
        return sorted(self.conversations, key=lambda x: x.created_at, reverse=reverse)