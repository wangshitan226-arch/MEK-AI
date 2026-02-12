# 系统默认数据设置指南

## 概述

MEK-AI 支持自动创建系统默认数据，包括：
- 默认组织 (`org_default`)
- 系统用户 (`system`)
- 预设数字员工（AI助手、程序员助手等）

## 方式一：应用启动时自动创建（推荐）

应用启动时会自动检查并创建默认组织和系统用户：

```bash
python -m app.main
```

启动日志中会显示：
```
数据库表初始化: 完成
默认组织和系统用户已存在  # 或
默认组织和系统用户创建完成
```

## 方式二：手动运行初始化脚本

### 1. 创建默认组织和用户

应用启动时已自动完成，无需手动操作。

### 2. 创建默认员工

运行初始化脚本创建预设员工：

```bash
python init_default_data.py
```

输出示例：
```
============================================================
🚀 MEK-AI 系统默认数据初始化
============================================================

📦 步骤 1/2: 初始化组织和用户...
✅ 默认组织已存在
✅ 系统用户已存在

🤖 步骤 2/2: 初始化默认员工...
✅ 创建员工: AI助手 (ID: emp_xxxxx)
✅ 创建员工: 程序员助手 (ID: emp_xxxxx)
✅ 创建员工: 文案写手 (ID: emp_xxxxx)
✅ 创建员工: 数据分析师 (ID: emp_xxxxx)
✅ 创建员工: 产品经理 (ID: emp_xxxxx)

============================================================
📊 初始化完成统计
============================================================
  创建员工数: 5
  跳过已存在: 0
  总计配置: 5
============================================================
```

## 预设员工列表

| 员工名称 | 类别 | 状态 | 价格 | 描述 |
|---------|------|------|------|------|
| AI助手 | 通用/助手 | 已发布 | 免费 | 通用的AI助手，回答各种问题 |
| 程序员助手 | 技术/编程 | 已发布 | 免费 | 编程助手，代码编写和调试 |
| 文案写手 | 创意/写作 | 已发布 | 免费 | 文案创作助手 |
| 数据分析师 | 技术/数据 | 已发布 | 免费 | 数据分析专家 |
| 产品经理 | 管理/产品 | 已发布 | 免费 | 产品规划专家 |

## 自定义默认员工

编辑 `init_default_data.py` 文件中的 `DEFAULT_EMPLOYEES` 列表：

```python
DEFAULT_EMPLOYEES = [
    {
        "name": "你的员工名称",
        "description": "员工描述",
        "category": ["类别1", "类别2"],
        "tags": ["标签1", "标签2"],
        "price": "0",
        "status": "published",
        "skills": ["技能1", "技能2"],
        "prompt": "系统提示词...",
        "model": "deepseek-chat",
        "is_hot": True,
    },
    # 添加更多员工...
]
```

然后重新运行：
```bash
python init_default_data.py
```

## 直接修改数据库（不推荐）

如需直接修改数据库，请使用以下SQL：

```sql
-- 创建组织
INSERT INTO organizations (id, name, description, status, created_at, updated_at)
VALUES ('org_default', '默认组织', '系统默认组织', 'active', NOW(), NOW());

-- 创建系统用户
INSERT INTO users (id, username, email, organization_id, role, status, created_at, updated_at)
VALUES ('system', 'system', 'system@mekai.ai', 'org_default', 'admin', 'active', NOW(), NOW());

-- 创建员工（示例）
INSERT INTO employees (
    id, name, description, status, price, 
    category, tags, skills, prompt, model,
    created_by, created_at, updated_at
) VALUES (
    'emp_001', 'AI助手', '通用的AI助手', 'published', '0',
    '["通用", "助手"]', '["AI", "问答"]', '["问答", "写作"]', 
    '你是一个 helpful 的AI助手...', 'deepseek-chat',
    'system', NOW(), NOW()
);
```

**注意**：直接修改数据库不会触发业务逻辑（如ID生成、默认值设置等），建议使用脚本方式。

## 常见问题

### Q: 运行脚本时提示数据库连接失败？
A: 请先确保：
1. MySQL服务已启动
2. `.env` 文件中配置了正确的 MySQL 密码
3. 数据库 `mekai` 已创建

### Q: 可以重复运行初始化脚本吗？
A: 可以。脚本会跳过已存在的员工，不会重复创建。

### Q: 如何删除默认员工？
A: 使用管理后台或API删除，不建议直接操作数据库。

### Q: 默认员工的图片如何修改？
A: 修改 `init_default_data.py` 中的 `avatar` 字段，使用图片URL。

---

**建议**：首次部署时运行一次 `init_default_data.py`，后续通过管理界面管理员工。
