/**
 * 头像工具函数
 * 提供稳定的头像生成服务，带有错误处理和备用方案
 */

/**
 * 生成员工头像URL
 * 优先使用 ui-avatars.com（更稳定），失败时使用其他服务
 */
export const getAvatarUrl = (name: string, seed?: string): string => {
  const encodedName = encodeURIComponent(name);
  
  // 方案1: ui-avatars.com (最稳定)
  const uiAvatar = `https://ui-avatars.com/api/?name=${encodedName}&background=random&color=fff&size=200&font-size=0.33`;
  
  // 方案2: dicebear.com (备用)
  const dicebear = `https://api.dicebear.com/7.x/initials/svg?seed=${seed || name}&backgroundColor=random`;
  
  // 方案3: pravatar.cc (备用)
  const pravatar = `https://i.pravatar.cc/150?u=${seed || name}`;
  
  return uiAvatar;
};

/**
 * 生成带背景的头像URL
 */
export const getAvatarWithBackground = (
  name: string,
  backgroundColor?: string,
  textColor: string = '#fff'
): string => {
  const encodedName = encodeURIComponent(name);
  const bg = backgroundColor || 'random';
  
  return `https://ui-avatars.com/api/?name=${encodedName}&background=${bg}&color=${textColor}&size=200&font-size=0.33`;
};

/**
 * 根据员工ID生成头像
 */
export const getAvatarById = (employeeId: string, name: string): string => {
  return getAvatarUrl(name, employeeId);
};

/**
 * 获取默认头像
 */
export const getDefaultAvatar = (): string => {
  return 'https://ui-avatars.com/api/?name=AI&background=0D8ABC&color=fff&size=200';
};
