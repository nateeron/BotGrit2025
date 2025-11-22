import { Box } from '@mui/material'
import { useRef, useEffect, useState } from 'react'
import './tradingLayout.css'

interface SplitterProps {
  direction: 'horizontal' | 'vertical'
  onResize: (delta: number) => void
}

export const Splitter = ({ direction, onResize }: SplitterProps) => {
  const [isDragging, setIsDragging] = useState(false)
  const startPosRef = useRef<number>(0)
  const startDeltaRef = useRef<number>(0)

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault()
    setIsDragging(true)
    if (direction === 'horizontal') {
      startPosRef.current = e.clientY
    } else {
      startPosRef.current = e.clientX
    }
    startDeltaRef.current = 0
  }

  useEffect(() => {
    if (!isDragging) return

    const handleMouseMove = (e: MouseEvent) => {
      const currentPos = direction === 'horizontal' ? e.clientY : e.clientX
      const delta = currentPos - startPosRef.current
      const deltaChange = delta - startDeltaRef.current
      
      if (Math.abs(deltaChange) > 0) {
        onResize(deltaChange)
        startDeltaRef.current = delta
      }
    }

    const handleMouseUp = () => {
      setIsDragging(false)
    }

    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)

    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isDragging, direction, onResize])

  return (
    <Box
      className={`trading-splitter trading-splitter-${direction}`}
      onMouseDown={handleMouseDown}
      sx={{
        position: 'relative',
        backgroundColor: 'rgba(255,255,255,0.08)',
        flexShrink: 0,
        cursor: direction === 'horizontal' ? 'row-resize' : 'col-resize',
        '&:hover': {
          backgroundColor: 'rgba(255,255,255,0.15)',
        },
        ...(direction === 'horizontal'
          ? {
              width: '100%',
              height: '4px',
            }
          : {
              width: '4px',
              height: '100%',
            }),
      }}
    />
  )
}

