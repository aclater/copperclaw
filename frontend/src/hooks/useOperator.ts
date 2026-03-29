import { useState, useCallback } from 'react'
import type { OperatorMessage } from '../types'

export function useOperator() {
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [messages, setMessages] = useState<OperatorMessage[]>([{
    role: 'system',
    content: 'Operator interface online. COPPERCLAW targeting cycle ready. Type a command to begin or ask a question about the current cycle state.',
    timestamp_zulu: new Date().toISOString()
  }])

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
        content: 'Operator service unreachable — check that operator-service is running on port 8000.',
        timestamp_zulu: new Date().toISOString()
      }])
    } finally {
      setSending(false)
    }
  }, [input, sending])

  const appendMessage = useCallback((msg: OperatorMessage) => {
    setMessages(prev => [...prev, msg])
  }, [])

  return { input, setInput, transmit, sending, messages, appendMessage }
}
