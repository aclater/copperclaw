import type { TargetState } from '../types'
import { TARGETS, ISR_TRACKS } from '../config/targets'
import { TargetMarker } from './TargetMarker'
import { useTargetPositions } from '../hooks/useTargetPositions'
import type { TargetPosition } from '../hooks/useTargetPositions'

interface TacticalMapProps {
  targets: TargetState[]
}

const POSITION_FALLBACK = (x: number, y: number): TargetPosition => ({
  x, y, uncertainty: 0, isConfirmed: false, lastConfirmedAt: 0, trail: [],
})

export function TacticalMap({ targets }: TacticalMapProps) {
  const positions = useTargetPositions(targets, TARGETS)
  const getTargetState = (id: string) =>
    targets.find(t => t.target_id === id)

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

      <svg
        viewBox="0 0 560 400"
        width="100%"
        height="100%"
        style={{ display: 'block', background: '#010409' }}
        preserveAspectRatio="xMidYMid meet"
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

        {/* Target markers — translated to animated position from hook */}
        {TARGETS.map(cfg => {
          const pos = positions.get(cfg.id) ?? POSITION_FALLBACK(cfg.x, cfg.y)
          return (
            <g key={cfg.id} transform={`translate(${pos.x.toFixed(1)},${pos.y.toFixed(1)})`}>
              <TargetMarker
                config={cfg}
                state={getTargetState(cfg.id)}
                position={pos}
              />
            </g>
          )
        })}
      </svg>
    </div>
  )
}
