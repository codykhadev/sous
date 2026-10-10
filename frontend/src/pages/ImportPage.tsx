import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router'
import { api, ApiError, type RecipeDraft } from '../api/client'

type Failure = { message: string; existingId?: number }

export default function ImportPage() {
  const navigate = useNavigate()
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [failure, setFailure] = useState<Failure | null>(null)

  async function submit(e: FormEvent) {
    e.preventDefault()
    setLoading(true)
    setFailure(null)
    try {
      const draft = await api.post<RecipeDraft>('/import/url', { url })
      navigate('/recipes/new', { state: { draft } })
    } catch (err) {
      const existingId =
        err instanceof ApiError && err.status === 409
          ? (err.detail as { recipe_id: number }).recipe_id
          : undefined
      setFailure({ message: err instanceof Error ? err.message : 'Import failed.', existingId })
      setLoading(false)
    }
  }

  return (
    <section className="mx-auto max-w-2xl">
      <h1 className="font-display text-4xl font-bold">Import a recipe</h1>
      <p className="mt-2 text-ink/70">
        Paste a link to a recipe page. You'll get to review and edit it before it's saved.
      </p>

      <form onSubmit={submit} className="mt-6 flex flex-col gap-3 sm:flex-row">
        <input
          type="url"
          required
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://…"
          aria-label="Recipe link"
          disabled={loading}
          className="flex-1 rounded-lg border border-ink/20 bg-white px-4 py-2.5 outline-none focus:border-paprika"
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-paprika px-6 py-2.5 font-medium text-white hover:bg-paprika/90 disabled:opacity-60"
        >
          {loading ? 'Reading recipe…' : 'Import'}
        </button>
      </form>

      {failure && (
        <div role="alert" className="mt-6 rounded-lg border border-paprika/30 bg-paprika/5 p-4">
          <p>{failure.message}</p>
          <div className="mt-3 flex gap-4 text-sm font-medium">
            {failure.existingId ? (
              <Link to={`/recipes/${failure.existingId}`} className="text-paprika underline">
                Open the saved recipe
              </Link>
            ) : (
              <Link to="/recipes/new" className="text-paprika underline">
                Add it manually instead
              </Link>
            )}
          </div>
        </div>
      )}
    </section>
  )
}
