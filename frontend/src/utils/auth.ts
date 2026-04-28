// 认证相关的工具函数

/**
 * 从localStorage或Cookie中获取token
 * @returns token字符串或null
 */
export function getTokenFromCookie(): string | null {
  // 先尝试从Cookie中获取token（访问令牌存储在Cookie中）
  const cookie = document.cookie;
  const cookieArray = cookie.split(';');
  for (const item of cookieArray) {
    const [name, value] = item.trim().split('=');
    if (name === 'token') {
      return value;
    }
  }
  
  // 再尝试从localStorage中获取token
  const tokenFromLocalStorage = localStorage.getItem('token');
  if (tokenFromLocalStorage) {
    return tokenFromLocalStorage;
  }
  
  return null;
}

/**
 * 将token存储到localStorage
 * @param token token字符串
 */
export function setTokenToLocalStorage(token: string): void {
  localStorage.setItem('token', token);
}

/**
 * 从localStorage中移除token
 */
export function removeTokenFromLocalStorage(): void {
  localStorage.removeItem('token');
}

/**
 * 检查是否已登录
 * @returns 是否已登录
 */
export function isLoggedIn(): boolean {
  return getTokenFromCookie() !== null;
}
