-- ============================================
-- 修复雇佣记录表和试用记录表缺少时间戳字段
-- ============================================

USE mekai;

-- 为 hire_records 表添加 created_at 和 updated_at 字段
ALTER TABLE hire_records
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间';

-- 为 trial_records 表添加 created_at 和 updated_at 字段
ALTER TABLE trial_records
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间';
