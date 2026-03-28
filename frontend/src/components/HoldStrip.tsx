import type { TargetId } from '../types'

interface HoldStripProps {
  targetId?: TargetId
  codename?: string
  tnpId?: string
  visible: boolean
}

export function HoldStrip({ targetId, codename, tnpId, visible }: HoldStripProps) {
  if (!visible) return null

  return (
    <div style={{
      background: '#1a0a00',
      border: '1px solid #3d1a00',
      borderRadius: 4,
      padding: '8px 12px',
      display: 'flex',
      alignItems: 'center',
      gap: 10,
    }}>
      {/* Pulsing amber dot */}
      <div style={{
        width: 10,
        height: 10,
        borderRadius: '50%',
        background: 'var(--amber)',
        flexShrink: 0,
        animation: 'blink 1.2s step-end infinite',
      }} />
      <div>
        <div style={{ fontSize: 11, color: 'var(--amber)', fontWeight: 500 }}>
          Commander hold — {codename ?? targetId} {targetId ? `(${targetId})` : ''}
        </div>
        <div style={{ fontSize: 9, color: '#854f0b', marginTop: 2 }}>
          Nomination package {tnpId ?? '—'} cleared by legal review — awaiting COMKJTF authorization
        </div>
      </div>
    </div>
  )
}
