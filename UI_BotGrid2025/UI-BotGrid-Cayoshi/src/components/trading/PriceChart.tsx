import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  Alert,
  Box,
  CircularProgress,
  Typography,
  IconButton,
  Tooltip,
} from '@mui/material'
import SettingsIcon from '@mui/icons-material/Settings'
import {
  AreaSeries,
  CandlestickSeries,
  HistogramSeries,
  LineSeries,
  LineStyle,
  createSeriesMarkers,
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
  SeriesMarker,
  ISeriesMarkersPluginApi,
  Time,
  UTCTimestamp,
} from 'lightweight-charts'
import {
  fetchBacktestTrades,
  fetchChartBootstrap,
  fetchChartWindow,
  getPriceLevels,
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

const convertTradesToMarkers = (
  trades: BacktestTrade[],
): SeriesMarker<UTCTimestamp>[] => {
  const duplicates = new Map<number, number>()
  return trades.flatMap((trade) => {
    const buyTime = (Math.floor(trade.timestem_buy / 1000) +
      7 * 60 * 60) as UTCTimestamp
    const buyMarker: SeriesMarker<UTCTimestamp> = {
      time: buyTime,
      position: 'belowBar',
      color: '#4A9FE6',
      shape: 'arrowUp',
      text: `Buy @ ${Number(trade.priceAction).toFixed(4)}`,
    }
    if (!trade.timestem_sell || trade.status === 0) {
      return [buyMarker]
    }
    const sellTime = (Math.floor(trade.timestem_sell / 1000) +
      7 * 60 * 60) as UTCTimestamp
    const duplicateCount = duplicates.get(trade.timestem_sell) ?? 0
    duplicates.set(trade.timestem_sell, duplicateCount + 1)
    const suffix = duplicateCount > 0 ? ` x${duplicateCount + 1}` : ''
    const sellMarker: SeriesMarker<UTCTimestamp> = {
      time: sellTime,
      position: 'aboveBar',
      color: '#DA46EE',
      shape: 'arrowDown',
      text: `Sell @ ${Number(trade.priceSell).toFixed(4)}${suffix}`,
    }
    return [buyMarker, sellMarker]
  })
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
    setShowSettingsDialog,
  } = useTradingStore()

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
  const rsiChartRef = useRef<IChartApi | null>(null)
  const mainSeriesRef = useRef<MainSeries | null>(null)
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null)
  const indicatorSeriesRef = useRef<Record<string, ISeriesApi<'Line'>[]>>({})
  const rsiSeriesRef = useRef<ISeriesApi<'Line'> | null>(null)
  const priceLineRefs = useRef<Record<string, PriceLineInstance>>({})
  const realtimeCleanupRef = useRef<() => void>(() => {})
  const dataRef = useRef<OhlcPoint[]>([])
  const startTimestampRef = useRef<UTCTimestamp | null>(null)
  const loadingMoreRef = useRef(false)
  const markersPluginRef = useRef<ISeriesMarkersPluginApi<Time> | null>(null)
  const isInitialLoadRef = useRef(true)

  const indicatorConfigs = useTradingStore((state) => state.indicatorConfigs)
  const loadIndicatorConfigs = useTradingStore(
    (state) => state.loadIndicatorConfigs,
  )
  const priceLevels = useTradingStore((state) => state.priceLevels)
  const setPriceLevels = useTradingStore((state) => state.setPriceLevels)

  const [data, setData] = useState<OhlcPoint[]>([])
  const [markers, setMarkers] = useState<SeriesMarker<UTCTimestamp>[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [mousePos, setMousePos] = useState<{ x: number; y: number } | null>(null)
  const [rsiMousePos, setRsiMousePos] = useState<{ x: number; y: number } | null>(null)

  useEffect(() => {
    loadIndicatorConfigs()
  }, [loadIndicatorConfigs])

  useEffect(() => {
    let active = true
    const loadLevels = async () => {
      const levels = await getPriceLevels(selectedCoin)
      if (active) setPriceLevels(levels)
    }
    loadLevels()
    return () => {
      active = false
    }
  }, [selectedCoin, setPriceLevels])

  useEffect(() => {
    if (!containerRef.current) return
    chartRef.current = createChart(containerRef.current, {
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
      realtimeCleanupRef.current?.()
      chartRef.current?.remove()
      chartRef.current = null
    }
  }, [])

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const handleMouseMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top
      setMousePos({ x, y })

      // Sync to RSI chart - sync vertical line position
      try {
        const rsiContainer = document.getElementById('tv_rsi_container')
        if (rsiContainer) {
          const rsiRect = rsiContainer.getBoundingClientRect()
          const rsiX = e.clientX - rsiRect.left
          if (rsiX >= 0 && rsiX <= rsiRect.width) {
            setRsiMousePos({ x: rsiX, y: 0 })
          } else {
            setRsiMousePos(null)
          }
        }
      } catch (e) {
        // Ignore sync errors
      }
    }

    const handleMouseLeave = () => {
      setMousePos(null)
      setRsiMousePos(null)
    }

    container.addEventListener('mousemove', handleMouseMove)
    container.addEventListener('mouseleave', handleMouseLeave)

    return () => {
      container.removeEventListener('mousemove', handleMouseMove)
      container.removeEventListener('mouseleave', handleMouseLeave)
    }
  }, [data])


  useEffect(() => {
    const container = document.getElementById('tv_rsi_container')
    if (!container) return
    if (rsiChartRef.current) {
      rsiChartRef.current.remove()
      rsiChartRef.current = null
      rsiSeriesRef.current = null
    }
    rsiChartRef.current = createChart(container, {
      height: 160,
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
    const handleResize = () => {
      if (!container || !rsiChartRef.current) return
      const { width } = container.getBoundingClientRect()
      rsiChartRef.current.applyOptions({ width })
    }
    window.addEventListener('resize', handleResize)
    return () => {
      window.removeEventListener('resize', handleResize)
      if (rsiChartRef.current) {
        rsiChartRef.current.remove()
        rsiChartRef.current = null
        rsiSeriesRef.current = null
      }
    }
  }, [fullscreenChart])


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

  const loadMarkers = useCallback(
    async (startTime: UTCTimestamp | null) => {
      if (!startTime) {
        setMarkers([])
        return
      }
      try {
        const trades = await fetchBacktestTrades({
          symbol: symbolPair,
          interval,
          startTime,
          limit: 1000,
        })
        setMarkers(convertTradesToMarkers(trades))
      } catch (markerError) {
        console.warn('loadMarkers error', markerError)
        setMarkers([])
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
        await loadMarkers(candles[0]?.time ?? null)
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
  }, [handleRealtimeCandle, interval, loadMarkers, symbolPair])

  useEffect(() => {
    if (!chartRef.current || data.length === 0) return
    const chart = chartRef.current
    const normalized = sanitizeSeries(data)

    const clearPriceLines = () => {
      if (!mainSeriesRef.current) return
      Object.values(priceLineRefs.current).forEach((line) => {
        try {
          mainSeriesRef.current?.removePriceLine(line)
        } catch {
          /* noop */
        }
      })
      priceLineRefs.current = {}
    }

    if (mainSeriesRef.current) {
      clearPriceLines()
      chart.removeSeries(mainSeriesRef.current)
      mainSeriesRef.current = null
    }
    if (markersPluginRef.current) {
      markersPluginRef.current.detach()
      markersPluginRef.current = null
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
      markersPluginRef.current = createSeriesMarkers(series)
      markersPluginRef.current?.setMarkers(markers as SeriesMarker<Time>[])
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

    if (rsiChartRef.current) {
      if (!rsiSeriesRef.current) {
        rsiSeriesRef.current = rsiChartRef.current.addSeries(LineSeries, {
          color: '#29b6f6',
          lineWidth: 2,
        }) as ISeriesApi<'Line'>
      }
      const rsiData = calculateRSI(normalized, 14)
      rsiSeriesRef.current.setData(rsiData)
      // Only fit RSI chart on initial load
      if (shouldFitContent) {
        rsiChartRef.current.timeScale().fitContent()
      }
    }
  }, [chartMode, data, indicatorConfigs, markers, showIndicators, showVolume])

  useEffect(() => {
    const series = mainSeriesRef.current
    if (!series) return
    const existing = new Set(Object.keys(priceLineRefs.current))
    priceLevels.forEach((level) => {
      if (priceLineRefs.current[level.id]) {
        existing.delete(level.id)
        return
      }
      const line = series.createPriceLine({
        price: level.price,
        color: level.side === 'Buy' ? '#26a69a' : '#ef5350',
        lineStyle: LineStyle.Dashed,
        lineWidth: 1,
        axisLabelVisible: true,
        title: level.label ?? level.side,
      })
      priceLineRefs.current[level.id] = line
    })
    existing.forEach((id) => {
      const line = priceLineRefs.current[id]
      if (line) {
        try {
          series.removePriceLine(line)
        } catch {
          /* noop */
        }
        delete priceLineRefs.current[id]
      }
    })
  }, [priceLevels])

  useEffect(() => {
    if (!markersPluginRef.current) return
    if (chartMode !== 'candle') {
      markersPluginRef.current.setMarkers([])
      return
    }
    markersPluginRef.current.setMarkers(markers as SeriesMarker<Time>[])
  }, [chartMode, markers])

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
        gap: 2,
      }

  const mainChartStyles = fullscreenChart
    ? {
        position: 'relative' as const,
        flexGrow: 1,
        borderRadius: 3,
        overflow: 'hidden',
        backgroundColor: 'rgba(255,255,255,0.02)',
      }
    : {
        position: 'relative' as const,
        flexGrow: 1,
        minHeight: 380,
        borderRadius: 3,
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
            top: 16,
            left: 16,
            display: 'flex',
            flexDirection: 'column',
            gap: 0.5,
            pointerEvents: 'none',
          }}
        >
          <Typography variant="h6">
            {selectedCoin}/USDT · {interval.toUpperCase()}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {chartMode === 'candle' ? 'Candlestick' : 'Line'} Mode
            {showIndicators ? ' · Custom indicators' : ''}{' '}
            {showVolume ? ' · Volume' : ''}
          </Typography>
        </Box>
        <Box
          sx={{
            position: 'absolute',
            top: 16,
            right: 16,
            pointerEvents: 'auto',
          }}
        >
          <Tooltip title="Chart Settings">
            <IconButton
              onClick={() => setShowSettingsDialog(true)}
              sx={{
                color: '#e4e7ef',
                backgroundColor: 'rgba(255,255,255,0.08)',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.12)',
                },
              }}
            >
              <SettingsIcon />
            </IconButton>
          </Tooltip>
        </Box>
        <ChartSettingsDialog />
      </Box>
      <Box
        sx={{
          borderRadius: 3,
          backgroundColor: 'rgba(255,255,255,0.02)',
          p: 1,
          minHeight: 160,
        }}
      >
        <Typography variant="subtitle2" sx={{ mb: 1 }}>
          RSI (14)
        </Typography>
        <Box sx={{ position: 'relative', width: '100%', height: 140 }}>
          <Box id="tv_rsi_container" sx={{ width: '100%', height: '100%' }} />
          {rsiMousePos && (
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
                  x1={rsiMousePos.x}
                  y1="0"
                  x2={rsiMousePos.x}
                  y2="100%"
                  stroke="#b0b0b0"
                  strokeWidth="1"
                />
              </svg>
            </Box>
          )}
        </Box>
      </Box>
    </Box>
  )
}

export default PriceChart
