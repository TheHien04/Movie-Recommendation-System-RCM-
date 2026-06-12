import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { Send, LoaderCircle, ThumbsUp, ThumbsDown, Sparkles, Cloud } from 'lucide-react'
import { fetchChatHistory, fetchRecommendations, saveChatMessage, submitFeedback } from '../lib/api'
import type { Recommendation } from '../lib/api'
import { getToken } from '../lib/auth'
import { MovieCard } from '../components/MovieCard'

type Message = {
  role: 'user' | 'assistant'
  text: string
  movies?: Recommendation[]
  variant?: string
  query?: string
}

const WELCOME: Message = {
  role: 'assistant',
  text: 'Tell me what you want to watch — genre, actor, director, mood, or plot keywords.',
}

export function Chat() {
  const [params] = useSearchParams()
  const [input, setInput] = useState('')
  const [mode, setMode] = useState<'hybrid' | 'rag'>('hybrid')
  const [messages, setMessages] = useState<Message[]>([WELCOME])
  const [loading, setLoading] = useState(false)
  const [synced, setSynced] = useState(false)
  const bootstrapped = useRef(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    document.title = 'AI Chat — Cinemate'
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  useEffect(() => {
    if (!getToken()) return
    fetchChatHistory()
      .then((history) => {
        if (!history.length) return
        const restored: Message[] = history.map((m) => ({
          role: m.role,
          text: m.content,
          movies: m.movies?.length ? m.movies : undefined,
        }))
        setMessages(restored)
        setSynced(true)
      })
      .catch(() => {})
  }, [])

  useEffect(() => {
    const q = params.get('q')
    if (q && !bootstrapped.current) {
      bootstrapped.current = true
      void submitQuery(q)
    }
  }, [params])

  async function persistMessage(message: Message) {
    if (!getToken()) return
    try {
      await saveChatMessage({
        role: message.role,
        content: message.text,
        movies: message.movies,
      })
      setSynced(true)
    } catch {
      /* local session still works */
    }
  }

  async function submitQuery(query: string) {
    if (!query.trim()) return
    const userMessage: Message = { role: 'user', text: query }
    setMessages((prev) => [...prev, userMessage])
    void persistMessage(userMessage)
    setLoading(true)
    try {
      const data = await fetchRecommendations(query, mode)
      const assistantMessage: Message = {
        role: 'assistant',
        text: data.answer || `Top picks from ${data.model}${data.personalized ? ' (personalized)' : ''} (variant ${data.variant || 'A'}).`,
        movies: data.recommended_movies,
        variant: data.variant,
        query,
      }
      setMessages((prev) => [...prev, assistantMessage])
      void persistMessage(assistantMessage)
    } catch {
      const errorMessage: Message = {
        role: 'assistant',
        text: 'Could not reach the API. Ensure backend is running on port 5001.',
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
      setInput('')
    }
  }

  async function feedback(movie: string, rating: 1 | -1, query?: string, variant?: string) {
    try { await submitFeedback(movie, rating, query, variant) } catch { /* ignore */ }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault()
    void submitQuery(input)
  }

  return (
    <div className="mx-auto flex max-w-5xl flex-col px-4 py-10 md:px-6">
      <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold">AI Recommendation Chat</h1>
          <p className="text-white/60">Hybrid ML + optional RAG mode with A/B variants</p>
          {getToken() && synced && (
            <p className="mt-1 inline-flex items-center gap-1 text-xs text-emerald-300/80">
              <Cloud size={12} /> Chat synced to your account
            </p>
          )}
        </div>
        <div className="flex rounded-full bg-white/10 p-1">
          <button type="button" onClick={() => setMode('hybrid')} className={`rounded-full px-4 py-2 text-sm ${mode === 'hybrid' ? 'bg-[#f5c518] text-black' : ''}`}>Hybrid</button>
          <button type="button" onClick={() => setMode('rag')} className={`inline-flex items-center gap-1 rounded-full px-4 py-2 text-sm ${mode === 'rag' ? 'bg-[#f5c518] text-black' : ''}`}><Sparkles size={14} /> RAG</button>
        </div>
      </div>

      <div className="glass-panel flex min-h-[60vh] flex-col rounded-[2rem] p-4 md:p-6">
        <div className="flex-1 space-y-4 overflow-y-auto pr-1">
          {messages.map((message, index) => (
            <div key={index}>
              <div className={message.role === 'user' ? 'flex justify-end' : ''}>
                <div className={`max-w-[90%] rounded-2xl px-4 py-3 ${message.role === 'user' ? 'bg-[#f5c518] text-black' : 'bg-white/5'}`}>
                  {message.text}
                  {message.variant && <p className="mt-1 text-xs opacity-60">A/B variant {message.variant}</p>}
                </div>
              </div>
              {message.movies && (
                <div className="mt-4 grid gap-4 sm:grid-cols-2">
                  {message.movies.map((movie) => (
                    <div key={movie.title} className="space-y-2">
                      <Link to={`/movie/${encodeURIComponent(movie.title)}`}>
                        <MovieCard title={movie.title} poster={movie.poster} rating={movie.total_rating} explanation={movie.explanation} />
                      </Link>
                      <div className="flex gap-2">
                        <button type="button" onClick={() => feedback(movie.title, 1, message.query, message.variant)} className="flex-1 rounded-lg bg-white/5 py-1 text-sm hover:bg-emerald-500/20"><ThumbsUp size={14} className="mx-auto" /></button>
                        <button type="button" onClick={() => feedback(movie.title, -1, message.query, message.variant)} className="flex-1 rounded-lg bg-white/5 py-1 text-sm hover:bg-red-500/20"><ThumbsDown size={14} className="mx-auto" /></button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
          {loading && <div className="inline-flex items-center gap-2 text-white/60"><LoaderCircle className="animate-spin" size={18} /> Ranking...</div>}
          <div ref={bottomRef} />
        </div>

        <form onSubmit={onSubmit} className="mt-4 flex gap-3 border-t border-white/10 pt-4">
          <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="e.g. psychological thriller directed by David Fincher" className="flex-1 rounded-2xl border border-white/10 bg-black/30 px-4 py-3 outline-none" />
          <button type="submit" disabled={loading} className="inline-flex items-center gap-2 rounded-2xl bg-[#f5c518] px-5 py-3 font-semibold text-black disabled:opacity-50"><Send size={18} /> Send</button>
        </form>
      </div>

    </div>
  )
}
