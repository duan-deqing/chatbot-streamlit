"""数据模型模块"""

import uuid
import datetime
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import List, Optional, Dict

from utils.helpers import get_time_category


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
    _index: Dict[str, Conversation] = field(default_factory=dict)
    
    def create_conversation(self) -> Conversation:
        """创建新对话"""
        conv = Conversation()
        self.conversations.append(conv)
        self._index[conv.id] = conv
        self.current_id = conv.id
        return conv
    
    def get_current(self) -> Optional[Conversation]:
        """获取当前对话"""
        if self.current_id is None:
            return None
        return self._index.get(self.current_id)
    
    def switch_to(self, conversation_id: str) -> Optional[Conversation]:
        """切换到指定对话"""
        conv = self._index.get(conversation_id)
        if conv is not None:
            self.current_id = conversation_id
        return conv
    
    def get_all_sorted(self, reverse: bool = True) -> List[Conversation]:
        """获取所有对话（按创建时间排序）"""
        return sorted(self.conversations, key=lambda x: x.created_at, reverse=reverse)

    def get_grouped_sorted(self) -> OrderedDict:
        """获取按时间分类分组的对话列表
        
        Returns:
            OrderedDict，key为分类标签，value为该分类下的对话列表（按时间倒序）
            分类顺序：今天 → 3天内 → 7天内 → 30天内 → 年月（按时间倒序）
        """
        category_order = ["今天", "3天内", "7天内", "30天内"]
        grouped = OrderedDict()

        for conv in sorted(self.conversations, key=lambda x: x.created_at, reverse=True):
            category = get_time_category(conv.created_at)
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(conv)

        result = OrderedDict()
        for cat in category_order:
            if cat in grouped:
                result[cat] = grouped[cat]
                del grouped[cat]

        for cat in sorted(grouped.keys(), reverse=True):
            result[cat] = grouped[cat]

        return result