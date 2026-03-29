import type { KeyboardEvent } from 'react'
import type { TargetActionDef, SelectedTarget } from '../types'

interface ConfirmDialogProps {
  action: TargetActionDef
  target: SelectedTarget
  reason: string
  onReasonChange: (r: string) => void
  onConfirm: () => void
  onCancel: () => void
}

export function ConfirmDialog({
  action, target, reason, onReasonChange, onConfirm, onCancel,
}: ConfirmDialogProps) {
  const isRed = action.color === 'red'
  const isGreen = action.color === 'green'

  const borderColor = isRed ? '#3d1a00' : isGreen ? '#1a3a20' : '#3d2a00'
  const confirmBg   = isRed ? '#4a1a1a' : isGreen ? '#0d2010' : '#2d1e00'
  const confirmText = isRed ? '#f85149' : isGreen ? '#3fb950' : '#d29922'
  const confirmBdr  = isRed ? '#6b2020' : isGreen ? '#1a4a20' : '#5a3a00'

  const canConfirm = !action.requiresReason || reason.trim().length > 0

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey && canConfirm) {
      e.preventDefault()
      onConfirm()
    }
    if (e.key === 'Escape') {
      e.preventDefault()
      onCancel()
    }
  }

  return (
    <div style={{
      background: '#010409',
      border: `1px solid ${borderColor}`,
      borderRadius: 4,
      padding: '8px 10px',
      width: 180,
      marginTop: 4,
      fontFamily: 'var(--font-mono)',
    }}>
      <div style={{ fontSize: 10, color: '#e6edf3', marginBottom: 2 }}>
        Confirm: {action.label}
      </div>
      <div style={{ fontSize: 8, color: '#8b949e', marginBottom: 6 }}>
        for {target.codename}
      </div>

      {action.requiresReason && (
        <textarea
          rows={3}
          value={reason}
          onChange={e => onReasonChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="State reason..."
          style={{
            width: '100%',
            background: '#161b22',
            border: '1px solid #21262d',
            color: '#e6edf3',
            fontFamily: 'var(--font-mono)',
            fontSize: 9,
            padding: '4px 6px',
            borderRadius: 3,
            resize: 'vertical',
            outline: 'none',
            boxSizing: 'border-box',
          }}
          autoFocus
        />
      )}

      <div style={{ display: 'flex', gap: 6, marginTop: 6 }}>
        <button
          onClick={onCancel}
          style={{
            flex: 1,
            fontSize: 8,
            background: 'transparent',
            border: '1px solid #21262d',
            color: '#8b949e',
            padding: '3px 8px',
            borderRadius: 3,
            cursor: 'pointer',
            fontFamily: 'var(--font-mono)',
          }}
        >
          Cancel
        </button>
        <button
          onClick={canConfirm ? onConfirm : undefined}
          disabled={!canConfirm}
          style={{
            flex: 1,
            fontSize: 8,
            background: canConfirm ? confirmBg : '#161b22',
            border: `1px solid ${canConfirm ? confirmBdr : '#21262d'}`,
            color: canConfirm ? confirmText : '#30363d',
            padding: '3px 8px',
            borderRadius: 3,
            cursor: canConfirm ? 'pointer' : 'not-allowed',
            fontFamily: 'var(--font-mono)',
          }}
        >
          Confirm
        </button>
      </div>
    </div>
  )
}
