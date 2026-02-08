import React from 'react';
import { Edit, Trash2 } from 'lucide-react';
import { Employee } from '@/shared/types/employee';

export interface EmployeeCardProps {
  employee: Employee;
  onClick: (employeeId: string) => void;
  variant?: 'default' | 'created';
  onEdit?: (employeeId: string) => void;
  onDelete?: (employeeId: string) => void;
}

export const EmployeeCard: React.FC<EmployeeCardProps> = ({
  employee,
  onClick,
  variant = 'default',
  onEdit,
  onDelete,
}) => {
  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    onEdit?.(employee.id);
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDelete?.(employee.id);
  };

  return (
    <div 
      className="group relative flex flex-col items-center bg-white rounded-lg p-6 shadow-sm border border-slate-100 hover:shadow-lg transition-all duration-300 cursor-pointer h-full"
      onClick={() => onClick(employee.id)}
    >
      {/* "Recruited" Stamp (Only for default view) */}
      {variant === 'default' && employee.isRecruited && (
        <div className="absolute top-4 right-4 text-xs font-medium text-blue-500 border border-blue-200 px-2 py-0.5 rounded bg-blue-50 transform rotate-12 z-10">
          已招聘
        </div>
      )}

      {/* Avatar */}
      <div className="w-20 h-20 mb-4 rounded-full overflow-hidden border-2 border-slate-50 shadow-sm group-hover:scale-105 transition-transform shrink-0">
        <img
          src={employee.avatar || `https://ui-avatars.com/api/?name=${employee.name}&background=random`}
          alt={employee.name}
          className="w-full h-full object-cover"
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(employee.name)}&background=random`;
          }}
        />
      </div>

      {/* Name */}
      <h3 className="text-lg font-bold text-slate-900 mb-2 text-center truncate w-full px-2">
        {employee.name}
      </h3>

      {/* Description */}
      <p className="text-sm text-slate-500 text-center mb-4 line-clamp-2 h-10 leading-relaxed w-full">
        {employee.description || '暂无描述'}
      </p>

      {/* Tags/Stats Row 1 */}
      <div className="flex items-center justify-center space-x-3 text-xs text-slate-400 mb-auto w-full pb-4">
        <div className="flex items-center">
          <span className="mr-1">◎</span>
          <span>{employee.industry || employee.category?.[0] || '通用'}</span>
        </div>
        {variant === 'default' && (
          <>
            <div className="flex items-center">
              <span className="mr-1">{employee.trialCount || 0}</span>
              <span>试用</span>
            </div>
            <div className="flex items-center">
              <span className="mr-1">{employee.hireCount || 0}</span>
              <span>招聘</span>
            </div>
          </>
        )}
      </div>

      {/* Bottom Section: Price OR Action Buttons */}
      <div className="w-full mt-2 pt-3 border-t border-slate-50">
        {variant === 'created' ? (
          <div className="flex items-center space-x-3">
            <button 
              onClick={handleEdit}
              className="flex-1 flex items-center justify-center space-x-1 py-1.5 rounded-md border border-blue-200 text-blue-600 hover:bg-blue-50 text-xs font-medium transition-colors"
            >
              <Edit size={12} />
              <span>修改编辑</span>
            </button>
            <button 
              onClick={handleDelete}
              className="flex-1 flex items-center justify-center space-x-1 py-1.5 rounded-md border border-red-200 text-red-500 hover:bg-red-50 text-xs font-medium transition-colors"
            >
              <Trash2 size={12} />
              <span>解雇</span>
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center space-y-1">
            <div className="flex items-center space-x-2">
              <span className="text-red-500 font-bold text-lg">
                {employee.price === 'free' ? '免费' : `¥${employee.price}/年`}
              </span>
              <span className="bg-amber-100 text-amber-700 text-[10px] px-1.5 py-0.5 rounded font-medium">
                专业版免费
              </span>
            </div>
            {employee.originalPrice && (
              <span className="text-slate-300 text-xs line-through">
                ¥{employee.originalPrice}/年
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};