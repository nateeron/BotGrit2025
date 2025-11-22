import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  Alert,
  Box,
  CircularProgress,
  Typography,
} from '@mui/material'
import {
  AreaSeries,
  CandlestickSeries,
  HistogramSeries,
  LineSeries,
  LineStyle,
  createChart,
} from 'lightweight-charts'
import type {
  AreaSeriesPartialOptions,
  CandlestickData,
  CandlestickSeriesPartialOptions,
  HistogramSeriesPartialOptions,
  IChartApi,
  ISeriesApi,
  LineData,
  LineSeriesPartialOptions,
  UTCTimestamp,
} from 'lightweight-charts'
import {
  fetchBacktestTrades,
  fetchChartBootstrap,
  fetchChartWindow,
  subscribeBinanceKlines,
  type BacktestTrade,
  type OhlcPoint,
} from '../../services/api'
import { useTradingStore, type IndicatorConfig } from '../../store/tradingStore'
import {
  calculateBollingerBands,
  calculateEMA,
  calculateRSI,
  calculateSMA,
} from '../../utils/indicatorMath'
import ChartSettingsDialog from './ChartSettingsDialog'
import { useChartDataStore } from './useChartData'
import { useChartRefsStore } from './useChartRefsStore'

type MainSeries = ISeriesApi<'Candlestick'> | ISeriesApi<'Area'>

const sanitizeSeries = (points: OhlcPoint[]) => {
  const sorted = [...points].sort((a, b) => Number(a.time) - Number(b.time))
  return sorted.filter(
    (point, index) => index === 0 || point.time !== sorted[index - 1].time,
  )
}

const FALLBACK_VOLUME_MULTIPLIER = 120

type PriceLineInstance =
  | ReturnType<ISeriesApi<'Candlestick'>['createPriceLine']>
  | ReturnType<ISeriesApi<'Area'>['createPriceLine']>

const createIndicatorSeries = (
  chart: IChartApi,
  data: OhlcPoint[],
  config: IndicatorConfig,
) => {
  const seriesList: ISeriesApi<'Line'>[] = []
  const baseOptions: LineSeriesPartialOptions = {
    color: config.color,
    lineWidth: 2,
  }

  const addLine = (
    lineData: LineData<UTCTimestamp>[],
    options: Partial<LineSeriesPartialOptions> = {},
  ) => {
    if (!lineData.length) return
    const series = chart.addSeries(LineSeries, {
      ...baseOptions,
      ...options,
    }) as ISeriesApi<'Line'>
    series.setData(lineData)
    seriesList.push(series)
  }

  switch (config.type) {
    case 'sma':
      addLine(calculateSMA(data, config.params.period ?? 20))
      break
    case 'ema':
      addLine(calculateEMA(data, config.params.period ?? 20))
      break
    case 'bollinger': {
      const bands = calculateBollingerBands(
        data,
        config.params.period ?? 20,
        config.params.stdDev ?? 2,
      )
      addLine(bands.upper)
      addLine(bands.middle, { color: '#ffffff', lineWidth: 1 })
      addLine(bands.lower)
      break
    }
    case 'rsi':
      addLine(calculateRSI(data, config.params.period ?? 14), {
        priceScaleId: 'right',
      })
      break
    default:
      break
  }

  return seriesList
}

const toCandles = (points: OhlcPoint[]): CandlestickData<UTCTimestamp>[] =>
  points.map((point) => ({
    time: point.time,
    open: point.open,
    high: point.high,
    low: point.low,
    close: point.close,
  }))

const toAreaData = (points: OhlcPoint[]) =>
  points.map((point) => ({
    time: point.time,
    value: point.close,
  }))

const toHistogramData = (points: OhlcPoint[]) =>
  points.map((point) => ({
    time: point.time,
    value:
      point.volume ??
      Math.abs(point.close - point.open) * FALLBACK_VOLUME_MULTIPLIER +
        1000,
    color: point.close >= point.open ? '#26a69a' : '#ef5350',
  }))

const intervalToSeconds = (interval: string) => {
  const unit = interval.slice(-1)
  const value = Number(interval.slice(0, -1))
  const multipliers: Record<string, number> = {
    s: 1,
    m: 60,
    h: 3600,
    d: 86400,
    w: 604800,
  }
  return (multipliers[unit] ?? 60) * value
}

interface TradePriceLine {
  id: string
  price: number
  color: string
  label: string
}

const convertTradesToPriceLines = (
  trades: BacktestTrade[],
): TradePriceLine[] => {
  const priceLines: TradePriceLine[] = []
  const priceCounts = new Map<number, { buy: number; sell: number }>()

  trades.forEach((trade) => {
    const buyPrice = Number(trade.priceAction)
    
    if (!priceCounts.has(buyPrice)) {
      priceCounts.set(buyPrice, { buy: 0, sell: 0 })
    }
    const counts = priceCounts.get(buyPrice)!
    counts.buy++

    if (trade.timestem_sell && trade.status !== 0) {
      const sellPrice = Number(trade.priceSell)
      if (!priceCounts.has(sellPrice)) {
        priceCounts.set(sellPrice, { buy: 0, sell: 0 })
      }
      const sellCounts = priceCounts.get(sellPrice)!
      sellCounts.sell++
    }
  })

  priceCounts.forEach((counts, price) => {
    if (counts.buy > 0) {
      priceLines.push({
        id: `buy-${price}`,
        price,
        color: '#4A9FE6',
        label: `Buy ${counts.buy > 1 ? `x${counts.buy}` : ''} @ ${price.toFixed(4)}`,
      })
    }
    if (counts.sell > 0) {
      priceLines.push({
        id: `sell-${price}`,
        price,
        color: '#DA46EE',
        label: `Sell ${counts.sell > 1 ? `x${counts.sell}` : ''} @ ${price.toFixed(4)}`,
      })
    }
  })

  return priceLines
}

export const PriceChart = () => {
  const {
    selectedCoin,
    timeframe,
    chartMode,
    showIndicators,
    showVolume,
    fullscreenChart,
    toggleFullscreen,
    syncRsiChart,
  } = useTradingStore()
  
  const setMainChartRef = useChartRefsStore((state) => state.setMainChartRef)
  const setMainMousePos = useChartRefsStore((state) => state.setMainMousePos)
  const rsiMousePos = useChartRefsStore((state) => state.rsiMousePos)
  const rsiChartRef = useChartRefsStore((state) => state.rsiChartRef)

  const symbolPair = useMemo(
    () => `${selectedCoin}USDT`,
    [selectedCoin],
  )
  const interval = useMemo(
    () => (timeframe === '1D' ? '1d' : timeframe),
    [timeframe],
  )

  const containerRef = useRef<HTMLDivElement | null>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const mainSeriesRef = useRef<MainSeries | null>(null)
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null)
  const indicatorSeriesRef = useRef<Record<string, ISeriesApi<'Line'>[]>>({})
  const tradePriceLineRefs = useRef<Record<string, PriceLineInstance>>({})
  const realtimeCleanupRef = useRef<() => void>(() => {})
  const dataRef = useRef<OhlcPoint[]>([])
  const startTimestampRef = useRef<UTCTimestamp | null>(null)
  const loadingMoreRef = useRef(false)
  const isInitialLoadRef = useRef(true)

  const indicatorConfigs = useTradingStore((state) => state.indicatorConfigs)
  const loadIndicatorConfigs = useTradingStore(
    (state) => state.loadIndicatorConfigs,
  )
  const setChartData = useChartDataStore((state) => state.setChartData)

  const [data, setData] = useState<OhlcPoint[]>([])
  const [tradePriceLines, setTradePriceLines] = useState<TradePriceLine[]>([])
  const [trades, setTrades] = useState<BacktestTrade[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [mousePos, setMousePos] = useState<{ x: number; y: number } | null>(null)

  // Count Buy and Sell trades
  const tradeCounts = useMemo(() => {
    const buyCount = trades.filter((trade) => trade.status !== 0 || !trade.timestem_sell).length
    const sellCount = trades.filter((trade) => trade.timestem_sell && trade.status !== 0).length
    return { buy: buyCount, sell: sellCount }
  }, [trades])

  useEffect(() => {
    loadIndicatorConfigs()
  }, [loadIndicatorConfigs])


  useEffect(() => {
    if (!containerRef.current) return
    
    // Calculate initial size from container
    const containerRect = containerRef.current.getBoundingClientRect()
    const initialWidth = containerRect.width
    const initialHeight = containerRect.height

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
      crosshair: {
        mode: 0,
      },
      rightPriceScale: {
        borderColor: 'rgba(255,255,255,0.08)',
      },
      timeScale: {
        borderColor: 'rgba(255,255,255,0.08)',
        timeVisible: true,
        secondsVisible: false,
      },
    })
    
    // Register chart ref for sync
    setMainChartRef(chartRef.current)

    const updateChartSize = () => {
      if (!containerRef.current || !chartRef.current) return
      requestAnimationFrame(() => {
        if (chartRef.current && containerRef.current) {
          const currentRect = containerRef.current.getBoundingClientRect()
          chartRef.current.applyOptions({ 
            width: Math.max(1, Math.floor(currentRect.width)), 
            height: Math.max(1, Math.floor(currentRect.height))
          })
        }
      })
    }

    const resizeObserver = new ResizeObserver(updateChartSize)
    resizeObserver.observe(containerRef.current)
    
    // Also listen to window resize as fallback
    const handleWindowResize = () => {
      updateChartSize()
    }
    window.addEventListener('resize', handleWindowResize)

    return () => {
      resizeObserver.disconnect()
      window.removeEventListener('resize', handleWindowResize)
      realtimeCleanupRef.current?.()
      chartRef.current?.remove()
      chartRef.current = null
      setMainChartRef(null)
    }
  }, [setMainChartRef])

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const handleMouseMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top
      setMousePos({ x, y })
      
      // Sync mouse position to RSI chart if sync is enabled
      if (syncRsiChart && chartRef.current) {
        try {
          // Verify that the coordinate is valid (within chart bounds)
          const time = chartRef.current.timeScale().coordinateToTime(x)
          if (time !== null) {
            setMainMousePos({ x, y })
            // Clear RSI mouse pos to prevent sync back
            useChartRefsStore.getState().setRsiMousePos(null)
          } else {
            setMainMousePos(null)
          }
        } catch (e) {
          // Ignore errors
          setMainMousePos(null)
        }
      }
    }

    const handleMouseLeave = () => {
      setMousePos(null)
      if (syncRsiChart) {
        setMainMousePos(null)
      }
    }

    container.addEventListener('mousemove', handleMouseMove)
    container.addEventListener('mouseleave', handleMouseLeave)

    return () => {
      container.removeEventListener('mousemove', handleMouseMove)
      container.removeEventListener('mouseleave', handleMouseLeave)
    }
  }, [data, syncRsiChart, setMainMousePos])

  useEffect(() => {
    if (!fullscreenChart) return
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        toggleFullscreen()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [fullscreenChart, toggleFullscreen])

  const handleRealtimeCandle = useCallback((candle: OhlcPoint) => {
    const index = dataRef.current.findIndex(
      (item) => item.time === candle.time,
    )
    if (index >= 0) {
      dataRef.current[index] = candle
    } else {
      dataRef.current.push(candle)
    }
    const series = mainSeriesRef.current
    if (series?.seriesType() === 'Candlestick') {
      ;(series as ISeriesApi<'Candlestick'>).update(candle)
    } else if (series) {
      ;(series as ISeriesApi<'Area'>).update({
        time: candle.time,
        value: candle.close,
      })
    }
    setData([...dataRef.current])
    setChartData([...dataRef.current]) // Share data with RSI chart
    if (volumeSeriesRef.current) {
      volumeSeriesRef.current.update({
        time: candle.time,
        value:
          candle.volume ??
          Math.abs(candle.close - candle.open) * FALLBACK_VOLUME_MULTIPLIER +
            1000,
        color: candle.close >= candle.open ? '#26a69a' : '#ef5350',
      })
    }
  }, [])

  const loadTradePriceLines = useCallback(
    async (startTime: UTCTimestamp | null) => {
      if (!startTime) {
        setTradePriceLines([])
        return
      }
      try {
        const tradesData = await fetchBacktestTrades({
          symbol: symbolPair,
          interval,
          startTime,
          limit: 1000,
        })
        setTrades(tradesData)
        setTradePriceLines(convertTradesToPriceLines(tradesData))
      } catch (error) {
        console.warn('loadTradePriceLines error', error)
        setTrades([])
        setTradePriceLines([])
      }
    },
    [interval, symbolPair],
  )

  const loadMoreBars = useCallback(async () => {
    if (loadingMoreRef.current) return
    const startTime = startTimestampRef.current
    if (!startTime) return
    loadingMoreRef.current = true
    try {
      const seconds = intervalToSeconds(interval)
      const to = startTime - seconds
      const from = to - seconds * 800
      const windowData = sanitizeSeries(
        await fetchChartWindow({
          symbol: symbolPair,
          interval,
          from,
          to,
          limit: 1000,
        }),
      )
        if (windowData.length) {
        const merged = sanitizeSeries([...windowData, ...dataRef.current])
        dataRef.current = merged
        startTimestampRef.current = windowData[0].time
        setData(merged)
        setChartData(merged) // Share data with RSI chart
      }
    } catch (err) {
      console.warn('loadMoreBars failed', err)
    } finally {
      loadingMoreRef.current = false
    }
  }, [interval, symbolPair])

  useEffect(() => {
    const chart = chartRef.current
    if (!chart) return
    const handler = () => {
      const series = mainSeriesRef.current
      if (!series) return
      const range = chart.timeScale().getVisibleLogicalRange()
      if (!range) return
      const barsInfo = series.barsInLogicalRange(range)
      if (barsInfo?.barsBefore !== undefined && barsInfo.barsBefore < -20) {
        loadMoreBars()
      }
    }
    chart.timeScale().subscribeVisibleLogicalRangeChange(handler)
    return () => {
      chart.timeScale().unsubscribeVisibleLogicalRangeChange(handler)
    }
  }, [loadMoreBars])

  // Sync time scale between main chart and RSI chart
  useEffect(() => {
    const mainChart = chartRef.current
    if (!mainChart || !syncRsiChart) return

    const rsiChart = useChartRefsStore.getState().rsiChartRef
    if (!rsiChart) return

    const syncTimeScale = () => {
      try {
        const visibleRange = mainChart.timeScale().getVisibleRange()
        if (visibleRange) {
          rsiChart.timeScale().setVisibleRange(visibleRange)
        }
      } catch (e) {
        // Ignore sync errors
      }
    }

    const handler = () => {
      syncTimeScale()
    }

    mainChart.timeScale().subscribeVisibleTimeRangeChange(handler)
    
    // Initial sync
    syncTimeScale()

    return () => {
      mainChart.timeScale().unsubscribeVisibleTimeRangeChange(handler)
    }
  }, [syncRsiChart, data])

  // Sync cursor from RSI chart when sync is enabled
  useEffect(() => {
    if (!syncRsiChart || !chartRef.current || !rsiChartRef) {
      return
    }

    if (!rsiMousePos) {
      return
    }

    try {
      // Get time from RSI chart's mouse position
      const time = rsiChartRef.timeScale().coordinateToTime(rsiMousePos.x)
      if (time !== null) {
        // Convert time to coordinate in main chart
        const mainX = chartRef.current.timeScale().timeToCoordinate(time)
        if (mainX !== null && mainX >= 0) {
          setMousePos({ x: mainX, y: rsiMousePos.y })
        }
      }
    } catch (e) {
      // Ignore errors
    }
  }, [rsiMousePos, syncRsiChart, rsiChartRef])

  useEffect(() => {
    let cancelled = false
    const bootstrap = async () => {
      setLoading(true)
      setError(null)
      realtimeCleanupRef.current?.()
      // Reset initial load flag when symbol or interval changes
      isInitialLoadRef.current = true
      try {
        const candles = sanitizeSeries(
          await fetchChartBootstrap({
            symbol: symbolPair,
            interval,
            limit: 1000,
          }),
        )
        if (cancelled) return
        dataRef.current = candles
        startTimestampRef.current = candles[0]?.time ?? null
        setData(candles)
        setChartData(candles) // Share data with RSI chart
        await loadTradePriceLines(candles[0]?.time ?? null)
        realtimeCleanupRef.current = subscribeBinanceKlines(
          symbolPair,
          interval,
          handleRealtimeCandle,
        )
      } catch (err) {
        if (!cancelled) {
          setError('ไม่สามารถโหลดข้อมูลกราฟได้')
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }
    bootstrap()
    return () => {
      cancelled = true
    }
  }, [handleRealtimeCandle, interval, loadTradePriceLines, symbolPair])

  useEffect(() => {
    if (!chartRef.current || data.length === 0) return
    const chart = chartRef.current
    const normalized = sanitizeSeries(data)

    const clearPriceLines = () => {
      if (!mainSeriesRef.current) return
      // Clear trade price lines
      Object.values(tradePriceLineRefs.current).forEach((line) => {
        try {
          mainSeriesRef.current?.removePriceLine(line)
        } catch {
          /* noop */
        }
      })
      tradePriceLineRefs.current = {}
    }

    if (mainSeriesRef.current) {
      clearPriceLines()
      // Clear trade price lines
      Object.values(tradePriceLineRefs.current).forEach((line) => {
        try {
          mainSeriesRef.current?.removePriceLine(line)
        } catch {
          /* noop */
        }
      })
      tradePriceLineRefs.current = {}
      chart.removeSeries(mainSeriesRef.current)
      mainSeriesRef.current = null
    }
    Object.values(indicatorSeriesRef.current).forEach((lines) => {
      lines.forEach((line) => chart.removeSeries(line))
    })
    indicatorSeriesRef.current = {}
    if (volumeSeriesRef.current) {
      chart.removeSeries(volumeSeriesRef.current)
      volumeSeriesRef.current = null
    }

    if (chartMode === 'candle') {
      const options: CandlestickSeriesPartialOptions = {
        upColor: '#26a69a',
        downColor: '#ef5350',
        wickUpColor: '#26a69a',
        wickDownColor: '#ef5350',
        borderVisible: false,
      }
      const series = chart.addSeries(
        CandlestickSeries,
        options,
      ) as ISeriesApi<'Candlestick'>
      series.setData(toCandles(normalized))
      mainSeriesRef.current = series
    } else {
      const options: AreaSeriesPartialOptions = {
        topColor: 'rgba(25,118,210,0.35)',
        bottomColor: 'rgba(25,118,210,0.02)',
        lineColor: '#90caf9',
        lineWidth: 2,
      }
      const series = chart.addSeries(
        AreaSeries,
        options,
      ) as ISeriesApi<'Area'>
      series.setData(toAreaData(normalized))
      mainSeriesRef.current = series
    }

    if (showIndicators && indicatorConfigs.length > 0) {
      indicatorConfigs.forEach((config) => {
        const created = createIndicatorSeries(
          chart,
          normalized,
          config,
        )
        if (created.length > 0) {
          indicatorSeriesRef.current[config.id] = created
        }
      })
    }

    if (showVolume) {
      const histogramOptions: HistogramSeriesPartialOptions = {
        priceFormat: { type: 'volume' },
        priceLineVisible: false,
        baseLineColor: 'transparent',
      }
      const histogram = chart.addSeries(
        HistogramSeries,
        {
          ...histogramOptions,
          priceScaleId: '',
        },
      ) as ISeriesApi<'Histogram'>
      histogram.priceScale().applyOptions({
        scaleMargins: { top: 0.7, bottom: 0 },
      })
      histogram.setData(toHistogramData(normalized))
      volumeSeriesRef.current = histogram
    }

    // Only fit content on initial load, not on every data update
    const shouldFitContent = isInitialLoadRef.current
    if (shouldFitContent) {
      chart.timeScale().fitContent()
      isInitialLoadRef.current = false
    }
  }, [chartMode, data, indicatorConfigs, showIndicators, showVolume])


  // Create price lines for trades
  useEffect(() => {
    const series = mainSeriesRef.current
    if (!series) return
    
    if (chartMode !== 'candle') {
      // Clear trade price lines if not in candle mode
      Object.values(tradePriceLineRefs.current).forEach((line) => {
        try {
          series.removePriceLine(line)
        } catch {
          /* noop */
        }
      })
      tradePriceLineRefs.current = {}
      return
    }

    const existing = new Set(Object.keys(tradePriceLineRefs.current))
    
    tradePriceLines.forEach((lineConfig) => {
      if (tradePriceLineRefs.current[lineConfig.id]) {
        existing.delete(lineConfig.id)
        return
      }
      
      try {
        const line = series.createPriceLine({
          price: lineConfig.price,
          color: lineConfig.color,
          lineStyle: LineStyle.Solid,
          lineWidth: 2,
          axisLabelVisible: true,
          title: lineConfig.label,
        })
        tradePriceLineRefs.current[lineConfig.id] = line
      } catch (error) {
        console.warn('Failed to create price line:', error)
      }
    })

    // Remove lines that no longer exist
    existing.forEach((id) => {
      const line = tradePriceLineRefs.current[id]
      if (line) {
        try {
          series.removePriceLine(line)
        } catch {
          /* noop */
        }
        delete tradePriceLineRefs.current[id]
      }
    })
  }, [chartMode, tradePriceLines])

  useEffect(() => {
    const height = fullscreenChart ? 520 : 380
    chartRef.current?.applyOptions({ height })
  }, [fullscreenChart])

  const shouldShowPlaceholder = !loading && data.length === 0

  const chartShellStyles = fullscreenChart
    ? {
        position: 'fixed' as const,
        top: 120,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: 1500,
        backgroundColor: '#0d1117',
        padding: 2,
        display: 'flex',
        flexDirection: 'column' as const,
        gap: 2,
      }
    : {
        display: 'flex',
        flexDirection: 'column' as const,
        width: '100%',
        height: '100%',
        minHeight: 0,
        gap: 0,
      }

  const mainChartStyles = fullscreenChart
    ? {
        position: 'relative' as const,
        flexGrow: 1,
        borderRadius: 0,
        overflow: 'hidden',
        backgroundColor: 'rgba(255,255,255,0.02)',
      }
    : {
        position: 'relative' as const,
        flexGrow: 1,
        width: '100%',
        height: '100%',
        minHeight: 0,
        borderRadius: 0,
        border: 'none',
        overflow: 'hidden',
        backgroundColor: 'rgba(255,255,255,0.02)',
      }

  return (
    <Box sx={chartShellStyles}>
      <Box sx={mainChartStyles} tabIndex={fullscreenChart ? 0 : -1}>
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
        {error && !loading && (
          <Box
            sx={{
              position: 'absolute',
              inset: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              px: 3,
              zIndex: 2,
            }}
          >
            <Alert severity="error" variant="filled">
              {error}
            </Alert>
          </Box>
        )}
        {shouldShowPlaceholder && !error && (
          <Box
            sx={{
              position: 'absolute',
              inset: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'text.secondary',
              zIndex: 1,
            }}
          >
            <Typography variant="body2">
              ไม่พบข้อมูลสำหรับ {symbolPair} / {interval}
            </Typography>
          </Box>
        )}
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
        <Box
          sx={{
            position: 'absolute',
            top: 8,
            left: 8,
            display: 'flex',
            flexDirection: 'column',
            gap: 0.25,
            pointerEvents: 'none',
          }}
        >
          <Typography 
            variant="h6"
            sx={{ 
              fontSize: '0.875rem',
            }}
          >
            {selectedCoin}/USDT · {interval.toUpperCase()}
          </Typography>
          <Typography 
            variant="caption" 
            color="text.secondary"
            sx={{ 
              fontSize: '0.65rem',
              display: { xs: 'none', sm: 'block' },
            }}
          >
            {chartMode === 'candle' ? 'Candlestick' : 'Line'} Mode
            {showIndicators ? ' · Custom indicators' : ''}{' '}
            {showVolume ? ' · Volume' : ''}
          </Typography>
        </Box>
        {/* Trade Counts Display */}
        {trades.length > 0 && (
          <Box
            sx={{
              position: 'absolute',
              top: 8,
              right: 8,
              display: 'flex',
              flexDirection: 'column',
              gap: 0.5,
              pointerEvents: 'none',
              zIndex: 10,
            }}
          >
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 0.5,
              }}
            >
              <Box
                sx={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  backgroundColor: '#26a69a',
                }}
              />
              <Typography 
                variant="body2"
                sx={{ 
                  fontSize: '0.75rem',
                  fontWeight: 'bold',
                  color: '#26a69a',
                }}
              >
                Buy: {tradeCounts.buy}
              </Typography>
            </Box>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 0.5,
              }}
            >
              <Box
                sx={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  backgroundColor: '#ef5350',
                }}
              />
              <Typography 
                variant="body2"
                sx={{ 
                  fontSize: '0.75rem',
                  fontWeight: 'bold',
                  color: '#ef5350',
                }}
              >
                Sell: {tradeCounts.sell}
              </Typography>
            </Box>
          </Box>
        )}
        <ChartSettingsDialog />
      </Box>
    </Box>
  )
}

export default PriceChart
