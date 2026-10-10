export class ApiError extends Error {
  status: number
  detail: unknown

  constructor(status: number, message: string, detail: unknown) {
    super(message)
    this.status = status
    this.detail = detail
  }
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const res = await fetch(`/api${path}`, {
    method,
    headers: body === undefined ? undefined : { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  if (!res.ok) {
    const data = await res.json().catch(() => null)
    const detail = data?.detail
    const message =
      typeof detail === 'string' ? detail : (detail?.message ?? `${method} /api${path} failed: ${res.status}`)
    throw new ApiError(res.status, message, detail)
  }
  return (res.status === 204 ? undefined : await res.json()) as T
}

export const api = {
  get: <T>(path: string) => request<T>('GET', path),
  post: <T>(path: string, body: unknown) => request<T>('POST', path, body),
  put: <T>(path: string, body: unknown) => request<T>('PUT', path, body),
  delete: (path: string) => request<void>('DELETE', path),
}

export type RecipeDraft = {
  title: string
  source_type: 'manual' | 'url' | 'video'
  source_url: string | null
  image_url: string | null
  servings: number | null
  total_minutes: number | null
  tags: string[]
  ingredients: string[]
  steps: string[]
}

export type ParsedIngredient = {
  raw: string
  quantity: number | null
  quantity_max: number | null
  unit: string | null
  name: string | null
  note: string | null
}

export type Ingredient = ParsedIngredient & { id: number; position: number }

export type Step = { id: number; position: number; text: string }

export type RecipeSummary = {
  id: number
  title: string
  image_url: string | null
  servings: number | null
  total_minutes: number | null
  tags: string[]
}

export type Recipe = RecipeSummary & {
  source_type: RecipeDraft['source_type']
  source_url: string | null
  created_at: string
  updated_at: string
  ingredients: Ingredient[]
  steps: Step[]
}

export function toDraft(recipe: Recipe): RecipeDraft {
  return {
    title: recipe.title,
    source_type: recipe.source_type,
    source_url: recipe.source_url,
    image_url: recipe.image_url,
    servings: recipe.servings,
    total_minutes: recipe.total_minutes,
    tags: recipe.tags,
    ingredients: recipe.ingredients.map((i) => i.raw),
    steps: recipe.steps.map((s) => s.text),
  }
}
