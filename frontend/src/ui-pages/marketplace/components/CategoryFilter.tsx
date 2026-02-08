import React from 'react';
import { Category } from '../types';

export interface CategoryFilterProps {
  categories: Category[];
  activeCategoryId: string | null;
  onChange: (categoryId: string) => void;
}

export const CategoryFilter: React.FC<CategoryFilterProps> = ({
  categories,
  activeCategoryId,
  onChange,
}) => {
  return (
    <div className="flex items-center space-x-6 overflow-x-auto no-scrollbar py-2">
      {categories.map((category) => {
        const isActive = activeCategoryId === category.id;
        return (
          <button
            key={category.id}
            onClick={() => onChange(category.id)}
            className={`
              whitespace-nowrap text-sm font-medium transition-colors relative pb-2
              ${isActive 
                ? 'text-blue-600' 
                : 'text-slate-600 hover:text-slate-900'
              }
            `}
          >
            {category.name}
            {isActive && (
              <span className="absolute bottom-0 left-0 w-full h-0.5 bg-blue-600 rounded-t-full" />
            )}
          </button>
        );
      })}
    </div>
  );
};
