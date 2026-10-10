import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router'
import { api, type Recipe } from '../api/client'
import { formatMinutes } from '../lib/format'

export default function RecipeDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [recipe, setRecipe] = useState<Recipe | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .get<Recipe>(`/recipes/${id}`)
      .then(setRecipe)
      .catch((e: Error) => setError(e.message))
  }, [id])

  async function remove() {
    if (!recipe || !window.confirm(`Delete "${recipe.title}"? This can't be undone.`)) return
    await api.delete(`/recipes/${recipe.id}`)
    navigate('/', { replace: true })
  }

  if (error) {
    return (
      <section>
        <p className="text-ink/70">{error}</p>
        <Link to="/" className="mt-4 inline-block text-paprika underline">
          Back to your recipes
        </Link>
      </section>
    )
  }
  if (!recipe) return <p className="text-ink/60">Loading…</p>

  const meta = [
    formatMinutes(recipe.total_minutes),
    recipe.servings && `Serves ${recipe.servings}`,
  ].filter(Boolean)

  return (
    <article className="mx-auto max-w-3xl">
      {recipe.image_url && (
        <img src={recipe.image_url} alt="" className="mb-6 aspect-[16/9] w-full rounded-xl object-cover" />
      )}

      <h1 className="font-display text-4xl font-bold">{recipe.title}</h1>
      {meta.length > 0 && <p className="mt-2 text-ink/70">{meta.join(' · ')}</p>}
      {recipe.source_url && (
        <a
          href={recipe.source_url}
          target="_blank"
          rel="noreferrer"
          className="mt-1 inline-block text-sm text-ink/50 underline"
        >
          {new URL(recipe.source_url).hostname}
        </a>
      )}

      {recipe.tags.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {recipe.tags.map((t) => (
            <Link
              key={t}
              to={`/?tag=${encodeURIComponent(t)}`}
              className="rounded-full bg-ink/5 px-3 py-1 text-sm text-ink/80 hover:bg-ink/10"
            >
              {t}
            </Link>
          ))}
        </div>
      )}

      <div className="mt-6 flex flex-wrap gap-3">
        <button
          type="button"
          disabled
          title="Cook mode is coming in stage 3"
          className="rounded-lg bg-paprika px-5 py-2 font-medium text-white opacity-50"
        >
          Start cooking
        </button>
        <Link to={`/recipes/${recipe.id}/edit`} className="rounded-lg border border-ink/20 px-5 py-2 font-medium hover:bg-ink/5">
          Edit
        </Link>
        <button
          type="button"
          onClick={remove}
          className="rounded-lg border border-ink/20 px-5 py-2 font-medium text-red-700 hover:bg-red-50"
        >
          Delete
        </button>
      </div>

      <div className="mt-10 grid gap-10 md:grid-cols-[2fr_3fr]">
        <section>
          <h2 className="font-display text-2xl font-semibold">Ingredients</h2>
          <ul className="mt-4 space-y-2">
            {recipe.ingredients.map((i) => (
              <li key={i.id} className="border-b border-ink/10 pb-2">
                {i.raw}
              </li>
            ))}
          </ul>
        </section>
        <section>
          <h2 className="font-display text-2xl font-semibold">Steps</h2>
          <ol className="mt-4 space-y-5">
            {recipe.steps.map((s, n) => (
              <li key={s.id} className="flex gap-4">
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-paprika text-sm font-semibold text-white">
                  {n + 1}
                </span>
                <p className="leading-relaxed">{s.text}</p>
              </li>
            ))}
          </ol>
        </section>
      </div>
    </article>
  )
}
