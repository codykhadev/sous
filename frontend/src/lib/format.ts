const FRACTIONS: [number, string][] = [
  [1 / 8, '⅛'],
  [1 / 4, '¼'],
  [1 / 3, '⅓'],
  [3 / 8, '⅜'],
  [1 / 2, '½'],
  [5 / 8, '⅝'],
  [2 / 3, '⅔'],
  [3 / 4, '¾'],
  [7 / 8, '⅞'],
]

export function formatNumber(value: number): string {
  const whole = Math.floor(value)
  const rest = value - whole
  if (rest < 0.04) return String(whole)
  if (rest > 0.96) return String(whole + 1)
  const match = FRACTIONS.find(([f]) => Math.abs(rest - f) < 0.04)
  if (!match) return String(Math.round(value * 100) / 100)
  return whole ? `${whole} ${match[1]}` : match[1]
}

export function formatQuantity(quantity: number | null, max: number | null): string {
  if (quantity === null) return ''
  return max === null ? formatNumber(quantity) : `${formatNumber(quantity)}–${formatNumber(max)}`
}

export function formatMinutes(minutes: number | null): string | null {
  if (!minutes) return null
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  if (!h) return `${m} min`
  return m ? `${h} hr ${m} min` : `${h} hr`
}
