# MEK-AI 内存存储 → MySQL 迁移指南

> 本文档指导如何将项目从内存存储迁移到MySQL数据库存储

---

## 📋 迁移概览

### 架构变化

```
改造前（内存存储）:
┌─────────────────┐
│  EmployeeService│──► self._employees: Dict
├─────────────────┤
│KnowledgeService │──► self._knowledge_bases: Dict
├─────────────────┤
│ConversationMemory│──► self._conversations: Dict
└─────────────────┘

改造后（MySQL存储）:
┌─────────────────┐     ┌──────────────┐     ┌──────────┐
│  EmployeeService│────►│ EmployeeRepo │────►│  MySQL   │
├─────────────────┤     ├──────────────┤     ├──────────┤
│KnowledgeService │────►│KnowledgeRepo │────►│  MySQL   │
├─────────────────┤     ├──────────────┤     ├──────────┤
│ConversationMem  │────►│ConversationRepo│───►│  MySQL   │
└─────────────────┘     └──────────────┘     └──────────┘
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装数据库依赖
pip install sqlalchemy>=2.0.0 pymysql>=1.1.0

# 或使用 requirements-db.txt
cat requirements-db.txt >> requirements.txt
pip install -r requirements.txt
```

### 2. 配置数据库连接

在 `.env` 文件中添加：

```env
# MySQL数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=mekai
```

### 3. 初始化数据库

```bash
# 方法1: 使用SQL脚本
mysql -u root -p < app/db/migrations/001_initial_schema_mysql.sql

# 方法2: 使用SQLAlchemy自动创建（开发环境）
python -c "from app.db import init_db; init_db()"
```

### 4. 启动应用

```bash
# 数据库连接会自动初始化
python -m app.main
```

---

## 📁 新增文件清单

### 数据库核心文件

| 文件路径 | 说明 |
|---------|------|
| `app/db/__init__.py` | 数据库模块导出 |
| `app/db/database.py` | 连接池和会话管理 |
| `app/db/models/base.py` | 基础ORM模型 |
| `app/db/models/user.py` | User/Organization模型 |
| `app/db/models/employee.py` | Employee模型 |
| `app/db/models/knowledge.py` | Knowledge相关模型 |
| `app/db/models/conversation.py` | Conversation/Message模型 |
| `app/db/models/record.py` | Hire/Trial记录模型 |
| `app/db/repositories/base.py` | 基础仓库类 |
| `app/db/repositories/employee_repo.py` | 员工数据访问 |
| `app/db/repositories/knowledge_repo.py` | 知识库数据访问 |
| `app/db/repositories/conversation_repo.py` | 对话数据访问 |

### 配置文件修改

| 文件路径 | 修改内容 |
|---------|---------|
| `app/config/settings.py` | 添加MySQL配置项 |
| `requirements.txt` | 添加SQLAlchemy和PyMySQL |

---

## 🔄 Service层改造示例

### EmployeeService 改造

#### 改造前（内存存储）

```python
class EmployeeService(LoggerMixin):
    def __init__(self):
        self._employees: Dict[str, Dict[str, Any]] = {}
        self._init_sample_employees()
    
    def get_employee(self, employee_id: str) -> Optional[EmployeeResponse]:
        if employee_id not in self._employees:
            return None
        return EmployeeResponse(**self._employees[employee_id])
    
    def create_employee(self, employee_data: EmployeeCreate, created_by: str):
        employee_id = f"emp_{str(uuid.uuid4())[:8]}"
        employee_record = {
            "id": employee_id,
            **employee_data.dict(),
            "created_by": created_by,
            # ...
        }
        self._employees[employee_id] = employee_record
        return EmployeeResponse(**employee_record)
```

#### 改造后（MySQL存储）

```python
from sqlalchemy.orm import Session
from app.db.repositories import employee_repository
from app.db.models import Employee

class EmployeeService(LoggerMixin):
    """不再存储数据，通过repository访问数据库"""
    
    def get_employee(self, db: Session, employee_id: str) -> Optional[EmployeeResponse]:
        employee = employee_repository.get(db, employee_id)
        if not employee:
            return None
        return EmployeeResponse(**employee.to_dict())
    
    def create_employee(
        self, 
        db: Session, 
        employee_data: EmployeeCreate, 
        created_by: str
    ):
        import uuid
        from datetime import datetime
        
        employee_record = {
            "id": f"emp_{str(uuid.uuid4())[:8]}",
            "name": employee_data.name,
            "description": employee_data.description,
            # ... 其他字段
            "created_by": created_by,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        employee = employee_repository.create(db, obj_in=employee_record)
        return EmployeeResponse(**employee.to_dict())
```

### API层配合修改

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db import get_db

@router.get("/{employee_id}")
async def get_employee(
    employee_id: str,
    db: Session = Depends(get_db)  # 注入数据库会话
):
    employee = employee_service.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="员工不存在")
    return SuccessResponse(data=employee)
```

---

## 📊 数据迁移脚本

### 从内存数据导出到MySQL

```python
# migrate_data.py
"""
数据迁移脚本：将内存数据迁移到MySQL
"""

from sqlalchemy.orm import Session
from app.db import SessionLocal, init_db
from app.db.repositories import (
    employee_repository,
    knowledge_repository,
    conversation_repository,
)
from app.services.employee_service import employee_service
from app.services.knowledge.knowledge_service import knowledge_service
from app.services.memory.conversation_memory import conversation_memory_manager

def migrate_employees():
    """迁移员工数据"""
    db = SessionLocal()
    try:
        # 获取内存中的员工数据
        for emp_id, emp_data in employee_service._employees.items():
            # 转换为ORM模型格式
            employee_record = {
                "id": emp_data["id"],
                "name": emp_data["name"],
                "description": emp_data.get("description", ""),
                "avatar": emp_data.get("avatar"),
                "category": emp_data.get("category", []),
                "tags": emp_data.get("tags", []),
                "price": str(emp_data.get("price", "0")),
                "original_price": emp_data.get("original_price"),
                "trial_count": emp_data.get("trial_count", 0),
                "hire_count": emp_data.get("hire_count", 0),
                "is_hired": emp_data.get("is_hired", False),
                "is_recruited": emp_data.get("is_recruited", False),
                "status": emp_data.get("status", "draft"),
                "skills": emp_data.get("skills", []),
                "knowledge_base_ids": emp_data.get("knowledge_base_ids", []),
                "industry": emp_data.get("industry"),
                "role": emp_data.get("role"),
                "prompt": emp_data.get("prompt"),
                "model": emp_data.get("model", "deepseek-chat"),
                "is_hot": emp_data.get("is_hot", False),
                "personality": emp_data.get("personality"),
                "created_by": emp_data.get("created_by"),
                "created_at": emp_data.get("created_at"),
                "updated_at": emp_data.get("updated_at"),
            }
            
            # 检查是否已存在
            existing = employee_repository.get(db, emp_id)
            if not existing:
                employee_repository.create(db, obj_in=employee_record)
                print(f"✓ 迁移员工: {emp_id}")
        
        db.commit()
        print(f"✅ 员工数据迁移完成，共 {len(employee_service._employees)} 条")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 员工迁移失败: {e}")
        raise
    finally:
        db.close()


def migrate_knowledge_bases():
    """迁移知识库数据"""
    db = SessionLocal()
    try:
        for kb_id, kb_data in knowledge_service._knowledge_bases.items():
            kb_record = {
                "id": kb_data["id"],
                "name": kb_data["name"],
                "description": kb_data.get("description", ""),
                "category": kb_data.get("category"),
                "doc_count": kb_data.get("doc_count", 0),
                "created_by": kb_data.get("created_by"),
                "status": kb_data.get("status", "active"),
                "tags": kb_data.get("tags", []),
                "is_public": kb_data.get("is_public", True),
                "vectorized": kb_data.get("vectorized", False),
                "embedding_model": kb_data.get("embedding_model", "text-embedding-3-small"),
                "created_at": kb_data.get("created_at"),
                "updated_at": kb_data.get("updated_at"),
            }
            
            existing = knowledge_repository.get_kb(db, kb_id)
            if not existing:
                knowledge_repository.create_kb(db, obj_in=kb_record)
                print(f"✓ 迁移知识库: {kb_id}")
        
        db.commit()
        print(f"✅ 知识库数据迁移完成")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 知识库迁移失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 开始数据迁移...")
    
    # 初始化数据库表
    print("📦 初始化数据库表...")
    init_db()
    
    # 迁移数据
    migrate_employees()
    migrate_knowledge_bases()
    
    print("✅ 数据迁移完成！")
```

---

## ⚠️ 注意事项

### 1. 事务管理

```python
# 使用数据库会话时需要注意事务
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db import get_db

@router.post("/employees")
def create_employee(
    data: EmployeeCreate,
    db: Session = Depends(get_db)
):
    try:
        employee = employee_service.create_employee(db, data, "user_001")
        db.commit()  # 提交事务
        return employee
    except Exception as e:
        db.rollback()  # 回滚事务
        raise
```

### 2. 性能优化

```python
# 使用joinedload避免N+1查询
from sqlalchemy.orm import joinedload

# 查询员工同时加载关联数据
db.query(Employee).options(
    joinedload(Employee.creator),
    joinedload(Employee.organization)
).all()
```

### 3. 异步支持（可选）

```python
# 如果需要异步支持，可以使用 asyncmy + SQLAlchemy async
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# 修改 database.py 使用异步引擎
async_engine = create_async_engine(
    "mysql+asyncmy://user:pass@localhost/db",
    echo=True,
)
```

---

## 🔧 故障排查

### 问题1: 连接失败

```
Error: Can't connect to MySQL server
```

**解决:**
1. 检查MySQL服务是否启动
2. 检查配置参数是否正确
3. 检查防火墙设置

### 问题2: 字符集问题

```
Error: Incorrect string value
```

**解决:**
确保数据库和表使用 `utf8mb4` 字符集

### 问题3: 外键约束冲突

```
Error: Cannot add or update a child row
```

**解决:**
1. 确保外键引用的数据存在
2. 或者暂时禁用外键检查: `SET FOREIGN_KEY_CHECKS=0;`

---

## 📚 参考文档

- [SQLAlchemy 2.0 文档](https://docs.sqlalchemy.org/)
- [FastAPI + SQLAlchemy](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [PyMySQL 文档](https://pymysql.readthedocs.io/)

---

*文档版本: v1.0*
*更新日期: 2026-02-09*
