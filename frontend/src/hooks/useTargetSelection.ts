import { useState, useEffect, useRef } from 'react'
import type { TargetId, TargetState, TargetAction, SelectedTarget } from '../types'

export function useTargetSelection() {
  const [selected, setSelected] = useState<SelectedTarget | null>(null)
  const [confirmAction, setConfirmAction] = useState<TargetAction | null>(null)
  const [confirmReason, setConfirmReason] = useState('')
  const menuRef = useRef<HTMLDivElement | null>(null)

  const selectTarget = (
    targetId: TargetId,
    codename: string,
    state: TargetState | undefined,
    position: { x: number; y: number },
  ) => {
    setSelected({ targetId, codename, state, menuPosition: position })
    setConfirmAction(null)
    setConfirmReason('')
  }

  const clearSelection = () => {
    setSelected(null)
    setConfirmAction(null)
    setConfirmReason('')
  }

  const startConfirm = (action: TargetAction) => {
    setConfirmAction(action)
    setConfirmReason('')
  }

  const cancelConfirm = () => {
    setConfirmAction(null)
    setConfirmReason('')
  }

  useEffect(() => {
    const handleMouseDown = (e: MouseEvent) => {
      if (!selected) return
      if (menuRef.current && menuRef.current.contains(e.target as Node)) return
      clearSelection()
    }
    document.addEventListener('mousedown', handleMouseDown)
    return () => document.removeEventListener('mousedown', handleMouseDown)
  }, [selected])

  return {
    selected,
    selectTarget,
    clearSelection,
    confirmAction,
    confirmReason,
    setConfirmReason,
    startConfirm,
    cancelConfirm,
    menuRef,
  }
}
