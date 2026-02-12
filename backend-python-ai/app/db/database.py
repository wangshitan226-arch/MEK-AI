"""
数据库连接管理
使用SQLAlchemy管理MySQL连接
"""

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator

from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# 创建声明性基类
Base = declarative_base()

# 构建数据库URL
# 格式: mysql+pymysql://user:password@host:port/database
# 处理密码中的特殊字符
import urllib.parse

# 对密码进行URL编码，处理特殊字符
encoded_password = urllib.parse.quote_plus(str(settings.MYSQL_PASSWORD or ''))

DATABASE_URL = (
    f"mysql+pymysql://{settings.MYSQL_USER}:{encoded_password}"
    f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
    f"?charset=utf8mb4"
)

logger.info(f"数据库连接URL: mysql+pymysql://{settings.MYSQL_USER}:****@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}")

# 创建引擎
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # 自动检测断开连接
    pool_recycle=3600,   # 1小时后回收连接
    echo=settings.APP_DEBUG,  # 调试模式打印SQL
)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# 监听连接事件，设置时区
@event.listens_for(engine, "connect")
def set_mysql_timezone(dbapi_conn, connection_record):
    """设置MySQL时区为UTC"""
    cursor = dbapi_conn.cursor()
    cursor.execute("SET time_zone = '+00:00'")
    cursor.close()


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话
    用于FastAPI依赖注入
    
    Yields:
        Session: 数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    初始化数据库
    创建所有表结构
    """
    try:
        # 导入所有模型以确保它们被注册
        from app.db.models import (
            user,
            employee,
            knowledge,
            conversation,
            record,
        )
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise


def check_db_connection() -> bool:
    """
    检查数据库连接
    
    Returns:
        bool: 连接是否成功
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"数据库连接检查失败: {str(e)}")
        return False
