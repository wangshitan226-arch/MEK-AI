-- ============================================
-- 修复所有表缺失的字段
-- 根据模型和SQL脚本的对比结果
-- ============================================

USE mekai;

-- ============================================
-- 1. documents 表 - 添加 updated_at
-- ============================================
ALTER TABLE documents
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间';

-- ============================================
-- 2. employees 表 - 添加 employee_type 和 is_system_default
-- ============================================
ALTER TABLE employees
ADD COLUMN IF NOT EXISTS employee_type VARCHAR(20) DEFAULT 'user' COMMENT '员工类型: system-系统级, user-用户级',
ADD COLUMN IF NOT EXISTS is_system_default BOOLEAN DEFAULT FALSE COMMENT '是否系统默认员工';

-- ============================================
-- 3. knowledge_items 表 - 添加 updated_at
-- ============================================
ALTER TABLE knowledge_items
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间';

-- ============================================
-- 4. messages 表 - 添加 updated_at
-- ============================================
ALTER TABLE messages
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间';

-- ============================================
-- 5. vector_metadata 表 - 添加 updated_at
-- ============================================
ALTER TABLE vector_metadata
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间';

-- 注意: hire_records 和 trial_records 的 created_at/updated_at 已在 003 迁移中添加
