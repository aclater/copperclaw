import { useRef } from 'react'
import type { CycleState } from '../types'
import { TARGETS, ISR_TRACKS } from '../config/targets'
import { TargetMarker } from './TargetMarker'
import { TargetContextMenu } from './TargetContextMenu'
import { ConfirmDialog } from './ConfirmDialog'
import { useTargetPositions } from '../hooks/useTargetPositions'
import { useTargetSelection } from '../hooks/useTargetSelection'
import { getAvailableActions } from '../utils/targetActions'
import { executeTargetAction } from '../utils/executeAction'
import type { TargetPosition } from '../hooks/useTargetPositions'
import type { TargetAction } from '../types'

interface TacticalMapProps {
  targets: CycleState['targets']
  cycleState: CycleState
  onActionExecuted: (message: string) => void
}

const POSITION_FALLBACK = (x: number, y: number): TargetPosition => ({
  x, y, uncertainty: 0, isConfirmed: false, lastConfirmedAt: 0, trail: [],
})

export function TacticalMap({ targets, cycleState, onActionExecuted }: TacticalMapProps) {
  const positions = useTargetPositions(targets, TARGETS)
  const svgRef = useRef<SVGSVGElement>(null)

  const {
    selected, selectTarget, clearSelection,
    confirmAction, confirmReason, setConfirmReason,
    startConfirm, cancelConfirm,
    menuRef,
  } = useTargetSelection()

  const getTargetState = (id: string) =>
    targets.find(t => t.target_id === id)

  const handleAction = (action: TargetAction) => {
    if (!selected) return
    const actions = getAvailableActions(selected.state, cycleState)
    const actionDef = actions.find(a => a.id === action)
    if (!actionDef || actionDef.lockedReason) return
    if (actionDef.requiresConfirm) {
      startConfirm(action)
    } else {
      executeTargetAction(action, selected, cycleState).then(result => {
        if (result.message !== 'TNP view requested') {
          onActionExecuted(result.message)
        }
        clearSelection()
      })
    }
  }

  const handleConfirm = () => {
    if (!selected || !confirmAction) return
    const actions = getAvailableActions(selected.state, cycleState)
    const actionDef = actions.find(a => a.id === confirmAction)
    if (!actionDef) return
    executeTargetAction(confirmAction, selected, cycleState, confirmReason).then(result => {
      if (result.message !== 'TNP view requested') {
        onActionExecuted(result.message)
      }
      clearSelection()
    })
  }

  const availableActions = selected
    ? getAvailableActions(selected.state, cycleState)
    : []

  const confirmActionDef = confirmAction
    ? availableActions.find(a => a.id === confirmAction)
    : null

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', minHeight: 240 }}>
      {/* Header strip */}
      <div style={{
        position: 'absolute',
        top: 0, left: 0, right: 0,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '4px 8px',
        zIndex: 2,
        pointerEvents: 'none',
      }}>
        <span style={{ fontSize: 9, color: 'var(--text-dim)' }}>
          MGRS VICTOR-5 KILO — AO HARROW
        </span>
        <span style={{
          fontSize: 9,
          color: 'var(--amber)',
          border: '1px solid var(--amber-bdr)',
          padding: '2px 6px',
          borderRadius: 2,
        }}>
          COSMIC INDIGO // EXERCISE
        </span>
      </div>

      {/* SVG map */}
      <div style={{ position: 'relative' }}>
        <svg
          ref={svgRef}
          viewBox="0 0 560 400"
          width="100%"
          height="100%"
          style={{ display: 'block', background: '#010409' }}
          preserveAspectRatio="xMidYMid meet"
          onClick={clearSelection}
        >
          <defs>
            <pattern id="grid" width={44} height={44} patternUnits="userSpaceOnUse">
              <path d="M 44 0 L 0 0 0 44" fill="none" stroke="white" strokeWidth={0.5} opacity={0.025} />
            </pattern>
          </defs>

          {/* Grid background */}
          <rect width={560} height={400} fill="url(#grid)" />

          {/* ISR tracks */}
          {ISR_TRACKS.map(track => (
            <g key={track.callsign}>
              <ellipse
                cx={track.cx}
                cy={track.cy}
                rx={track.rx}
                ry={track.ry}
                fill="none"
                stroke="#1f6feb"
                strokeWidth={1}
                strokeDasharray="4 2"
                opacity={0.25}
              />
              <text
                x={track.cx}
                y={track.cy - track.ry - 4}
                textAnchor="middle"
                fill="#58a6ff"
                fontSize={8}
                fontFamily="var(--font-mono)"
                opacity={0.6}
              >
                {track.callsign}
              </text>
            </g>
          ))}

          {/* Target markers */}
          {TARGETS.map(cfg => {
            const pos = positions.get(cfg.id) ?? POSITION_FALLBACK(cfg.x, cfg.y)
            const targetState = getTargetState(cfg.id)
            const isSelected = cfg.id === selected?.targetId

            return (
              <g
                key={cfg.id}
                className="tactical-target"
                transform={`translate(${pos.x.toFixed(1)},${pos.y.toFixed(1)})`}
                onClick={(e) => {
                  e.stopPropagation()
                  if (!svgRef.current) return
                  const svgRect = svgRef.current.getBoundingClientRect()
                  selectTarget(
                    cfg.id,
                    cfg.codename,
                    targetState,
                    {
                      x: e.clientX - svgRect.left,
                      y: e.clientY - svgRect.top,
                    }
                  )
                }}
              >
                <TargetMarker
                  config={cfg}
                  state={targetState}
                  position={pos}
                  isSelected={isSelected}
                />
              </g>
            )
          })}
        </svg>

        {/* Context menu overlay */}
        {selected && (
          <div
            ref={menuRef}
            style={{
              position: 'absolute',
              left: Math.min(selected.menuPosition.x + 12, (svgRef.current?.clientWidth ?? 560) - 196),
              top: Math.max(selected.menuPosition.y - 24, 0),
              zIndex: 100,
            }}
          >
            <TargetContextMenu
              selected={selected}
              actions={availableActions}
              cycleState={cycleState}
              onAction={handleAction}
              onClose={clearSelection}
            />
            {confirmAction && confirmActionDef && (
              <ConfirmDialog
                action={confirmActionDef}
                target={selected}
                reason={confirmReason}
                onReasonChange={setConfirmReason}
                onConfirm={handleConfirm}
                onCancel={cancelConfirm}
              />
            )}
          </div>
        )}
      </div>
    </div>
  )
}
