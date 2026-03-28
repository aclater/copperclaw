import { useState, useCallback } from 'react'
import type { OperatorMessage } from '../types'

export function useOperator() {
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [messages, setMessages] = useState<OperatorMessage[]>([])

  const transmit = useCallback(async () => {
    if (!input.trim() || sending) return
    const text = input.trim()
    setInput('')
    setSending(true)

    setMessages(prev => [...prev, {
      role: 'operator',
      content: text,
      timestamp_zulu: new Date().toISOString()
    }])

    try {
      const res = await fetch('/api/operator/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      })
      const data = await res.json()
      setMessages(prev => [...prev, {
        role: 'system',
        content: data.response ?? 'Acknowledged.',
        timestamp_zulu: new Date().toISOString()
      }])
    } catch {
      setMessages(prev => [...prev, {
        role: 'system',
        content: 'Operator service unreachable — command not transmitted.',
        timestamp_zulu: new Date().toISOString()
      }])
    } finally {
      setSending(false)
    }
  }, [input, sending])

  return { input, setInput, transmit, sending, messages }
}
