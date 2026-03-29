import type { TargetId } from '../types'

export interface TargetConfig {
  id: TargetId
  codename: string
  x: number
  y: number
  component: 'ECHO' | 'GAMMA' | 'DELTA'
  mobility: 'HIGH' | 'LOW' | 'STATIC'
}

export const TARGETS: TargetConfig[] = [
  { id: 'TGT-ECHO-001',  codename: 'VARNAK',    x: 185, y: 120, component: 'ECHO',  mobility: 'HIGH'   },
  { id: 'TGT-ECHO-002',  codename: 'KAZMER',    x: 370, y: 195, component: 'ECHO',  mobility: 'HIGH'   },
  { id: 'TGT-GAMMA-001', codename: 'IRONBOX',   x: 295, y: 180, component: 'GAMMA', mobility: 'LOW'    },
  { id: 'TGT-DELTA-001', codename: 'OILCAN',    x: 155, y: 265, component: 'DELTA', mobility: 'STATIC' },
  { id: 'TGT-GAMMA-002', codename: 'STONEPILE', x: 265, y: 305, component: 'GAMMA', mobility: 'LOW'    },
]

export const ISR_TRACKS = [
  { callsign: 'RAVEN-1', cx: 210, cy: 110, rx: 70, ry: 45 },
  { callsign: 'RAVEN-2', cx: 320, cy: 220, rx: 55, ry: 35 },
]
