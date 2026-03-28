import { useEffect, useRef, type KeyboardEvent } from 'react'
import type { OperatorMessage } from '../types'

interface OperatorChatProps {
  input: string
  setInput: (v: string) => void
  transmit: () => void
  sending: boolean
  messages: OperatorMessage[]
  cycleId?: string
  activeTarget?: string
}

function formatTime(iso: string): string {
  try {
    const d = new Date(iso)
    const hh = String(d.getUTCHours()).padStart(2, '0')
    const mm = String(d.getUTCMinutes()).padStart(2, '0')
    const ss = String(d.getUTCSeconds()).padStart(2, '0')
    return `${hh}:${mm}:${ss}Z`
  } catch {
    return ''
  }
}

export function OperatorChat({
  input, setInput, transmit, sending, messages,
}: OperatorChatProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      transmit()
    }
  }

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      flex: 1,
      minHeight: 0,
      background: 'var(--bg-panel)',
      border: '1px solid var(--border)',
      borderRadius: 6,
      overflow: 'hidden',
    }}>
      {/* Panel title */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 6,
        padding: '6px 10px',
        borderBottom: '1px solid var(--border)',
        flexShrink: 0,
      }}>
        <span style={{ fontSize: 9, color: 'var(--text-dim)', letterSpacing: '0.08em' }}>
          OPERATOR
        </span>
        <span style={{
          fontSize: 8,
          background: 'var(--blue-bg)',
          color: 'var(--blue)',
          border: '1px solid var(--blue-bdr)',
          borderRadius: 10,
          padding: '0 5px',
        }}>
          COMKJTF
        </span>
      </div>

      {/* Chat history */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: 8,
        display: 'flex',
        flexDirection: 'column',
        gap: 8,
        minHeight: 0,
      }}>
        {messages.length === 0 ? (
          <div style={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            textAlign: 'center',
            fontSize: 10,
            color: 'var(--text-dim)',
            padding: '0 16px',
            lineHeight: 1.5,
          }}>
            Type a command or question below. The cycle will respond in real time.
          </div>
        ) : (
          messages.map((msg, i) => {
            const isOperator = msg.role === 'operator'
            return (
              <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: isOperator ? 'flex-end' : 'flex-start' }}>
                <div style={{
                  fontSize: 8,
                  color: '#30363d',
                  marginBottom: 2,
                }}>
                  {isOperator ? `COMKJTF · ${formatTime(msg.timestamp_zulu)}` : `System · ${formatTime(msg.timestamp_zulu)}`}
                </div>
                <div style={{
                  alignSelf: isOperator ? 'flex-end' : 'flex-start',
                  background: isOperator ? '#0d1f3c' : '#161b22',
                  border: `1px solid ${isOperator ? '#1f3a6e' : '#21262d'}`,
                  color: isOperator ? '#85b7eb' : '#8b949e',
                  borderRadius: isOperator ? '4px 4px 0 4px' : '4px 4px 4px 0',
                  padding: '6px 10px',
                  fontSize: 10,
                  maxWidth: isOperator ? '88%' : '92%',
                  lineHeight: 1.5,
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}>
                  {msg.content}
                </div>
              </div>
            )
          })
        )}
        <div ref={bottomRef} />
      </div>

      {/* Textarea */}
      <div style={{
        flexShrink: 0,
        padding: '6px 8px 4px',
        borderTop: '1px solid var(--border)',
      }}>
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="COMKJTF › type your command or question..."
          rows={3}
          style={{
            width: '100%',
            background: '#010409',
            border: '1px solid #21262d',
            borderRadius: 4,
            color: '#e6edf3',
            fontFamily: 'inherit',
            fontSize: 10,
            padding: '8px 10px',
            minHeight: 54,
            maxHeight: 120,
            resize: 'vertical',
            outline: 'none',
            lineHeight: 1.5,
            boxSizing: 'border-box',
          }}
          onFocus={e => { e.currentTarget.style.borderColor = '#1f6feb' }}
          onBlur={e => { e.currentTarget.style.borderColor = '#21262d' }}
        />
      </div>

      {/* Footer row */}
      <div style={{
        flexShrink: 0,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '0 8px 8px',
      }}>
        <span style={{ fontSize: 8, color: '#30363d' }}>
          Enter · send&nbsp;&nbsp;&nbsp;Shift+Enter · new line
        </span>
        <button
          onClick={transmit}
          disabled={sending}
          style={{
            background: sending ? '#161b22' : '#1f6feb',
            color: 'white',
            border: 'none',
            borderRadius: 4,
            padding: '5px 14px',
            fontSize: 10,
            cursor: sending ? 'not-allowed' : 'pointer',
            opacity: sending ? 0.5 : 1,
            fontFamily: 'inherit',
            transition: 'background 0.15s',
          }}
        >
          Transmit
        </button>
      </div>
    </div>
  )
}
