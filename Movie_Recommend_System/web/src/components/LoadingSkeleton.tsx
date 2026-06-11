export function MovieCardSkeleton() {
  return (
    <div className="glass-panel animate-pulse overflow-hidden rounded-2xl">
      <div className="aspect-[2/3] bg-white/10" />
      <div className="space-y-2 p-4">
        <div className="h-4 rounded bg-white/10" />
        <div className="h-3 w-2/3 rounded bg-white/5" />
      </div>
    </div>
  )
}

export function MovieRailSkeleton({ count = 4 }: { count?: number }) {
  return (
    <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
      {Array.from({ length: count }).map((_, i) => (
        <MovieCardSkeleton key={i} />
      ))}
    </div>
  )
}
