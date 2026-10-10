import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router'
import { api, type RecipeSummary } from '../api/client'
import { useDebounced } from '../hooks/useDebounced'
import { formatMinutes } from '../lib/format'

export default function LibraryPage() {
  const [params, setParams] = useSearchParams()
  const tag = params.get('tag')
  const [search, setSearch] = useState('')
  const query = useDebounced(search.trim(), 250)
  const [recipes, setRecipes] = useState<RecipeSummary[] | null>(null)
  const [tags, setTags] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.get<string[]>('/recipes/tags').then(setTags).catch(() => setTags([]))
  }, [])

  useEffect(() => {
    const search = new URLSearchParams()
    if (query) search.set('q', query)
    if (tag) search.set('tag', tag)
    api
      .get<RecipeSummary[]>(`/recipes?${search}`)
      .then((r) => {
        setRecipes(r)
        setError(null)
      })
      .catch((e: Error) => setError(e.message))
  }, [query, tag])

  function toggleTag(t: string) {
    const next = new URLSearchParams(params)
    if (t === tag) next.delete('tag')
    else next.set('tag', t)
    setParams(next, { replace: true })
  }

  const filtering = Boolean(query || tag)

  return (
    <section>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="font-display text-4xl font-bold">Your recipes</h1>
        <div className="flex gap-2">
          <Link to="/recipes/new" className="rounded-lg border border-ink/20 px-4 py-2 font-medium hover:bg-ink/5">
            Add manually
          </Link>
          <Link to="/import" className="rounded-lg bg-paprika px-4 py-2 font-medium text-white hover:bg-paprika/90">
            Import recipe
          </Link>
        </div>
      </div>

      <input
        type="search"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Search by title or ingredient…"
        aria-label="Search recipes"
        className="mt-6 w-full rounded-lg border border-ink/20 bg-white px-4 py-2.5 outline-none focus:border-paprika"
      />

      {tags.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {tags.map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => toggleTag(t)}
              aria-pressed={t === tag}
              className={`rounded-full px-3 py-1 text-sm ${
                t === tag ? 'bg-paprika text-white' : 'bg-ink/5 text-ink/80 hover:bg-ink/10'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      )}

      {error && <p className="mt-8 text-red-700">Couldn't load recipes: {error}</p>}

      {recipes && recipes.length === 0 && (
        <div className="mt-16 text-center text-ink/60">
          {filtering ? (
            <p>No recipes match.</p>
          ) : (
            <>
              <p className="text-lg">No recipes yet.</p>
              <p className="mt-1">Import one from a recipe site to get started.</p>
            </>
          )}
        </div>
      )}

      {recipes && recipes.length > 0 && (
        <ul className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {recipes.map((r) => (
            <li key={r.id}>
              <Link
                to={`/recipes/${r.id}`}
                className="block overflow-hidden rounded-xl bg-white shadow-sm ring-1 ring-ink/10 transition hover:shadow-md"
              >
                {r.image_url ? (
                  <img src={r.image_url} alt="" loading="lazy" className="aspect-[4/3] w-full object-cover" />
                ) : (
                  <div className="flex aspect-[4/3] items-center justify-center bg-paprika/10 font-display text-5xl text-paprika/40">
                    {r.title.charAt(0)}
                  </div>
                )}
                <div className="p-4">
                  <h2 className="font-display text-lg font-semibold leading-snug">{r.title}</h2>
                  <p className="mt-1 text-sm text-ink/60">
                    {[formatMinutes(r.total_minutes), r.servings && `Serves ${r.servings}`]
                      .filter(Boolean)
                      .join(' · ')}
                  </p>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
