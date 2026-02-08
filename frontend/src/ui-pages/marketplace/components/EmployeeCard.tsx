import React, { useState } from 'react';
import { Employee } from '../types';

export interface EmployeeCardProps {
  employee: Employee;
  onClick: (employeeId: string) => void;
  // onHireClick is deprecated in favor of unified onClick handler that decides action based on status
  onHireClick?: (employeeId: string) => void; 
}

export const EmployeeCard: React.FC<EmployeeCardProps> = ({
  employee,
  onClick,
}) => {
  const [imgError, setImgError] = useState(false);
  const [imgLoaded, setImgLoaded] = useState(false);

  const handleImageError = () => {
    setImgError(true);
  };

  const handleImageLoad = () => {
    setImgLoaded(true);
  };

  const getAvatarUrl = () => {
    if (imgError) {
      return `https://ui-avatars.com/api/?name=${encodeURIComponent(employee.name)}&background=random&color=fff&size=200&font-size=0.33`;
    }
    return employee.avatar;
  };

  return (
    <div 
      className="group relative flex flex-col items-center bg-white rounded-lg p-6 shadow-sm border border-slate-100 hover:shadow-lg transition-all duration-300 cursor-pointer"
      onClick={() => onClick(employee.id)}
    >
      {/* "Recruited" Stamp */}
      {employee.isHired && (
        <div className="absolute top-4 right-4 text-xs font-medium text-blue-500 border border-blue-200 px-2 py-0.5 rounded bg-blue-50 transform rotate-12 z-10">
          已招聘
        </div>
      )}

      {/* Avatar */}
      <div className="w-20 h-20 mb-4 rounded-full overflow-hidden border-2 border-slate-50 shadow-sm group-hover:scale-105 transition-transform">
        {!imgLoaded && (
          <div className="w-full h-full bg-slate-100 flex items-center justify-center">
            <div className="w-6 h-6 border-2 border-slate-300 border-t-transparent rounded-full animate-spin"></div>
          </div>
        )}
        <img
          src={getAvatarUrl()}
          alt={employee.name}
          className={`w-full h-full object-cover transition-opacity duration-300 ${imgLoaded ? 'opacity-100' : 'opacity-0'}`}
          onError={handleImageError}
          onLoad={handleImageLoad}
        />
      </div>

      {/* Name */}
      <h3 className="text-lg font-bold text-slate-900 mb-2 text-center">
        {employee.name}
      </h3>

      {/* Description */}
      <p className="text-sm text-slate-500 text-center mb-4 line-clamp-2 h-10 leading-relaxed">
        {employee.description}
      </p>

      {/* Tags/Stats Row 1 */}
      <div className="flex items-center justify-center space-x-3 text-xs text-slate-400 mb-4 w-full">
        <div className="flex items-center">
          <span className="mr-1">◎</span>
          <span>行业专家</span>
        </div>
        <div className="flex items-center">
          <span className="mr-1">{employee.trialCount}</span>
          <span>试用</span>
        </div>
        <div className="flex items-center">
          <span className="mr-1">{employee.hireCount}</span>
          <span>招聘</span>
        </div>
      </div>

      {/* Price Section */}
      <div className="flex flex-col items-center justify-center space-y-1 mb-4">
        <div className="flex items-center space-x-2">
          <span className="text-red-500 font-bold text-lg">
            {typeof employee.price === 'number' ? `¥${employee.price}/年` : '免费'}
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
    </div>
  );
};
