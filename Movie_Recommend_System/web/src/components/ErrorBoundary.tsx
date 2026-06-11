import { Component, type ErrorInfo, type ReactNode } from 'react'

type Props = { children: ReactNode }
type State = { hasError: boolean }

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError(): State {
    return { hasError: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('UI error:', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="mx-auto max-w-lg p-10 text-center">
          <h1 className="text-2xl font-bold">Something went wrong</h1>
          <p className="mt-2 text-white/60">Please refresh the page or return home.</p>
          <a href="/" className="mt-6 inline-block rounded-full bg-[#f5c518] px-6 py-3 font-semibold text-black">
            Back to Home
          </a>
        </div>
      )
    }
    return this.props.children
  }
}
