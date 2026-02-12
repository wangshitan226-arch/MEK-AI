#!/usr/bin/env python3
"""
测试雇佣员工功能
验证修复后的数据库字段和流程
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ['ENV'] = 'test'

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import get_db
from app.db.models import Employee, HireRecord, TrialRecord
from app.services.employee_service import employee_service
from app.db.repositories.employee_repo import employee_repository

def test_hire_employee():
    """测试雇佣员工完整流程"""
    
    # 创建数据库会话
    db = next(get_db())
    
    try:
        print("=" * 80)
        print("测试雇佣员工功能")
        print("=" * 80)
        
        # 1. 获取一个未雇佣的员工
        employee = db.query(Employee).filter(
            Employee.id.like('emp_sys_%'),
            Employee.is_hired == False
        ).first()
        
        if not employee:
            print("❌ 没有找到未雇佣的系统员工")
            return False
        
        print(f"\n1. 选择员工: {employee.id} - {employee.name}")
        print(f"   当前状态: is_hired={employee.is_hired}, is_recruited={employee.is_recruited}")
        
        # 2. 执行雇佣
        print(f"\n2. 执行雇佣操作...")
        result = employee_service.hire_employee(
            db=db,
            employee_id=employee.id,
            user_id="test_user_001",
            organization_id=None
        )
        
        if not result:
            print("❌ 雇佣失败")
            return False
        
        print(f"   ✅ 雇佣成功")
        
        # 3. 验证员工状态更新
        db.refresh(employee)
        print(f"\n3. 验证员工状态:")
        print(f"   is_hired={employee.is_hired}, is_recruited={employee.is_recruited}, hire_count={employee.hire_count}")
        
        if not employee.is_hired or not employee.is_recruited:
            print("❌ 员工状态未正确更新")
            return False
        print("   ✅ 员工状态正确")
        
        # 4. 验证雇佣记录创建
        hire_record = db.query(HireRecord).filter(
            HireRecord.employee_id == employee.id,
            HireRecord.user_id == "test_user_001"
        ).first()
        
        print(f"\n4. 验证雇佣记录:")
        if not hire_record:
            print("❌ 雇佣记录未创建")
            return False
        
        print(f"   记录ID: {hire_record.id}")
        print(f"   员工ID: {hire_record.employee_id}")
        print(f"   用户ID: {hire_record.user_id}")
        print(f"   状态: {hire_record.status}")
        print(f"   创建时间: {hire_record.created_at}")
        print("   ✅ 雇佣记录创建成功")
        
        # 5. 测试重复雇佣（应该失败）
        print(f"\n5. 测试重复雇佣...")
        try:
            result2 = employee_service.hire_employee(
                db=db,
                employee_id=employee.id,
                user_id="test_user_001",
                organization_id=None
            )
            if result2:
                print("❌ 重复雇佣应该失败，但却成功了")
                return False
        except Exception as e:
            print(f"   ✅ 重复雇佣被正确拒绝: {str(e)[:50]}")
        
        print("\n" + "=" * 80)
        print("✅ 所有测试通过！")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_trial_employee():
    """测试试用员工功能"""
    
    db = next(get_db())
    
    try:
        print("\n" + "=" * 80)
        print("测试试用员工功能")
        print("=" * 80)
        
        # 1. 获取一个员工
        employee = db.query(Employee).filter(
            Employee.id.like('emp_sys_%')
        ).first()
        
        if not employee:
            print("❌ 没有找到系统员工")
            return False
        
        print(f"\n1. 选择员工: {employee.id} - {employee.name}")
        old_trial_count = employee.trial_count
        print(f"   当前试用次数: {old_trial_count}")
        
        # 2. 执行试用
        print(f"\n2. 执行试用操作...")
        result = employee_service.trial_employee(
            db=db,
            employee_id=employee.id,
            user_id="test_user_001",
            organization_id=None
        )
        
        if not result:
            print("❌ 试用失败")
            return False
        
        print(f"   ✅ 试用成功")
        
        # 3. 验证试用次数更新
        db.refresh(employee)
        print(f"\n3. 验证试用次数:")
        print(f"   试用次数: {employee.trial_count} (之前: {old_trial_count})")
        
        if employee.trial_count != old_trial_count + 1:
            print("❌ 试用次数未正确更新")
            return False
        print("   ✅ 试用次数正确")
        
        # 4. 验证试用记录创建
        trial_record = db.query(TrialRecord).filter(
            TrialRecord.employee_id == employee.id,
            TrialRecord.user_id == "test_user_001"
        ).order_by(TrialRecord.created_at.desc()).first()
        
        print(f"\n4. 验证试用记录:")
        if not trial_record:
            print("❌ 试用记录未创建")
            return False
        
        print(f"   记录ID: {trial_record.id}")
        print(f"   员工ID: {trial_record.employee_id}")
        print(f"   用户ID: {trial_record.user_id}")
        print(f"   创建时间: {trial_record.created_at}")
        print("   ✅ 试用记录创建成功")
        
        print("\n" + "=" * 80)
        print("✅ 试用测试通过！")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("\n开始测试...\n")
    
    success1 = test_hire_employee()
    success2 = test_trial_employee()
    
    print("\n" + "=" * 80)
    if success1 and success2:
        print("🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("❌ 部分测试失败")
        sys.exit(1)
