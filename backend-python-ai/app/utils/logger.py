"""
日志系统配置
提供结构化和分级的日志记录
"""

import os
import sys
import logging
import logging.handlers
from datetime import datetime
from typing import Optional, Callable, Any
from contextvars import ContextVar
from functools import wraps

from app.config.settings import settings

# 创建请求ID上下文变量
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="unknown")

class RequestIDFilter(logging.Filter):
    """添加请求ID到日志记录的过滤器"""
    
    def filter(self, record):
        record.request_id = request_id_ctx.get()
        return True

class ColoredFormatter(logging.Formatter):
    """带颜色的控制台日志格式化器"""
    
    COLORS = {
        "DEBUG": "\033[36m",      # 青色
        "INFO": "\033[32m",       # 绿色
        "WARNING": "\033[33m",    # 黄色
        "ERROR": "\033[31m",      # 红色
        "CRITICAL": "\033[35m",   # 洋红色
        "RESET": "\033[0m"        # 重置
    }
    
    def format(self, record):
        # 添加颜色
        if record.levelname in self.COLORS:
            color = self.COLORS[record.levelname]
            reset = self.COLORS["RESET"]
            record.levelname = f"{color}{record.levelname}{reset}"
            record.msg = f"{color}{record.msg}{reset}"
        
        # 调用父类格式化
        return super().format(record)

def setup_logging():
    """
    配置日志系统
    
    配置包括：
    - 控制台输出（带颜色，开发环境）
    - 文件输出（生产环境）
    - 按级别过滤
    - 请求ID追踪
    """
    
    # 创建日志目录
    log_dir = os.path.dirname(settings.LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # 获取根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.APP_LOG_LEVEL))
    
    # 清除现有处理器
    root_logger.handlers.clear()
    
    # 创建请求ID过滤器
    request_id_filter = RequestIDFilter()
    
    # 控制台处理器（开发环境）
    if settings.is_development:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        # 开发环境使用带颜色的格式化器
        console_format = ColoredFormatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(console_format)
        console_handler.addFilter(request_id_filter)
        root_logger.addHandler(console_handler)
    
    # 文件处理器（所有环境）
    file_handler = logging.handlers.RotatingFileHandler(
        filename=settings.LOG_FILE,
        maxBytes=settings.LOG_MAX_SIZE,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setLevel(getattr(logging, settings.APP_LOG_LEVEL))
    
    # 文件使用结构化JSON格式（生产环境）或详细文本格式
    if settings.is_production:
        # 生产环境使用JSON格式，便于日志收集
        file_format = logging.Formatter(
            fmt='{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", '
                '"request_id": "%(request_id)s", "message": "%(message)s"}',
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        # 其他环境使用详细文本格式
        file_format = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    file_handler.setFormatter(file_format)
    file_handler.addFilter(request_id_filter)
    root_logger.addHandler(file_handler)
    
    # 设置第三方库的日志级别
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    
    # 记录日志系统初始化完成
    root_logger.info(f"日志系统初始化完成 - 级别: {settings.APP_LOG_LEVEL}, 文件: {settings.LOG_FILE}")

def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器
    
    Args:
        name: 日志记录器名称，通常使用 __name__
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    return logger

def get_request_logger(request_id: str) -> logging.Logger:
    """
    获取带有请求ID上下文的日志记录器
    
    Args:
        request_id: 请求ID
        
    Returns:
        logging.Logger: 带有请求ID上下文的日志记录器
    """
    # 设置请求ID到上下文
    token = request_id_ctx.set(request_id)
    
    # 获取日志记录器
    logger = logging.getLogger("request")
    
    return logger

def log_execution_time(logger: Optional[logging.Logger] = None):
    """
    记录函数执行时间的装饰器
    
    Args:
        logger: 日志记录器，如果为None则创建新记录器
        
    Returns:
        Callable: 装饰器函数
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = datetime.now()
            func_name = func.__name__
            
            # 获取或创建日志记录器
            if logger is None:
                _logger = logging.getLogger(f"{func.__module__}.{func_name}")
            else:
                _logger = logger
            
            # 记录开始执行
            _logger.debug(f"开始执行: {func_name}")
            
            try:
                # 执行函数
                result = await func(*args, **kwargs)
                
                # 计算执行时间
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                
                # 记录执行完成
                _logger.debug(f"执行完成: {func_name} - 耗时: {execution_time:.3f}s")
                
                return result
                
            except Exception as e:
                # 计算执行时间（即使出错）
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                
                # 记录错误
                _logger.error(f"执行出错: {func_name} - 耗时: {execution_time:.3f}s - 错误: {str(e)}")
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = datetime.now()
            func_name = func.__name__
            
            # 获取或创建日志记录器
            if logger is None:
                _logger = logging.getLogger(f"{func.__module__}.{func_name}")
            else:
                _logger = logger
            
            # 记录开始执行
            _logger.debug(f"开始执行: {func_name}")
            
            try:
                # 执行函数
                result = func(*args, **kwargs)
                
                # 计算执行时间
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                
                # 记录执行完成
                _logger.debug(f"执行完成: {func_name} - 耗时: {execution_time:.3f}s")
                
                return result
                
            except Exception as e:
                # 计算执行时间（即使出错）
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                
                # 记录错误
                _logger.error(f"执行出错: {func_name} - 耗时: {execution_time:.3f}s - 错误: {str(e)}")
                raise
        
        # 根据函数类型返回合适的包装器
        if func.__code__.co_flags & 0x80:  # 检查是否为异步函数
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

class LoggerMixin:
    """
    日志混合类
    方便为类添加日志功能
    """
    
    @property
    def logger(self) -> logging.Logger:
        """获取类的日志记录器"""
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        return self._logger
    
    def log_debug(self, message: str, **kwargs):
        """记录调试日志"""
        extra = " " + " ".join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ""
        self.logger.debug(f"{message}{extra}")
    
    def log_info(self, message: str, **kwargs):
        """记录信息日志"""
        extra = " " + " ".join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ""
        self.logger.info(f"{message}{extra}")
    
    def log_warning(self, message: str, **kwargs):
        """记录警告日志"""
        extra = " " + " ".join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ""
        self.logger.warning(f"{message}{extra}")
    
    def log_error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """记录错误日志"""
        extra = " " + " ".join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ""
        if error:
            self.logger.error(f"{message}{extra}", exc_info=error)
        else:
            self.logger.error(f"{message}{extra}")
    
    def log_exception(self, message: str, error: Exception, **kwargs):
        """记录异常日志"""
        extra = " " + " ".join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ""
        self.logger.exception(f"{message}{extra}", exc_info=error)

# 导出日志函数
__all__ = [
    "setup_logging",
    "get_logger",
    "get_request_logger",
    "log_execution_time",
    "LoggerMixin",
    "request_id_ctx"
]