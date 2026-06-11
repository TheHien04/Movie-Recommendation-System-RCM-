import { useState } from 'react'
import type { FormEvent } from 'react'
import { GitCompare, Plus, X } from 'lucide-react'
import { compareMovies } from '../lib/api'
import type { MovieDetails } from '../lib/api'

type CompareMovie = MovieDetails & { error?: string }

export function Compare() {
  const [inputs, setInputs] = useState(['', ''])
  const [movies, setMovies] = useState<CompareMovie[]>([])
  const [matrix, setMatrix] = useState<number[][]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  function updateInput(i: number, val: string) {
    setInputs((prev) => prev.map((v, idx) => (idx === i ? val : v)))
  }

  function addSlot() {
    if (inputs.length < 3) setInputs((prev) => [...prev, ''])
  }

  function removeSlot(i: number) {
    if (inputs.length <= 2) return
    setInputs((prev) => prev.filter((_, idx) => idx !== i))
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    const titles = inputs.map((t) => t.trim()).filter(Boolean)
    if (titles.length < 2) {
      setError('Enter at least 2 movie titles')
      return
    }
    setError('')
    setLoading(true)
    try {
      const data = await compareMovies(titles)
      setMovies(data.movies as CompareMovie[])
      setMatrix(data.similarity_matrix)
    } catch {
      setError('Compare failed — check titles and try again')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 md:px-6">
      <div className="flex items-center gap-3">
        <GitCompare className="text-[#f5c518]" size={32} />
        <div>
          <h1 className="text-4xl font-bold">Compare Movies</h1>
          <p className="mt-1 text-white/60">Side-by-side metadata + semantic similarity matrix</p>
        </div>
      </div>

      <form onSubmit={onSubmit} className="glass-panel mt-8 space-y-3 rounded-2xl p-6">
        {inputs.map((val, i) => (
          <div key={i} className="flex gap-2">
            <input
              value={val}
              onChange={(e) => updateInput(i, e.target.value)}
              placeholder={`Movie ${i + 1} title`}
              className="flex-1 rounded-xl border border-white/10 bg-white/5 px-4 py-3 outline-none focus:border-[#f5c518]/40"
            />
            {inputs.length > 2 && (
              <button type="button" onClick={() => removeSlot(i)} className="rounded-xl border border-white/10 px-3 hover:bg-white/5">
                <X size={16} />
              </button>
            )}
          </div>
        ))}
        <div className="flex flex-wrap gap-3">
          {inputs.length < 3 && (
            <button type="button" onClick={addSlot} className="inline-flex items-center gap-2 rounded-xl border border-white/15 px-4 py-2 text-sm hover:bg-white/5">
              <Plus size={14} /> Add movie
            </button>
          )}
          <button type="submit" disabled={loading} className="rounded-xl bg-[#f5c518] px-6 py-2 font-semibold text-black disabled:opacity-50">
            {loading ? 'Comparing...' : 'Compare'}
          </button>
        </div>
        {error && <p className="text-sm text-red-300">{error}</p>}
      </form>

      {movies.length >= 2 && (
        <>
          <div className="mt-10 grid gap-5 lg:grid-cols-2 xl:grid-cols-3">
            {movies.map((m) => (
              <div key={m.title} className="glass-panel rounded-2xl p-5">
                {'error' in m && m.error ? (
                  <p className="text-red-300">{m.title}: not found</p>
                ) : (
                  <>
                    <img src={m.poster} alt={m.title} className="mb-4 h-48 w-full rounded-xl object-cover" />
                    <h3 className="text-lg font-bold">{m.title}</h3>
                    <dl className="mt-3 space-y-1 text-sm text-white/70">
                      <div className="flex justify-between"><dt>IMDb</dt><dd>{m.ratingIMDB ?? '—'}</dd></div>
                      <div className="flex justify-between"><dt>Genre</dt><dd className="text-right">{m.genre}</dd></div>
                      <div className="flex justify-between"><dt>Director</dt><dd>{m.director}</dd></div>
                      <div className="flex justify-between"><dt>Year</dt><dd>{m.year}</dd></div>
                      <div className="flex justify-between"><dt>Runtime</dt><dd>{m.runtime} min</dd></div>
                    </dl>
                  </>
                )}
              </div>
            ))}
          </div>

          {matrix.length > 0 && (
            <section className="glass-panel mt-8 overflow-x-auto rounded-2xl p-6">
              <h2 className="mb-4 text-xl font-semibold">Semantic Similarity Matrix</h2>
              <table className="w-full text-sm">
                <thead>
                  <tr>
                    <th className="p-2 text-left text-white/40" />
                    {movies.map((m) => (
                      <th key={m.title} className="p-2 text-left font-normal text-white/70">{m.title}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {matrix.map((row, i) => (
                    <tr key={i} className="border-t border-white/10">
                      <td className="p-2 text-white/70">{movies[i]?.title}</td>
                      {row.map((val, j) => (
                        <td key={j} className={`p-2 ${i === j ? 'text-white/30' : val > 0.7 ? 'text-emerald-400' : 'text-white/60'}`}>
                          {val.toFixed(3)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          )}
        </>
      )}
    </div>
  )
}
