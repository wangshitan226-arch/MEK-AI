-- ============================================
-- 修复剩余表缺失的字段（不使用 IF NOT EXISTS）
-- ============================================

USE mekai;

-- ============================================
-- 1. documents 表 - 添加 updated_at
-- ============================================
ALTER TABLE documents ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间';

-- ============================================
-- 2. hire_records 表 - 添加 created_at 和 updated_at
-- ============================================
ALTER TABLE hire_records ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间';
ALTER TABLE hire_records ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间';

-- ============================================
-- 3. trial_records 表 - 添加 created_at 和 updated_at
-- ============================================
ALTER TABLE trial_records ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间';
ALTER TABLE trial_records ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间';

-- ============================================
-- 4. vector_metadata 表 - 添加 updated_at
-- ============================================
ALTER TABLE vector_metadata ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间';
