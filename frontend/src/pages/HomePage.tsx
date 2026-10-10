import { useEffect, useState } from 'react'
import { apiGet, type Health } from '../api/client'

export default function HomePage() {
  const [health, setHealth] = useState<Health | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    apiGet<Health>('/health').then(setHealth).catch((e: Error) => setError(e.message))
  }, [])

  return (
    <section>
      <h1 className="font-display text-4xl font-bold">Your recipes</h1>
      <p className="mt-2 text-ink/70">Nothing here yet. Recipe import arrives in stage 2.</p>
      <p className="mt-8 text-sm text-ink/50">
        {error
          ? `Backend unreachable: ${error}`
          : health
            ? `Backend ${health.status} · database ${health.database}`
            : 'Checking backend…'}
      </p>
    </section>
  )
}
