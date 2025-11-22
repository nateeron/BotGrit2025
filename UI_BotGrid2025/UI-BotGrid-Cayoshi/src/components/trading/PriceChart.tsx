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
  SeriesMarker,
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

interface TradePriceLevel {
  id: string
  price: number
  color: string
  label: string
  startTime: UTCTimestamp
  marker?: SeriesMarker<UTCTimestamp>
}

const convertTradesToPriceLevels = (
  trades: BacktestTrade[],
  data: OhlcPoint[],
): TradePriceLevel[] => {
  const priceLevels: TradePriceLevel[] = []
  
  console.log('convertTradesToPriceLevels - Total trades:', trades.length, 'Data points:', data.length)
  
  if (trades.length === 0 || data.length === 0) {
    console.warn('convertTradesToPriceLevels - No trades or data')
    return priceLevels
  }

  // Create a map of timestamps to data points for quick lookup
  const dataMap = new Map<UTCTimestamp, OhlcPoint>()
  data.forEach((point) => {
    dataMap.set(point.time, point)
  })

  trades.forEach((trade, index) => {
    // Debug first few trades
    if (index < 3) {
      console.log(`Trade ${index}:`, {
        timestem_buy: trade.timestem_buy,
        priceAction: trade.priceAction,
        priceSell: trade.priceSell,
        timestem_sell: trade.timestem_sell,
        status: trade.status,
      })
    }

    // Convert buy timestamp to UTCTimestamp
    // timestem_buy is in milliseconds, need to convert to seconds for UTCTimestamp
    const buyTimestamp = Math.floor(trade.timestem_buy / 1000) as UTCTimestamp
    
    // Find the closest data point for buy action
    let buyTime: UTCTimestamp | null = null
    let buyPoint: OhlcPoint | null = null
    
    // Try exact match first
    if (dataMap.has(buyTimestamp)) {
      buyTime = buyTimestamp
      buyPoint = dataMap.get(buyTimestamp)!
    } else {
      // Find closest timestamp
      let closestDiff = Infinity
      let closestTime: UTCTimestamp | null = null
      data.forEach((point) => {
        const diff = Math.abs(Number(point.time) - buyTimestamp)
        if (diff < closestDiff) {
          closestDiff = diff
          closestTime = point.time
          buyPoint = point
        }
      })
      buyTime = closestTime
    }

    if (buyTime && buyPoint) {
      const buyPrice = Number(trade.priceAction)
      if (!isNaN(buyPrice) && buyPrice > 0) {
        // Determine position based on price vs bar
        const position: 'aboveBar' | 'belowBar' | 'inBar' = 
          buyPrice > buyPoint.high ? 'aboveBar' :
          buyPrice < buyPoint.low ? 'belowBar' : 'inBar'
        
        priceLevels.push({
          id: `buy-${trade.timestem_buy}-${buyPrice}`,
          price: buyPrice,
          color: '#4A9FE6',
          label: `Buy @ ${buyPrice.toFixed(4)}`,
          startTime: buyTime,
          marker: {
            time: buyTime,
            position,
            color: '#4A9FE6',
            shape: 'circle',
            text: `Buy @ ${buyPrice.toFixed(4)}`,
            size: 2, // Large marker at start point
          },
        })
      }
    }

    // Add sell price level if exists
    const hasSell = (trade.timestem_sell != null && trade.timestem_sell !== 0) ||
                    (trade.status !== 0 && trade.status !== null) ||
                    (trade.priceSell != null && Number(trade.priceSell) > 0)
    
    if (hasSell && trade.timestem_sell) {
      const sellTimestamp = Math.floor(trade.timestem_sell / 1000) as UTCTimestamp
      
      // Find the closest data point for sell action
      let sellTime: UTCTimestamp | null = null
      let sellPoint: OhlcPoint | null = null
      
      if (dataMap.has(sellTimestamp)) {
        sellTime = sellTimestamp
        sellPoint = dataMap.get(sellTimestamp)!
      } else {
        let closestDiff = Infinity
        let closestTime: UTCTimestamp | null = null
        data.forEach((point) => {
          const diff = Math.abs(Number(point.time) - sellTimestamp)
          if (diff < closestDiff) {
            closestDiff = diff
            closestTime = point.time
            sellPoint = point
          }
        })
        sellTime = closestTime
      }

      if (sellTime && sellPoint) {
        const sellPrice = Number(trade.priceSell)
        if (!isNaN(sellPrice) && sellPrice > 0) {
          const position: 'aboveBar' | 'belowBar' | 'inBar' = 
            sellPrice > sellPoint.high ? 'aboveBar' :
            sellPrice < sellPoint.low ? 'belowBar' : 'inBar'
          
          priceLevels.push({
            id: `sell-${trade.timestem_sell}-${sellPrice}`,
            price: sellPrice,
            color: '#DA46EE',
            label: `Sell @ ${sellPrice.toFixed(4)}`,
            startTime: sellTime,
            marker: {
              time: sellTime,
              position,
              color: '#DA46EE',
              shape: 'circle',
              text: `Sell @ ${sellPrice.toFixed(4)}`,
              size: 2, // Large marker at start point
            },
          })
        }
      }
    }
  })

  console.log('convertTradesToPriceLevels - Created price levels:', {
    total: priceLevels.length,
    buy: priceLevels.filter(p => p.color === '#4A9FE6').length,
    sell: priceLevels.filter(p => p.color === '#DA46EE').length,
  })

  return priceLevels
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
  const tradePriceLevelsRef = useRef<TradePriceLevel[]>([]) // Store price levels in ref
  const tradeMarkersRef = useRef<SeriesMarker<UTCTimestamp>[]>([]) // Store markers in ref
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
  const [trades, setTrades] = useState<BacktestTrade[]>([])
  const [tradePriceLevels, setTradePriceLevels] = useState<TradePriceLevel[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [mousePos, setMousePos] = useState<{ x: number; y: number } | null>(null)
  const showBuySellLines = useTradingStore((state) => state.showBuySellLines)
  const setReloadBacktestData = useTradingStore((state) => state.setReloadBacktestData)

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
    // Update data without triggering full series recreation
    // This prevents price lines from being removed
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
        console.log('loadTradePriceLines - No startTime, clearing price levels')
        tradePriceLevelsRef.current = [] // Clear ref
        tradeMarkersRef.current = [] // Clear ref
        setTradePriceLevels([])
        setTrades([])
        
        // Clear price lines
        if (mainSeriesRef.current) {
          Object.values(tradePriceLineRefs.current).forEach((line) => {
            try {
              mainSeriesRef.current?.removePriceLine(line)
            } catch {
              /* noop */
            }
          })
          tradePriceLineRefs.current = {}
        }
        
        // Clear markers on series if it exists
        if (mainSeriesRef.current && mainSeriesRef.current.seriesType() === 'Candlestick') {
          const series = mainSeriesRef.current as any
          if (typeof series.setMarkers === 'function') {
            series.setMarkers([])
          }
        }
        return
      }
      try {
        console.log('loadTradePriceLines - Fetching trades:', {
          symbol: symbolPair,
          interval,
          startTime,
        })
        const tradesData = await fetchBacktestTrades({
          symbol: symbolPair,
          interval,
          startTime,
          limit: 1000,
        })
        console.log('loadTradePriceLines - Received trades:', tradesData.length)
        setTrades(tradesData)
        // Convert trades to price levels using current data
        // Wait a bit to ensure dataRef.current is updated
        const currentData = dataRef.current.length > 0 ? dataRef.current : []
        const priceLevels = convertTradesToPriceLevels(tradesData, currentData)
        console.log('loadTradePriceLines - Setting price levels:', priceLevels.length, 'from data points:', currentData.length)
        tradePriceLevelsRef.current = priceLevels // Store in ref
        setTradePriceLevels(priceLevels)
        
        // Extract markers for series
        const markers = priceLevels
          .filter(level => level.marker)
          .map(level => level.marker!)
        tradeMarkersRef.current = markers
        
        // Price lines and markers will be created by the useEffect hook
        // No need to set them here as the effect will handle it
      } catch (error) {
        console.error('loadTradePriceLines error', error)
        tradePriceLevelsRef.current = [] // Clear ref
        tradeMarkersRef.current = [] // Clear ref
        setTrades([])
        setTradePriceLevels([])
        
        // Clear price lines
        if (mainSeriesRef.current) {
          Object.values(tradePriceLineRefs.current).forEach((line) => {
            try {
              mainSeriesRef.current?.removePriceLine(line)
            } catch {
              /* noop */
            }
          })
          tradePriceLineRefs.current = {}
        }
        
        // Clear markers on series if it exists
        if (mainSeriesRef.current && mainSeriesRef.current.seriesType() === 'Candlestick') {
          const series = mainSeriesRef.current as any
          if (typeof series.setMarkers === 'function') {
            series.setMarkers([])
          }
        }
      }
    },
    [interval, symbolPair],
  )

  const handleReloadBacktest = useCallback(() => {
    const startTime = startTimestampRef.current
    if (startTime) {
      loadTradePriceLines(startTime)
    }
  }, [loadTradePriceLines])

  // Register reload function to store
  useEffect(() => {
    setReloadBacktestData(() => handleReloadBacktest)
    return () => {
      setReloadBacktestData(null)
    }
  }, [handleReloadBacktest, setReloadBacktestData])

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
        // Load trade markers after data is set (this will update markers using current data)
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

  // Separate effect for updating series data (without recreating series)
  useEffect(() => {
    // Only update if series exists and data is available
    if (!mainSeriesRef.current || data.length === 0) return
    
    const normalized = sanitizeSeries(data)
    
    // Update existing series data without recreating
    try {
      if (mainSeriesRef.current.seriesType() === 'Candlestick') {
        ;(mainSeriesRef.current as ISeriesApi<'Candlestick'>).setData(toCandles(normalized))
      } else if (mainSeriesRef.current.seriesType() === 'Area') {
        ;(mainSeriesRef.current as ISeriesApi<'Area'>).setData(toAreaData(normalized))
      }
    } catch (error) {
      console.error('Error updating series data:', error)
    }
  }, [data])

  // Effect for creating/recreating series (only when chartMode, indicators, or volume changes)
  // Also recreate when data changes from empty to having data
  useEffect(() => {
    if (!chartRef.current) return
    const chart = chartRef.current
    
    // If no data, don't create series yet
    if (data.length === 0) {
      // Clear existing series if data is empty
      if (mainSeriesRef.current) {
        chart.removeSeries(mainSeriesRef.current)
        mainSeriesRef.current = null
      }
      return
    }
    
    const normalized = sanitizeSeries(data)
    
    // Check if series already exists and has the same type
    const needsRecreate = !mainSeriesRef.current || 
      (chartMode === 'candle' && mainSeriesRef.current.seriesType() !== 'Candlestick') ||
      (chartMode === 'line' && mainSeriesRef.current.seriesType() !== 'Area')

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

    // Only recreate series if needed (chartMode changed or series doesn't exist)
    if (needsRecreate) {
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
      
      // Clear indicators and volume when recreating
      Object.values(indicatorSeriesRef.current).forEach((lines) => {
        lines.forEach((line) => chart.removeSeries(line))
      })
      indicatorSeriesRef.current = {}
      if (volumeSeriesRef.current) {
        chart.removeSeries(volumeSeriesRef.current)
        volumeSeriesRef.current = null
      }

      // Create new series
      if (chartMode === 'candle') {
        const options: CandlestickSeriesPartialOptions = {
          upColor: '#26a69a',
          downColor: '#ef5350',
          wickUpColor: '#26a69a',
          wickDownColor: '#ef5350',
          borderVisible: false,
        }
        // Try using addCandlestickSeries if available (for markers support)
        const chartAny = chart as any
        let series: ISeriesApi<'Candlestick'>
        if (typeof chartAny.addCandlestickSeries === 'function') {
          series = chartAny.addCandlestickSeries(options) as ISeriesApi<'Candlestick'>
        } else {
          series = chart.addSeries(
            CandlestickSeries,
            options,
          ) as ISeriesApi<'Candlestick'>
        }
        series.setData(toCandles(normalized))
        mainSeriesRef.current = series
        
        // Price lines and markers will be created by the useEffect hook
        // No need to set them here as the effect will handle it
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
    }

    // Add indicators and volume (always update, not just when recreating)
    // Remove existing indicators first
    Object.values(indicatorSeriesRef.current).forEach((lines) => {
      lines.forEach((line) => chart.removeSeries(line))
    })
    indicatorSeriesRef.current = {}
    
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

    // Remove existing volume if exists
    if (volumeSeriesRef.current) {
      chart.removeSeries(volumeSeriesRef.current)
      volumeSeriesRef.current = null
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
  }, [chartMode, indicatorConfigs, showIndicators, showVolume, data.length]) // Add data.length to detect when data is loaded


  // Create price lines and markers for trades
  useEffect(() => {
    const series = mainSeriesRef.current
    if (!series) {
      console.log('Price lines effect - No series available')
      return
    }
    
    console.log('Price lines effect - chartMode:', chartMode, 'priceLevels:', tradePriceLevels.length, 'showBuySellLines:', showBuySellLines)
    
    // Clear all existing price lines first
    Object.values(tradePriceLineRefs.current).forEach((line) => {
      try {
        series.removePriceLine(line)
      } catch {
        /* noop */
      }
    })
    tradePriceLineRefs.current = {}
    
    if (chartMode !== 'candle') {
      // Clear markers if not in candle mode
      console.log('Price lines effect - Not in candle mode, clearing')
      try {
        const seriesAny = series as any
        if (typeof seriesAny.setMarkers === 'function') {
          seriesAny.setMarkers([])
        }
      } catch (error) {
        console.error('Failed to clear markers:', error)
      }
      return
    }

    // If showBuySellLines is false, remove all price lines and markers
    if (!showBuySellLines) {
      console.log('Price lines effect - Buy/Sell lines hidden, clearing')
      try {
        const seriesAny = series as any
        if (typeof seriesAny.setMarkers === 'function') {
          seriesAny.setMarkers([])
        }
      } catch (error) {
        console.error('Failed to clear markers:', error)
      }
      return
    }

    // Create price lines and markers
    const markers: SeriesMarker<UTCTimestamp>[] = []
    
    tradePriceLevels.forEach((level) => {
      try {
        // Create price line
        const priceLine = series.createPriceLine({
          price: level.price,
          color: level.color,
          lineStyle: LineStyle.Dashed,
          lineWidth: 1,
          axisLabelVisible: true,
          title: level.label,
        })
        tradePriceLineRefs.current[level.id] = priceLine
        
        // Add marker at start point if available
        if (level.marker) {
          markers.push(level.marker)
        }
      } catch (error) {
        console.error('Failed to create price line:', error, level)
      }
    })

    // Update markers on series
    try {
      const seriesAny = series as any
      if (typeof seriesAny.setMarkers === 'function') {
        seriesAny.setMarkers(markers)
        console.log(`Price lines effect - Created ${tradePriceLevels.length} price lines and ${markers.length} markers`)
      } else {
        console.warn('setMarkers is not available on this series type')
      }
    } catch (error) {
      console.error('Failed to set markers:', error)
    }
  }, [chartMode, tradePriceLevels, showBuySellLines])

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
