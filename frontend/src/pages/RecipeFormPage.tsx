import { useEffect, useState, type FormEvent, type ReactNode } from 'react'
import { Link, useLocation, useNavigate, useParams } from 'react-router'
import { api, toDraft, type ParsedIngredient, type Recipe, type RecipeDraft } from '../api/client'
import { useDebounced } from '../hooks/useDebounced'
import { formatQuantity } from '../lib/format'

type FormState = {
  title: string
  servings: string
  totalMinutes: string
  imageUrl: string
  tags: string
  ingredients: string
  steps: string
}

const EMPTY_DRAFT: RecipeDraft = {
  title: '',
  source_type: 'manual',
  source_url: null,
  image_url: null,
  servings: null,
  total_minutes: null,
  tags: [],
  ingredients: [],
  steps: [],
}

function toForm(draft: RecipeDraft): FormState {
  return {
    title: draft.title,
    servings: draft.servings?.toString() ?? '',
    totalMinutes: draft.total_minutes?.toString() ?? '',
    imageUrl: draft.image_url ?? '',
    tags: draft.tags.join(', '),
    ingredients: draft.ingredients.join('\n'),
    steps: draft.steps.join('\n'),
  }
}

function lines(text: string): string[] {
  return text
    .split('\n')
    .map((l) => l.trim())
    .filter(Boolean)
}

function toNumber(text: string): number | null {
  const n = parseInt(text, 10)
  return Number.isNaN(n) ? null : n
}

const inputClass =
  'w-full rounded-lg border border-ink/20 bg-white px-3 py-2 outline-none focus:border-paprika'

function Field({ label, hint, children }: { label: string; hint?: string; children: ReactNode }) {
  return (
    <label className="block">
      <span className="font-medium">{label}</span>
      {hint && <span className="ml-2 text-sm text-ink/50">{hint}</span>}
      <div className="mt-1">{children}</div>
    </label>
  )
}

export default function RecipeFormPage() {
  const { id } = useParams()
  const location = useLocation()
  const navigate = useNavigate()
  const importedDraft = (location.state as { draft?: RecipeDraft } | null)?.draft

  const [base, setBase] = useState<RecipeDraft | null>(id ? null : (importedDraft ?? EMPTY_DRAFT))
  const [form, setForm] = useState<FormState | null>(base ? toForm(base) : null)
  const [preview, setPreview] = useState<ParsedIngredient[]>([])
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const ingredientText = useDebounced(form?.ingredients ?? '', 300)

  useEffect(() => {
    if (!id) return
    api
      .get<Recipe>(`/recipes/${id}`)
      .then((r) => {
        const draft = toDraft(r)
        setBase(draft)
        setForm(toForm(draft))
      })
      .catch((e: Error) => setError(e.message))
  }, [id])

  useEffect(() => {
    const ingredientLines = lines(ingredientText)
    if (!ingredientLines.length) return
    let cancelled = false
    api
      .post<ParsedIngredient[]>('/ingredients/parse', { lines: ingredientLines })
      .then((p) => !cancelled && setPreview(p))
      .catch(() => !cancelled && setPreview([]))
    return () => {
      cancelled = true
    }
  }, [ingredientText])

  if (!form || !base) {
    return <p className="text-ink/60">{error ?? 'Loading…'}</p>
  }

  const set = (key: keyof FormState) => (e: { target: { value: string } }) =>
    setForm({ ...form, [key]: e.target.value })

  async function submit(e: FormEvent) {
    e.preventDefault()
    if (!form || !base) return
    setSaving(true)
    setError(null)
    const body: RecipeDraft = {
      ...base,
      title: form.title,
      servings: toNumber(form.servings),
      total_minutes: toNumber(form.totalMinutes),
      image_url: form.imageUrl.trim() || null,
      tags: form.tags.split(',').map((t) => t.trim()).filter(Boolean),
      ingredients: lines(form.ingredients),
      steps: lines(form.steps),
    }
    try {
      const saved = id ? await api.put<Recipe>(`/recipes/${id}`, body) : await api.post<Recipe>('/recipes', body)
      navigate(`/recipes/${saved.id}`, { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Save failed.')
      setSaving(false)
    }
  }

  const shownPreview = lines(ingredientText).length ? preview : []
  const heading = id ? 'Edit recipe' : importedDraft ? 'Review imported recipe' : 'Add a recipe'

  return (
    <form onSubmit={submit} className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="font-display text-4xl font-bold">{heading}</h1>
        {importedDraft && (
          <p className="mt-2 text-ink/70">
            Imported from{' '}
            <a href={importedDraft.source_url ?? '#'} target="_blank" rel="noreferrer" className="underline">
              {importedDraft.source_url && new URL(importedDraft.source_url).hostname}
            </a>
            . Fix anything that looks off, then save.
          </p>
        )}
      </div>

      <Field label="Title">
        <input required value={form.title} onChange={set('title')} className={inputClass} />
      </Field>

      <div className="grid gap-4 sm:grid-cols-3">
        <Field label="Servings">
          <input type="number" min={1} value={form.servings} onChange={set('servings')} className={inputClass} />
        </Field>
        <Field label="Total time" hint="minutes">
          <input
            type="number"
            min={0}
            value={form.totalMinutes}
            onChange={set('totalMinutes')}
            className={inputClass}
          />
        </Field>
        <Field label="Tags" hint="comma separated">
          <input value={form.tags} onChange={set('tags')} placeholder="dinner, quick" className={inputClass} />
        </Field>
      </div>

      <Field label="Image link" hint="optional">
        <input type="url" value={form.imageUrl} onChange={set('imageUrl')} className={inputClass} />
      </Field>

      <div>
        <Field label="Ingredients" hint="one per line">
          <textarea
            rows={Math.max(6, lines(form.ingredients).length + 1)}
            value={form.ingredients}
            onChange={set('ingredients')}
            placeholder={'2 cups flour\n1 tsp salt'}
            className={`${inputClass} font-mono text-sm`}
          />
        </Field>
        {shownPreview.length > 0 && (
          <div className="mt-3 rounded-lg bg-white p-3 ring-1 ring-ink/10">
            <p className="mb-2 text-sm font-medium text-ink/60">How Sous reads these</p>
            <table className="w-full text-sm">
              <thead className="text-left text-ink/50">
                <tr>
                  <th className="pr-3 font-normal">Amount</th>
                  <th className="pr-3 font-normal">Unit</th>
                  <th className="pr-3 font-normal">Ingredient</th>
                  <th className="font-normal">Note</th>
                </tr>
              </thead>
              <tbody>
                {shownPreview.map((p, i) => (
                  <tr key={i} className="border-t border-ink/5 align-top">
                    <td className="py-1 pr-3 whitespace-nowrap">{formatQuantity(p.quantity, p.quantity_max)}</td>
                    <td className="py-1 pr-3">{p.unit}</td>
                    <td className="py-1 pr-3 font-medium">{p.name}</td>
                    <td className="py-1 text-ink/60">{p.note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <Field label="Steps" hint="one per line">
        <textarea
          rows={Math.max(6, lines(form.steps).length * 2)}
          value={form.steps}
          onChange={set('steps')}
          className={`${inputClass} text-sm leading-relaxed`}
        />
      </Field>

      {error && (
        <p role="alert" className="text-red-700">
          {error}
        </p>
      )}

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={saving}
          className="rounded-lg bg-paprika px-6 py-2.5 font-medium text-white hover:bg-paprika/90 disabled:opacity-60"
        >
          {saving ? 'Saving…' : 'Save recipe'}
        </button>
        <Link
          to={id ? `/recipes/${id}` : '/'}
          className="rounded-lg border border-ink/20 px-6 py-2.5 font-medium hover:bg-ink/5"
        >
          Cancel
        </Link>
      </div>
    </form>
  )
}
