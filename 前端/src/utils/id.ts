/** 生成唯一 ID（时间戳 + 随机串，本地 mock 使用；真实场景由后端生成主键） */
export function genId(prefix = ''): string {
  const rand = Math.random().toString(36).slice(2, 8)
  const time = Date.now().toString(36)
  return `${prefix}${time}${rand}`
}

/** 今天的日期字符串 YYYY-MM-DD */
export function today(): string {
  return new Date().toISOString().slice(0, 10)
}

/** 距今天偏移 n 天的日期字符串 */
export function offsetDate(days: number): string {
  const d = new Date()
  d.setDate(d.getDate() + days)
  return d.toISOString().slice(0, 10)
}