import { useRef, type KeyboardEvent } from 'react'

interface OperatorInputProps {
  input: string
  setInput: (val: string) => void
  transmit: () => void
  sending: boolean
  cycleId: string
  codename?: string
}

export function OperatorInput({
  input, setInput, transmit, sending, cycleId, codename
}: OperatorInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      transmit()
    }
  }

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: '160px 1fr 72px',
      gap: 8,
      alignItems: 'center',
      padding: '0 8px',
    }}>
      {/* Left info */}
      <div>
        <div style={{ fontSize: 9, color: 'var(--text-dim)', letterSpacing: '0.08em' }}>
          ACTIVE CYCLE
        </div>
        <div style={{ fontSize: 11, color: 'var(--text-primary)', marginTop: 2 }}>
          {cycleId} // {codename ?? '—'}
        </div>
      </div>

      {/* Chat input */}
      <div style={{
        background: 'var(--bg-panel)',
        border: '1px solid var(--border)',
        borderRadius: 4,
        padding: '6px 10px',
        display: 'flex',
        alignItems: 'center',
        gap: 8,
      }}>
        <span style={{ fontSize: 10, color: 'var(--text-dim)', flexShrink: 0 }}>
          COMKJTF ›
        </span>
        <textarea
          ref={textareaRef}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Enter command or authorization…"
          rows={1}
          style={{
            flex: 1,
            fontSize: 10,
            color: 'var(--text-secondary)',
            background: 'transparent',
            border: 'none',
            outline: 'none',
            resize: 'none',
            fontFamily: 'var(--font-mono)',
            lineHeight: 1.5,
          }}
        />
        {/* Cursor blink indicator */}
        <div style={{
          width: 1,
          height: 12,
          background: 'var(--blue)',
          flexShrink: 0,
          animation: 'blink 1s step-end infinite',
        }} />
      </div>

      {/* Transmit button */}
      <button
        onClick={transmit}
        disabled={sending || !input.trim()}
        style={{
          background: sending || !input.trim() ? '#161b22' : '#1f6feb',
          color: 'white',
          border: 'none',
          borderRadius: 4,
          padding: '8px 0',
          width: '100%',
          fontSize: 10,
          letterSpacing: '0.04em',
          cursor: sending || !input.trim() ? 'not-allowed' : 'pointer',
          opacity: sending ? 0.5 : 1,
          fontFamily: 'var(--font-mono)',
          transition: 'background 0.15s',
        }}
      >
        Transmit
      </button>
    </div>
  )
}
