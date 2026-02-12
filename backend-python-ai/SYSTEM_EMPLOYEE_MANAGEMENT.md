# 系统级员工管理功能设计方案

## 1. 功能概述

### 1.1 需求描述

在员工广场中区分两类员工：
- **系统级员工**：由管理员创建和管理，所有用户可见
- **用户级员工**：由普通用户创建，仅创建者可见

### 1.2 角色划分

| 角色 | 权限 |
|------|------|
| **系统管理员** | 创建/编辑/删除系统级员工，管理所有员工 |
| **普通用户** | 查看系统级员工，创建/管理自己的员工 |

---

## 2. 数据模型扩展

### 2.1 员工表扩展

在 `employees` 表中添加字段：

```sql
ALTER TABLE employees ADD COLUMN employee_type ENUM('system', 'user') DEFAULT 'user' COMMENT '员工类型: system-系统级, user-用户级';
ALTER TABLE employees ADD COLUMN is_system_default BOOLEAN DEFAULT FALSE COMMENT '是否为系统默认员工';
ALTER TABLE employees ADD INDEX idx_employee_type (employee_type);
ALTER TABLE employees ADD INDEX idx_is_system_default (is_system_default);
```

### 2.2 Pydantic 模型扩展

```python
# app/models/schemas.py

class EmployeeResponse(EmployeeBase):
    """员工响应模型"""
    id: str
    employee_type: str = "user"  # system 或 user
    is_system_default: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SystemEmployeeCreate(EmployeeBase):
    """系统级员工创建模型（管理员用）"""
    employee_type: str = "system"
    is_system_default: bool = False
    # ... 其他字段
```

---

## 3. API 设计

### 3.1 管理员 API（需认证）

```python
# app/api/v1/endpoints/admin_employees.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(prefix="/admin/employees", tags=["管理员-员工管理"])


@router.get("/system", response_model=SuccessResponse)
async def list_system_employees(
    page: int = 1,
    page_size: int = 20,
    current_user: UserContext = Depends(require_admin),  # 需管理员权限
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """获取系统级员工列表"""
    employees = employee_repository.get_by_type(db, employee_type="system")
    # 分页处理...
    return SuccessResponse(data=paged_result)


@router.post("/system", response_model=SuccessResponse)
async def create_system_employee(
    data: SystemEmployeeCreate,
    current_user: UserContext = Depends(require_admin),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """创建系统级员工"""
    employee = employee_service.create_system_employee(db, data, created_by="system")
    return SuccessResponse(data=employee.dict())


@router.put("/system/{employee_id}", response_model=SuccessResponse)
async def update_system_employee(
    employee_id: str,
    data: EmployeeUpdate,
    current_user: UserContext = Depends(require_admin),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """更新系统级员工"""
    employee = employee_service.update_system_employee(db, employee_id, data)
    return SuccessResponse(data=employee.dict())


@router.delete("/system/{employee_id}", response_model=SuccessResponse)
async def delete_system_employee(
    employee_id: str,
    current_user: UserContext = Depends(require_admin),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """删除系统级员工"""
    employee_service.delete_system_employee(db, employee_id)
    return SuccessResponse(message="删除成功")
```

### 3.2 员工广场 API（公开）

```python
# app/api/v1/endpoints/marketplace.py

@router.get("/employees", response_model=SuccessResponse)
async def get_marketplace_employees(
    # ... 现有参数
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """
    获取市场员工列表
    
    说明：
    - 只返回系统级员工（employee_type='system'）
    - 已发布状态（status='published'）
    """
    employees = employee_service.get_marketplace_employees(db)
    return SuccessResponse(data=employees)
```

---

## 4. Service 层实现

### 4.1 系统级员工创建

```python
# app/services/employee_service.py

class EmployeeService:
    
    def create_system_employee(
        self,
        db: Session,
        employee_data: SystemEmployeeCreate,
        created_by: str = "system"
    ) -> Employee:
        """
        创建系统级员工
        
        特点：
        - employee_type = 'system'
        - is_system_default 可以设置
        - 跳过某些用户级验证
        """
        # 验证数据
        # ...
        
        employee = Employee(
            **employee_data.dict(),
            employee_type="system",
            created_by=created_by,
            status="published"  # 系统级员工默认发布
        )
        
        db.add(employee)
        db.commit()
        db.refresh(employee)
        
        return employee
    
    def get_marketplace_employees(self, db: Session) -> List[Employee]:
        """
        获取广场员工列表
        
        只返回系统级且已发布的员工
        """
        return db.query(Employee).filter(
            Employee.employee_type == "system",
            Employee.status == "published"
        ).all()
```

---

## 5. RuoYi 集成方案

### 5.1 方案一：Python 后端 + RuoYi 前端（推荐）

```
┌─────────────────────────────────────────────────────────┐
│                    RuoYi Vue3 前端                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ 系统管理    │  │ 员工管理    │  │ 权限管理        │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼ HTTP REST API
┌─────────────────────────────────────────────────────────┐
│              MEK-AI Python 后端 (FastAPI)              │
│  ┌─────────────────────────────────────────────────────┐│
│  │ /admin/employees/system   - 系统员工CRUD            ││
│  │ /admin/employees/{id}    - 员工详情                ││
│  └─────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────┐│
│  │ Repository Layer → Service Layer → API Endpoints    ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    MySQL 数据库                          │
│  ┌─────────────────────────────────────────────────────┐│
│  │ employees (employee_type, is_system_default)        ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

### 5.2 方案二：独立 RuoYi Java 后端

如果完全使用 RuoYi Java，可以：

1. **复用 MySQL 数据库**：两个后端共享同一数据库
2. **REST API 对接**：Python 后端提供 REST API
3. **数据同步**：通过消息队列同步数据

```
┌─────────────────────────────────────────────────────────┐
│              RuoYi Vue3 前端 (管理端)                   │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼ HTTP
┌─────────────────────────────────────────────────────────┐
│              RuoYi Java 后端 (管理功能)                 │
│  ┌─────────────────────────────────────────────────────┐│
│  │ SystemEmployeeController                            ││
│  │   - listSystemEmployees                            ││
│  │   - createSystemEmployee                           ││
│  │   - updateSystemEmployee                           ││
│  │   - deleteSystemEmployee                           ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
                            │ 共享 MySQL
                            ▼
┌─────────────────────────────────────────────────────────┐
│              Python 后端 (AI 功能)                      │
│  ┌─────────────────────────────────────────────────────┐│
│  │ Chat Service / Employee Service                     ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

---

## 6. 前端页面设计（RuoYi）

### 6.1 员工管理页面

```vue
<!-- views/system/employee/index.vue -->
<template>
  <div class="app-container">
    <!-- 搜索栏 -->
    <el-form :model="queryParams" ref="queryForm" size="small" :inline="true" v-show="showSearch">
      <el-form-item label="员工名称" prop="name">
        <el-input v-model="queryParams.name" placeholder="请输入员工名称" clearable/>
      </el-form-item>
      <el-form-item label="员工类型" prop="employeeType">
        <el-select v-model="queryParams.employeeType" placeholder="请选择">
          <el-option label="系统级" value="system"/>
          <el-option label="用户级" value="user"/>
        </el-select>
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-select v-model="queryParams.status" placeholder="请选择">
          <el-option label="草稿" value="draft"/>
          <el-option label="已发布" value="published"/>
          <el-option label="已归档" value="archived"/>
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="el-icon-search" @click="handleQuery">搜索</el-button>
        <el-button icon="el-icon-refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 操作按钮 -->
    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button type="primary" icon="el-icon-plus" @click="handleAdd">新增系统员工</el-button>
      </el-col>
      <right-toolbar :showSearch.sync="showSearch" @queryTable="getList"/>
    </el-row>

    <!-- 数据表格 -->
    <el-table v-loading="loading" :data="employeeList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center"/>
      <el-table-column label="员工名称" prop="name" width="150"/>
      <el-table-column label="头像" prop="avatar" width="80">
        <template slot-scope="scope">
          <el-avatar :src="scope.row.avatar" :size="40"/>
        </template>
      </el-table-column>
      <el-table-column label="类型" prop="employeeType" width="100">
        <template slot-scope="scope">
          <el-tag :type="scope.row.employeeType === 'system' ? 'danger' : 'info'">
            {{ scope.row.employeeType === 'system' ? '系统级' : '用户级' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="分类" prop="category" width="120"/>
      <el-table-column label="状态" prop="status" width="100">
        <template slot-scope="scope">
          <el-tag :type="scope.row.status === 'published' ? 'success' : 'warning'">
            {{ scope.row.status === 'published' ? '已发布' : '草稿' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" prop="createdAt" width="180"/>
      <el-table-column label="操作" width="200" align="center">
        <template slot-scope="scope">
          <el-button size="mini" type="text" @click="handleUpdate(scope.row)">编辑</el-button>
          <el-button size="mini" type="text" @click="handleDelete(scope.row)">删除</el-button>
          <el-button size="mini" type="text" @click="handlePreview(scope.row)">预览</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <pagination v-show="total > 0" :total="total" :page.sync="queryParams.pageNum" :limit.sync="queryParams.pageSize" @pagination="getList"/>

    <!-- 添加/编辑对话框 -->
    <el-dialog :title="title" :visible.sync="open" width="800px" append-to-body>
      <el-form ref="form" :model="form" :rules="rules" label-width="100px">
        <el-row>
          <el-col :span="12">
            <el-form-item label="员工名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入员工名称"/>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="员工类型">
              <el-select v-model="form.employeeType" disabled>
                <el-option label="系统级" value="system"/>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <!-- 更多表单字段... -->
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="submitForm">确 定</el-button>
        <el-button @click="cancel">取 消</el-button>
      </div>
    </el-dialog>
  </div>
</template>
```

---

## 7. 实施路线图

### Phase 1: 数据模型扩展
- [ ] 添加 `employee_type` 和 `is_system_default` 字段
- [ ] 更新 Pydantic 模型
- [ ] 更新 Repository 层查询方法

### Phase 2: API 开发
- [ ] 开发 `/admin/employees/system` API
- [ ] 更新员工广场 API（只返回系统级员工）
- [ ] 添加管理员权限验证

### Phase 3: RuoYi 集成
- [ ] 对接 RuoYi 前端
- [ ] 实现员工管理页面
- [ ] 实现预览功能

### Phase 4: 权限系统
- [ ] 实现角色权限控制
- [ ] 添加审计日志
- [ ] 批量操作功能

---

## 8. 快速开始

### 8.1 数据库迁移

```bash
# 1. 添加字段
mysql -u root -p mekai -e "
ALTER TABLE employees 
ADD COLUMN employee_type ENUM('system', 'user') DEFAULT 'user' COMMENT '员工类型',
ADD COLUMN is_system_default BOOLEAN DEFAULT FALSE COMMENT '是否系统默认',
ADD INDEX idx_employee_type (employee_type);
"
```

### 8.2 更新现有数据

```sql
-- 将现有员工标记为用户级
UPDATE employees SET employee_type = 'user' WHERE employee_type IS NULL;
```

### 8.3 创建系统级员工示例

```sql
INSERT INTO employees (
    id, name, description, avatar, category, tags, 
    price, status, skills, prompt, model,
    employee_type, is_system_default, created_by,
    created_at, updated_at
) VALUES (
    'emp_sys_001', 'AI助手', '通用的AI助手...',
    'https://api.dicebear.com/7.x/bottts/svg?seed=ai-assistant',
    '[\"通用\", \"助手\"]', '[\"AI\", \"问答\"]',
    '0', 'published', '[\"问答\", \"写作\"]',
    '你是一个 helpful 的AI助手...', 'deepseek-chat',
    'system', TRUE, 'system',
    NOW(), NOW()
);
```

---

**文档版本**: v1.0  
**创建日期**: 2026-02-09
