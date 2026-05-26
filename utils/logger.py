"""日志工具模块"""

import logging
import sys
from pathlib import Path
from datetime import datetime

_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
_LOG_DIR.mkdir(exist_ok=True)

_LOG_FILE = _LOG_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"

_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
_DATE_FORMAT = "%H:%M:%S"


def _create_formatter():
    return logging.Formatter(_FORMAT, datefmt=_DATE_FORMAT)


def _create_console_handler():
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(_create_formatter())
    return handler


def _create_file_handler():
    handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(_create_formatter())
    return handler


def get_logger(name: str = "ai-chat") -> logging.Logger:
    """获取已配置的 logger 实例
    
    自动添加控制台和文件 handler，避免重复添加。
    
    Args:
        name: logger 名称，默认 "ai-chat"
        
    Returns:
        配置好的 Logger 实例
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        logger.addHandler(_create_console_handler())
        logger.addHandler(_create_file_handler())
        logger.propagate = False

    return logger