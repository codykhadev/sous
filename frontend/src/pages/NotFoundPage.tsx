import { Link } from 'react-router'

export default function NotFoundPage() {
  return (
    <section>
      <h1 className="font-display text-3xl font-bold">Page not found</h1>
      <Link to="/" className="mt-4 inline-block text-paprika underline">
        Back to your recipes
      </Link>
    </section>
  )
}
