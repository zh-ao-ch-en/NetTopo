/** 生成唯一 ID（时间戳 + 随机串）；真实主键由后端生成，本地 ID 仅用于临时新对象 */
export function genId(prefix = ''): string {
  const rand = Math.random().toString(36).slice(2, 8)
  const time = Date.now().toString(36)
  return `${prefix}${time}${rand}`
}