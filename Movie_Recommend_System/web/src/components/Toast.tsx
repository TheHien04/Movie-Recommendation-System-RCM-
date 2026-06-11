import { useEffect, useState } from 'react'

let showToastImpl: ((msg: string) => void) | null = null

export function toast(message: string) {
  showToastImpl?.(message)
}

export function ToastHost() {
  const [message, setMessage] = useState('')
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    showToastImpl = (msg: string) => {
      setMessage(msg)
      setVisible(true)
      setTimeout(() => setVisible(false), 2800)
    }
    return () => {
      showToastImpl = null
    }
  }, [])

  if (!visible) return null

  return (
    <div className="fixed bottom-6 left-1/2 z-[200] -translate-x-1/2 rounded-full bg-[#f5c518] px-6 py-3 font-semibold text-black shadow-lg">
      {message}
    </div>
  )
}
