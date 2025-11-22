import { useEffect, useRef, useState } from 'react'
import { Box, Typography } from '@mui/material'
import { createChart, LineSeries } from 'lightweight-charts'
import type { IChartApi, ISeriesApi } from 'lightweight-charts'
import { useTradingStore } from '../../store/tradingStore'
import { calculateRSI } from '../../utils/indicatorMath'
import { useChartDataStore } from './useChartData'

export const RSIChart = () => {
  const chartData = useChartDataStore((state) => state.chartData)
  const { syncRsiChart } = useTradingStore()
  const containerRef = useRef<HTMLDivElement | null>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const rsiSeriesRef = useRef<ISeriesApi<'Line'> | null>(null)
  const [mousePos, setMousePos] = useState<{ x: number; y: number } | null>(null)

  useEffect(() => {
    if (!containerRef.current) return

    const containerRect = containerRef.current.getBoundingClientRect()
    const initialWidth = containerRect.width
    const initialHeight = containerRect.height || 160

    if (chartRef.current) {
      chartRef.current.remove()
      chartRef.current = null
      rsiSeriesRef.current = null
    }

    chartRef.current = createChart(containerRef.current, {
      width: initialWidth,
      height: initialHeight,
      layout: {
        background: { color: 'transparent' },
        textColor: '#e4e7ef',
      },
      grid: {
        vertLines: { color: 'rgba(255,255,255,0.04)' },
        horzLines: { color: 'rgba(255,255,255,0.04)' },
      },
      rightPriceScale: {
        borderColor: 'rgba(255,255,255,0.08)',
        autoScale: true,
      },
      timeScale: {
        borderColor: 'rgba(255,255,255,0.08)',
      },
      crosshair: {
        mode: 0,
      },
    })

    const updateChartSize = () => {
      if (!containerRef.current || !chartRef.current) return
      requestAnimationFrame(() => {
        if (chartRef.current && containerRef.current) {
          const currentRect = containerRef.current.getBoundingClientRect()
          chartRef.current.applyOptions({
            width: Math.max(1, Math.floor(currentRect.width)),
            height: Math.max(1, Math.floor(currentRect.height || 160)),
          })
        }
      })
    }

    const resizeObserver = new ResizeObserver(updateChartSize)
    resizeObserver.observe(containerRef.current)

    const handleWindowResize = () => {
      updateChartSize()
    }
    window.addEventListener('resize', handleWindowResize)

    return () => {
      resizeObserver.disconnect()
      window.removeEventListener('resize', handleWindowResize)
      if (chartRef.current) {
        chartRef.current.remove()
        chartRef.current = null
        rsiSeriesRef.current = null
      }
    }
  }, [])

  useEffect(() => {
    if (!chartRef.current || chartData.length === 0) return

    const normalized = chartData
      .slice()
      .sort((a, b) => Number(a.time) - Number(b.time))
      .filter(
        (point, index, arr) =>
          index === 0 || point.time !== arr[index - 1].time,
      )

    if (!rsiSeriesRef.current) {
      rsiSeriesRef.current = chartRef.current.addSeries(LineSeries, {
        color: '#29b6f6',
        lineWidth: 2,
      }) as ISeriesApi<'Line'>
    }

    const rsiData = calculateRSI(normalized, 14)
    rsiSeriesRef.current.setData(rsiData)
    chartRef.current.timeScale().fitContent()
  }, [chartData])

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const handleMouseMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top
      setMousePos({ x, y })
    }

    const handleMouseLeave = () => {
      setMousePos(null)
    }

    container.addEventListener('mousemove', handleMouseMove)
    container.addEventListener('mouseleave', handleMouseLeave)

    return () => {
      container.removeEventListener('mousemove', handleMouseMove)
      container.removeEventListener('mouseleave', handleMouseLeave)
    }
  }, [])

  return (
    <Box
      sx={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        backgroundColor: 'rgba(255,255,255,0.02)',
      }}
    >
      <Typography
        variant="subtitle2"
        sx={{
          mb: 1,
          fontSize: { xs: '0.75rem', sm: '0.875rem' },
          px: 1,
          pt: 1,
        }}
      >
        RSI (14)
      </Typography>
      <Box
        sx={{
          position: 'relative',
          width: '100%',
          flexGrow: 1,
          minHeight: 0,
        }}
      >
        <Box
          ref={containerRef}
          sx={{
            width: '100%',
            height: '100%',
            position: 'relative',
          }}
        />
        {mousePos && (
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              pointerEvents: 'none',
              zIndex: 10,
            }}
          >
            <svg
              style={{
                width: '100%',
                height: '100%',
                position: 'absolute',
                top: 0,
                left: 0,
              }}
            >
              <line
                x1={mousePos.x}
                y1="0"
                x2={mousePos.x}
                y2="100%"
                stroke="#b0b0b0"
                strokeWidth="1"
              />
            </svg>
          </Box>
        )}
      </Box>
    </Box>
  )
}

