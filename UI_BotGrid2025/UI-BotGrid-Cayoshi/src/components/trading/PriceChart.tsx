import { useEffect, useRef, useState } from 'react'
import { Box, CircularProgress, Typography } from '@mui/material'
import {
  AreaSeries,
  CandlestickSeries,
  HistogramSeries,
  LineSeries,
  createChart,
  LineStyle,
} from 'lightweight-charts'
import type {
  IChartApi,
  ISeriesApi,
  CandlestickSeriesPartialOptions,
  AreaSeriesPartialOptions,
  HistogramSeriesPartialOptions,
} from 'lightweight-charts'
import type { OhlcPoint } from '../../services/api'
import { getOHLC } from '../../services/api'
import { useTradingStore } from '../../store/tradingStore'

type MainSeries =
  | ISeriesApi<'Candlestick'>
  | ISeriesApi<'Area'>

export const PriceChart = () => {
  const {
    selectedCoin,
    timeframe,
    chartMode,
    showVolume,
    showIndicators,
    fullscreenChart,
  } = useTradingStore()
  const containerRef = useRef<HTMLDivElement | null>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const mainSeriesRef = useRef<MainSeries | null>(null)
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null)
  const indicatorSeriesRef = useRef<ISeriesApi<'Line'> | null>(null)
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<OhlcPoint[]>([])

  useEffect(() => {
    if (!containerRef.current) return

    chartRef.current = createChart(containerRef.current, {
      layout: {
        background: { color: 'transparent' },
        textColor: '#c6d1f0',
      },
      grid: {
        vertLines: { color: 'rgba(255,255,255,0.05)' },
        horzLines: { color: 'rgba(255,255,255,0.05)' },
      },
      crosshair: {
        mode: 1,
        vertLine: { color: '#1976d2', width: 1, style: LineStyle.Solid },
        horzLine: { color: '#1976d2', width: 1, style: LineStyle.Solid },
      },
      rightPriceScale: {
        borderColor: 'rgba(255,255,255,0.08)',
      },
      timeScale: {
        borderColor: 'rgba(255,255,255,0.08)',
      },
    })

    const resizeObserver = new ResizeObserver((entries) => {
      window.requestAnimationFrame(() => {
        if (!entries[0]) return
        const { width, height } = entries[0].contentRect
        chartRef.current?.applyOptions({ width, height })
      })
    })

    resizeObserver.observe(containerRef.current)

    return () => {
      resizeObserver.disconnect()
      chartRef.current?.remove()
      chartRef.current = null
    }
  }, [])

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      const points = await getOHLC(selectedCoin, timeframe)
      setData(points)
      setLoading(false)
    }
    fetchData()
  }, [selectedCoin, timeframe])

  useEffect(() => {
    if (!chartRef.current || data.length === 0) return

    if (mainSeriesRef.current) {
      chartRef.current.removeSeries(mainSeriesRef.current)
    }
    if (volumeSeriesRef.current) {
      chartRef.current.removeSeries(volumeSeriesRef.current)
      volumeSeriesRef.current = null
    }
    if (indicatorSeriesRef.current) {
      chartRef.current.removeSeries(indicatorSeriesRef.current)
      indicatorSeriesRef.current = null
    }

    if (chartMode === 'candle') {
      const options: CandlestickSeriesPartialOptions = {
        upColor: '#26a69a',
        downColor: '#ef5350',
        borderUpColor: '#26a69a',
        borderDownColor: '#ef5350',
        wickUpColor: '#26a69a',
        wickDownColor: '#ef5350',
      }
      const candlestick = chartRef.current.addSeries(
        CandlestickSeries,
        options,
      ) as ISeriesApi<'Candlestick'>
      candlestick.setData(data)
      mainSeriesRef.current = candlestick
    } else {
      const options: AreaSeriesPartialOptions = {
        topColor: 'rgba(25,118,210,0.4)',
        bottomColor: 'rgba(25,118,210,0.05)',
        lineColor: '#90caf9',
        lineWidth: 2,
      }
      const area = chartRef.current.addSeries(AreaSeries, options) as ISeriesApi<'Area'>
      area.setData(
        data.map((point) => ({
          time: point.time,
          value: point.close,
        })),
      )
      mainSeriesRef.current = area
    }

    if (showIndicators) {
      const indicator = chartRef.current.addSeries(LineSeries, {
        color: '#fdd835',
        lineWidth: 2,
      }) as ISeriesApi<'Line'>
      indicator.setData(
        data.map((point, idx, array) => {
          const window = array.slice(Math.max(0, idx - 9), idx + 1)
          const avg =
            window.reduce((sum, candle) => sum + candle.close, 0) / window.length
          return {
            time: point.time,
            value: avg,
          }
        }),
      )
      indicatorSeriesRef.current = indicator
    }

    if (showVolume) {
      const histogramOptions: HistogramSeriesPartialOptions = {
        priceFormat: {
          type: 'volume',
        },
        priceLineVisible: false,
        color: 'rgba(255,255,255,0.3)',
        baseLineColor: 'transparent',
      }
      const histogram = chartRef.current.addSeries(HistogramSeries, {
        ...histogramOptions,
        priceScaleId: '',
      }) as ISeriesApi<'Histogram'>
      histogram.priceScale().applyOptions({
        scaleMargins: {
          top: 0.7,
          bottom: 0,
        },
      })
      histogram.setData(
        data.map((point) => ({
          time: point.time,
          value: Math.abs(point.close - point.open) * 120 + 1000,
          color: point.close >= point.open ? '#26a69a' : '#ef5350',
        })),
      )
      volumeSeriesRef.current = histogram
    }

    chartRef.current.timeScale().fitContent()
  }, [chartMode, data, showIndicators, showVolume])

  useEffect(() => {
    const height = fullscreenChart ? 520 : 380
    chartRef.current?.applyOptions({ height })
  }, [fullscreenChart])

  return (
    <Box
      sx={{
        position: 'relative',
        flexGrow: 1,
        minHeight: fullscreenChart ? 520 : 380,
        borderRadius: 3,
        overflow: 'hidden',
        backgroundColor: 'rgba(255,255,255,0.02)',
      }}
    >
      {loading && (
        <Box
          sx={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 2,
            backdropFilter: 'blur(2px)',
          }}
        >
          <CircularProgress />
        </Box>
      )}
      <Box
        ref={containerRef}
        sx={{
          width: '100%',
          height: '100%',
        }}
      />
      <Box
        sx={{
          position: 'absolute',
          top: 16,
          left: 16,
          display: 'flex',
          flexDirection: 'column',
          gap: 0.5,
        }}
      >
        <Typography variant="h6">{selectedCoin}/USDT</Typography>
        <Typography variant="caption" color="text.secondary">
          Timeframe: {timeframe} · {chartMode === 'candle' ? 'Candles' : 'Line'}
          {showIndicators ? ' · Indicators' : ''} {showVolume ? ' · Volume' : ''}
        </Typography>
      </Box>
    </Box>
  )
}

export default PriceChart

