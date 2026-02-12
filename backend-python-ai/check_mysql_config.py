#!/usr/bin/env python3
"""
MySQL配置检查脚本
检查数据库连接配置是否正确
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def check_mysql_config():
    """检查MySQL配置"""
    print("\n" + "="*60)
    print("🔍 MySQL配置检查")
    print("="*60 + "\n")
    
    # 显示当前配置
    print("📋 当前配置:")
    print(f"  MYSQL_HOST: {settings.MYSQL_HOST}")
    print(f"  MYSQL_PORT: {settings.MYSQL_PORT}")
    print(f"  MYSQL_USER: {settings.MYSQL_USER}")
    print(f"  MYSQL_PASSWORD: {'*' * len(settings.MYSQL_PASSWORD) if settings.MYSQL_PASSWORD else '(空)'}")
    print(f"  MYSQL_DATABASE: {settings.MYSQL_DATABASE}")
    print()
    
    # 检查密码
    if not settings.MYSQL_PASSWORD or settings.MYSQL_PASSWORD == "your_mysql_password_here":
        print("❌ 错误: MySQL密码未设置或使用了默认占位符!")
        print("   请在 .env 文件中设置正确的 MYSQL_PASSWORD")
        print()
        print("📝 修复步骤:")
        print("   1. 打开 .env 文件")
        print("   2. 找到 MYSQL_PASSWORD 配置项")
        print("   3. 将 'your_mysql_password_here' 替换为您的实际MySQL密码")
        print("   4. 保存文件并重新启动应用")
        print()
        return False
    
    # 尝试连接数据库
    print("🔄 正在尝试连接数据库...")
    try:
        from app.db.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        print("✅ 数据库连接成功!")
        print()
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        print()
        print("🔧 可能的解决方案:")
        
        error_str = str(e).lower()
        
        if "access denied" in error_str:
            print("   1. 用户名或密码错误")
            print("   2. 请检查 MYSQL_USER 和 MYSQL_PASSWORD 配置")
        elif "unknown database" in error_str:
            print(f"   1. 数据库 '{settings.MYSQL_DATABASE}' 不存在")
            print("   2. 请先创建数据库:")
            print(f"      CREATE DATABASE {settings.MYSQL_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        elif "can't connect" in error_str or "connection refused" in error_str:
            print("   1. MySQL服务未启动")
            print("   2. 请检查 MYSQL_HOST 和 MYSQL_PORT 配置")
            print("   3. 确保MySQL服务器正在运行")
        else:
            print(f"   错误详情: {e}")
        
        print()
        return False


def show_env_example():
    """显示环境变量示例"""
    print("\n" + "="*60)
    print("📝 .env 文件示例")
    print("="*60 + "\n")
    print("""# MySQL数据库配置
MYSQL_HOST="localhost"
MYSQL_PORT=3306
MYSQL_USER="root"
MYSQL_PASSWORD="your_actual_password_here"
MYSQL_DATABASE="mekai"
""")


def main():
    """主函数"""
    success = check_mysql_config()
    
    if not success:
        show_env_example()
        sys.exit(1)
    else:
        print("🎉 所有检查通过!")
        sys.exit(0)


if __name__ == "__main__":
    main()
