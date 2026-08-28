// 前端全局配置（后端接入时在此切换真实接口）
export const API_CONFIG = {
  /** 当前阶段使用本地 mock；后端就绪后置为 false 并设置 baseURL */
  useMock: false,
  /** 真实后端接口前缀（useMock=false 时生效） */
  baseURL: '/api',
  /** token 存储键名 */
  tokenKey: 'lab_token',
  /** 当前用户信息存储键名 */
  userKey: 'lab_user',
  /** mock 模拟网络延迟（毫秒），便于演示异步加载效果 */
  mockDelay: 250,
}