import type { TargetActionDef, TargetAction, SelectedTarget, CycleState } from '../types'

interface TargetContextMenuProps {
  selected: SelectedTarget
  actions: TargetActionDef[]
  cycleState: CycleState
  onAction: (action: TargetAction) => void
  onClose: () => void
}

const PHASE_DOT_COLOR: Record<string, string> = {
  HOLD:    '#d29922',
  FIND:    '#f85149',
  FIX:     '#f85149',
  ASSESS:  '#58a6ff',
  DEVELOP: '#58a6ff',
  COMPLETE:'#3fb950',
}

const ACTION_COLOR: Record<string, string> = {
  green: '#3fb950',
  amber: '#d29922',
  blue:  '#58a6ff',
  red:   '#f85149',
  gray:  '#8b949e',
}

const GROUP_LABEL: Record<string, string> = {
  cycle:    'CYCLE ACTIONS',
  isr:      'ISR',
  info:     'INFO',
  escalate: 'ESCALATE',
}

export function TargetContextMenu({
  selected, actions, onAction,
}: TargetContextMenuProps) {
  const phase = selected.state?.phase ?? 'FIND'
  const phaseDot = PHASE_DOT_COLOR[phase] ?? '#8b949e'
  const pct = selected.state?.confidence ?? 0

  // Group actions
  const groups = (['cycle', 'isr', 'info', 'escalate'] as const).map(g => ({
    key: g,
    items: actions.filter(a => a.group === g),
  })).filter(g => g.items.length > 0)

  return (
    <div style={{
      background: '#010409',
      border: '1px solid #21262d',
      borderRadius: 5,
      width: 180,
      zIndex: 100,
      overflow: 'hidden',
      fontFamily: 'var(--font-mono)',
    }}>
      {/* Header */}
      <div style={{
        padding: '6px 8px',
        borderBottom: '1px solid #21262d',
        display: 'flex',
        alignItems: 'center',
        gap: 6,
      }}>
        <div style={{
          width: 8, height: 8, borderRadius: '50%',
          background: phaseDot, flexShrink: 0,
        }} />
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <span style={{ fontSize: 10, color: '#e6edf3' }}>
            {selected.codename} ({selected.targetId})
          </span>
          <span style={{ fontSize: 8, color: '#8b949e' }}>
            Phase: {phase} · PIR: {pct}%
          </span>
        </div>
      </div>

      {/* Action groups */}
      {groups.map((group, gi) => (
        <div key={group.key}>
          {gi > 0 && <div style={{ height: 1, background: '#21262d', margin: '2px 0' }} />}
          <div style={{
            fontSize: 8,
            color: '#30363d',
            padding: '4px 8px 2px',
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
          }}>
            {GROUP_LABEL[group.key]}
          </div>
          {group.items.map(action => {
            const locked = !!action.lockedReason
            const dotColor = ACTION_COLOR[action.color] ?? '#8b949e'
            return (
              <div
                key={action.id}
                onClick={locked ? undefined : () => onAction(action.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  padding: '5px 8px',
                  cursor: locked ? 'default' : 'pointer',
                  opacity: locked ? 0.4 : 1,
                  transition: 'background 0.1s',
                }}
                onMouseEnter={e => {
                  if (!locked) (e.currentTarget as HTMLDivElement).style.background = '#161b22'
                }}
                onMouseLeave={e => {
                  (e.currentTarget as HTMLDivElement).style.background = 'transparent'
                }}
              >
                <div style={{
                  width: 5, height: 5, borderRadius: '50%',
                  background: dotColor, flexShrink: 0,
                }} />
                <span style={{
                  fontSize: 9,
                  color: locked ? '#30363d' : '#e6edf3',
                  flex: 1,
                  lineHeight: 1.3,
                }}>
                  {action.label}
                </span>
                {locked && (
                  <span style={{
                    fontSize: 8,
                    color: '#30363d',
                    maxWidth: 60,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}>
                    {action.lockedReason!.substring(0, 12)}
                  </span>
                )}
              </div>
            )
          })}
        </div>
      ))}
    </div>
  )
}
