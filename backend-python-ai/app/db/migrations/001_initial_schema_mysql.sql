-- ============================================
-- MEK-AI 数据库表结构 (MySQL)
-- 版本: v1.1
-- 说明: 基于实际数据流设计，兼容现有功能
-- 更新: 优化字段类型，添加组织表和权限关联表
-- ============================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS mekai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE mekai;

-- ============================================
-- 1. 组织表 (新增)
-- ============================================
CREATE TABLE IF NOT EXISTS organizations (
    id VARCHAR(50) PRIMARY KEY COMMENT '组织ID',
    name VARCHAR(100) NOT NULL COMMENT '组织名称',
    description TEXT COMMENT '描述',
    logo TEXT COMMENT '组织Logo URL',
    status VARCHAR(20) DEFAULT 'active' COMMENT '状态: active/inactive/suspended',
    settings JSON COMMENT '组织配置JSON',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB COMMENT='组织表';

-- ============================================
-- 2. 用户表
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(50) PRIMARY KEY COMMENT '用户ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    email VARCHAR(100) UNIQUE COMMENT '邮箱',
    phone VARCHAR(20) UNIQUE COMMENT '手机号',
    password_hash VARCHAR(255) COMMENT '密码哈希',
    organization_id VARCHAR(50) COMMENT '组织ID',
    role VARCHAR(20) DEFAULT 'user' COMMENT '角色: admin/user/guest',
    avatar TEXT COMMENT '头像URL',
    status VARCHAR(20) DEFAULT 'active' COMMENT '状态: active/inactive/banned',
    last_login_at TIMESTAMP COMMENT '最后登录时间',
    settings JSON COMMENT '用户配置JSON',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_organization (organization_id),
    INDEX idx_status (status),
    INDEX idx_role (role),
    INDEX idx_email (email)
) ENGINE=InnoDB COMMENT='用户表';

-- ============================================
-- 3. 员工表 (核心)
-- ============================================
CREATE TABLE IF NOT EXISTS employees (
    id VARCHAR(50) PRIMARY KEY COMMENT '员工ID (如: emp_001)',
    name VARCHAR(100) NOT NULL COMMENT '员工名称',
    description TEXT COMMENT '员工描述',
    avatar TEXT COMMENT '头像URL',
    category JSON COMMENT '分类标签数组 ["客服", "销售"]',
    tags JSON COMMENT '标签数组 ["热门", "推荐"]',
    price VARCHAR(20) DEFAULT '0' COMMENT '价格 (数字或"free"表示免费)',
    original_price INT COMMENT '原价',
    trial_count INT DEFAULT 0 COMMENT '试用次数',
    hire_count INT DEFAULT 0 COMMENT '雇佣次数',
    is_hired BOOLEAN DEFAULT FALSE COMMENT '是否被雇佣',
    is_recruited BOOLEAN DEFAULT FALSE COMMENT '是否被招募',
    status VARCHAR(20) DEFAULT 'draft' COMMENT '状态: draft/published/archived',
    skills JSON COMMENT '技能数组',
    knowledge_base_ids JSON COMMENT '关联知识库ID数组',
    industry VARCHAR(50) COMMENT '行业',
    role VARCHAR(50) COMMENT '角色定位',
    prompt TEXT COMMENT '系统提示词',
    model VARCHAR(50) DEFAULT 'deepseek-chat' COMMENT '使用的AI模型',
    model_config JSON COMMENT '模型配置参数JSON',
    is_hot BOOLEAN DEFAULT FALSE COMMENT '是否热门',
    personality VARCHAR(500) COMMENT '性格描述',
    welcome_message TEXT COMMENT '欢迎语',
    created_by VARCHAR(50) COMMENT '创建者ID',
    organization_id VARCHAR(50) COMMENT '所属组织ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_status (status),
    INDEX idx_created_by (created_by),
    INDEX idx_organization (organization_id),
    INDEX idx_updated_at (updated_at),
    INDEX idx_is_hired (is_hired),
    INDEX idx_is_hot (is_hot),
    FULLTEXT INDEX ft_name_desc (name, description)
) ENGINE=InnoDB COMMENT='数字员工表';

-- ============================================
-- 4. 知识库表
-- ============================================
CREATE TABLE IF NOT EXISTS knowledge_bases (
    id VARCHAR(50) PRIMARY KEY COMMENT '知识库ID',
    name VARCHAR(100) NOT NULL COMMENT '知识库名称',
    description TEXT COMMENT '描述',
    category VARCHAR(50) COMMENT '分类',
    doc_count INT DEFAULT 0 COMMENT '文档数量',
    created_by VARCHAR(50) COMMENT '创建者ID',
    organization_id VARCHAR(50) COMMENT '所属组织ID',
    status VARCHAR(20) DEFAULT 'active' COMMENT '状态: active/inactive/processing',
    tags JSON COMMENT '标签数组',
    is_public BOOLEAN DEFAULT TRUE COMMENT '是否公开',
    vectorized BOOLEAN DEFAULT FALSE COMMENT '是否已向量化',
    embedding_model VARCHAR(50) DEFAULT 'text-embedding-3-small' COMMENT '嵌入模型',
    vector_store_path TEXT COMMENT '向量存储路径',
    settings JSON COMMENT '知识库配置JSON',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_created_by (created_by),
    INDEX idx_organization (organization_id),
    INDEX idx_status (status),
    INDEX idx_vectorized (vectorized),
    INDEX idx_is_public (is_public),
    FULLTEXT INDEX ft_name_desc (name, description)
) ENGINE=InnoDB COMMENT='知识库表';

-- ============================================
-- 5. 用户-知识库权限关联表 (新增)
-- ============================================
CREATE TABLE IF NOT EXISTS user_knowledge_bases (
    id VARCHAR(50) PRIMARY KEY COMMENT '记录ID',
    user_id VARCHAR(50) NOT NULL COMMENT '用户ID',
    knowledge_base_id VARCHAR(50) NOT NULL COMMENT '知识库ID',
    permission VARCHAR(20) DEFAULT 'read' COMMENT '权限: read/write/admin',
    granted_by VARCHAR(50) COMMENT '授权者ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    UNIQUE KEY uk_user_kb (user_id, knowledge_base_id),
    INDEX idx_user_id (user_id),
    INDEX idx_kb_id (knowledge_base_id),
    INDEX idx_permission (permission)
) ENGINE=InnoDB COMMENT='用户知识库权限关联表';

-- ============================================
-- 6. 知识点表
-- ============================================
CREATE TABLE IF NOT EXISTS knowledge_items (
    id VARCHAR(50) PRIMARY KEY COMMENT '知识点ID',
    knowledge_base_id VARCHAR(50) NOT NULL COMMENT '所属知识库ID',
    serial_no INT NOT NULL COMMENT '序号',
    content TEXT NOT NULL COMMENT '知识内容',
    word_count INT DEFAULT 0 COMMENT '字数',
    source_file VARCHAR(255) COMMENT '源文件',
    metadata JSON COMMENT '元数据',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    INDEX idx_kb_id (knowledge_base_id),
    INDEX idx_serial_no (knowledge_base_id, serial_no),
    FULLTEXT INDEX ft_content (content)
) ENGINE=InnoDB COMMENT='知识点表';

-- ============================================
-- 7. 向量存储元数据表 (新增)
-- ============================================
CREATE TABLE IF NOT EXISTS vector_metadata (
    id VARCHAR(50) PRIMARY KEY COMMENT '记录ID',
    knowledge_base_id VARCHAR(50) NOT NULL COMMENT '知识库ID',
    item_id VARCHAR(50) NOT NULL COMMENT '知识点ID',
    embedding_model VARCHAR(50) COMMENT '嵌入模型',
    vector_id VARCHAR(100) COMMENT '向量数据库中的ID',
    chunk_index INT DEFAULT 0 COMMENT '分块索引',
    chunk_text TEXT COMMENT '分块文本内容',
    metadata JSON COMMENT '向量元数据',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    INDEX idx_kb_item (knowledge_base_id, item_id),
    INDEX idx_vector_id (vector_id),
    INDEX idx_embedding_model (embedding_model)
) ENGINE=InnoDB COMMENT='向量存储元数据表';

-- ============================================
-- 8. 文档表
-- ============================================
CREATE TABLE IF NOT EXISTS documents (
    id VARCHAR(50) PRIMARY KEY COMMENT '文档ID',
    knowledge_base_id VARCHAR(50) NOT NULL COMMENT '所属知识库ID',
    file_name VARCHAR(255) NOT NULL COMMENT '文件名',
    file_path TEXT NOT NULL COMMENT '存储路径',
    file_size BIGINT COMMENT '文件大小(字节)',
    mime_type VARCHAR(100) COMMENT '文件类型',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态: pending/parsed/processing/error',
    parse_result JSON COMMENT '解析结果',
    error_message TEXT COMMENT '错误信息',
    parsed_at TIMESTAMP COMMENT '解析完成时间',
    created_by VARCHAR(50) COMMENT '上传者ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    INDEX idx_kb_id (knowledge_base_id),
    INDEX idx_status (status),
    INDEX idx_created_by (created_by)
) ENGINE=InnoDB COMMENT='文档表';

-- ============================================
-- 9. 对话表
-- ============================================
CREATE TABLE IF NOT EXISTS conversations (
    id VARCHAR(50) PRIMARY KEY COMMENT '会话ID',
    employee_id VARCHAR(50) NOT NULL COMMENT '员工ID',
    user_id VARCHAR(50) COMMENT '用户ID (匿名用户为NULL)',
    organization_id VARCHAR(50) COMMENT '组织ID',
    title VARCHAR(200) COMMENT '会话标题',
    message_count INT DEFAULT 0 COMMENT '消息数量',
    status VARCHAR(20) DEFAULT 'active' COMMENT '状态: active/archived/deleted',
    metadata JSON COMMENT '会话元数据',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_employee_user (employee_id, user_id),
    INDEX idx_user_id (user_id),
    INDEX idx_organization (organization_id),
    INDEX idx_updated_at (updated_at),
    INDEX idx_status (status)
) ENGINE=InnoDB COMMENT='对话表';

-- ============================================
-- 10. 消息表
-- ============================================
CREATE TABLE IF NOT EXISTS messages (
    id VARCHAR(50) PRIMARY KEY COMMENT '消息ID',
    conversation_id VARCHAR(50) NOT NULL COMMENT '所属会话ID',
    role VARCHAR(20) NOT NULL COMMENT '角色: user/assistant/system',
    content TEXT NOT NULL COMMENT '消息内容',
    token_count INT COMMENT 'Token数量',
    model VARCHAR(50) COMMENT '使用的模型',
    metadata JSON COMMENT '元数据 (耗时、检索结果等)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    INDEX idx_conversation_id (conversation_id, created_at),
    INDEX idx_role (role),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB COMMENT='消息表';

-- ============================================
-- 11. 雇佣记录表
-- ============================================
CREATE TABLE IF NOT EXISTS hire_records (
    id VARCHAR(50) PRIMARY KEY COMMENT '记录ID',
    employee_id VARCHAR(50) NOT NULL COMMENT '员工ID',
    user_id VARCHAR(50) NOT NULL COMMENT '用户ID',
    organization_id VARCHAR(50) COMMENT '组织ID',
    hired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '雇佣时间',
    expired_at TIMESTAMP COMMENT '过期时间',
    status VARCHAR(20) DEFAULT 'active' COMMENT '状态: active/cancelled/expired',
    settings JSON COMMENT '雇佣配置JSON',
    
    INDEX idx_employee_id (employee_id),
    INDEX idx_user_id (user_id),
    INDEX idx_organization (organization_id),
    INDEX idx_status (status),
    INDEX idx_hired_at (hired_at),
    UNIQUE KEY uk_employee_user (employee_id, user_id, status)
) ENGINE=InnoDB COMMENT='雇佣记录表';

-- ============================================
-- 12. 试用记录表 (新增)
-- ============================================
CREATE TABLE IF NOT EXISTS trial_records (
    id VARCHAR(50) PRIMARY KEY COMMENT '记录ID',
    employee_id VARCHAR(50) NOT NULL COMMENT '员工ID',
    user_id VARCHAR(50) NOT NULL COMMENT '用户ID',
    organization_id VARCHAR(50) COMMENT '组织ID',
    trialed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '试用时间',
    feedback TEXT COMMENT '试用反馈',
    rating INT COMMENT '评分 1-5',
    
    INDEX idx_employee_id (employee_id),
    INDEX idx_user_id (user_id),
    INDEX idx_trialed_at (trialed_at)
) ENGINE=InnoDB COMMENT='试用记录表';

-- ============================================
-- 外键约束 (可选，根据性能需求决定是否添加)
-- ============================================

-- 如果启用外键约束，取消下面的注释
/*
ALTER TABLE users 
    ADD CONSTRAINT fk_users_organization 
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE SET NULL;

ALTER TABLE employees 
    ADD CONSTRAINT fk_employees_created_by 
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    ADD CONSTRAINT fk_employees_organization 
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE SET NULL;

ALTER TABLE knowledge_bases 
    ADD CONSTRAINT fk_kb_created_by 
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    ADD CONSTRAINT fk_kb_organization 
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE SET NULL;

ALTER TABLE user_knowledge_bases 
    ADD CONSTRAINT fk_ukb_user 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    ADD CONSTRAINT fk_ukb_kb 
    FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE;

ALTER TABLE knowledge_items 
    ADD CONSTRAINT fk_items_kb 
    FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE;

ALTER TABLE vector_metadata 
    ADD CONSTRAINT fk_vector_kb 
    FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    ADD CONSTRAINT fk_vector_item 
    FOREIGN KEY (item_id) REFERENCES knowledge_items(id) ON DELETE CASCADE;

ALTER TABLE documents 
    ADD CONSTRAINT fk_docs_kb 
    FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    ADD CONSTRAINT fk_docs_created_by 
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL;

ALTER TABLE conversations 
    ADD CONSTRAINT fk_conv_employee 
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    ADD CONSTRAINT fk_conv_user 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    ADD CONSTRAINT fk_conv_organization 
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE SET NULL;

ALTER TABLE messages 
    ADD CONSTRAINT fk_msg_conv 
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE;

ALTER TABLE hire_records 
    ADD CONSTRAINT fk_hire_employee 
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    ADD CONSTRAINT fk_hire_user 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    ADD CONSTRAINT fk_hire_organization 
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE SET NULL;

ALTER TABLE trial_records 
    ADD CONSTRAINT fk_trial_employee 
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    ADD CONSTRAINT fk_trial_user 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
*/

-- ============================================
-- 使用说明
-- ============================================
/*
1. 执行前确保MySQL版本 >= 8.0 (支持JSON类型)
2. 如果需要向量搜索功能，建议使用专门的向量数据库(如Milvus)或在应用层实现
3. 外键约束默认注释掉，生产环境根据需要启用
4. 字符集使用utf8mb4，支持emoji和特殊字符
5. 所有表使用InnoDB引擎，支持事务

执行命令:
mysql -u root -p < 001_initial_schema_mysql.sql

版本更新记录:
v1.1 (2026-02-09):
  - 添加 organizations 组织表
  - 添加 user_knowledge_bases 权限关联表
  - 添加 vector_metadata 向量元数据表
  - 添加 trial_records 试用记录表
  - 优化 employees.price 字段类型为 VARCHAR(20) 支持 "free"
  - 添加 employees.model_config, welcome_message 等字段
  - 优化索引设计
  - 完善外键约束
*/
