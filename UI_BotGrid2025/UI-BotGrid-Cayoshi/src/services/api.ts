import axios from 'axios'
import type { UTCTimestamp } from 'lightweight-charts'

// Mock helper to simulate latency
const delay = (ms = 400) => new Promise((resolve) => setTimeout(resolve, ms))

export interface CoinSummary {
  symbol: string
  name: string
  price: number
  changePct: number
}

export interface OhlcPoint {
  time: UTCTimestamp
  open: number
  high: number
  low: number
  close: number
  volume?: number
}

export interface OrderItem {
  id: string
  side: 'Buy' | 'Sell'
  price: number
  amount: number
  pnl: number
  status: 'Open' | 'Filled' | 'Cancelled'
}

export interface ReportSummary {
  label: string
  profit: number
  orders: number
  winRate: number
}

export interface PriceLevel {
  id: string
  price: number
  side: 'Buy' | 'Sell'
  label?: string
}

const mockCoins: CoinSummary[] = [
  { symbol: 'BTC', name: 'Bitcoin', price: 97250, changePct: 2.4 },
  { symbol: 'ETH', name: 'Ethereum', price: 3550, changePct: -1.1 },
  { symbol: 'XRP', name: 'Ripple', price: 0.67, changePct: 0.8 },
  { symbol: 'BNB', name: 'Binance Coin', price: 645, changePct: 1.7 },
  { symbol: 'SOL', name: 'Solana', price: 142, changePct: 3.2 },
  { symbol: 'ADA', name: 'Cardano', price: 0.58, changePct: -0.4 },
  { symbol: 'DOGE', name: 'Dogecoin', price: 0.19, changePct: 5.6 },
]

const randomPrice = (base: number, variance: number) =>
  base + (Math.random() - 0.5) * variance

const buildOhlc = (basePrice: number, candles = 120): OhlcPoint[] => {
  const points: OhlcPoint[] = []
  let price = basePrice

  for (let i = 0; i < candles; i += 1) {
    const open = price
    const high = open + Math.random() * 50
    const low = open - Math.random() * 50
    const close = randomPrice(open, 30)
    price = close
    points.push({
      time: (Math.floor(Date.now() / 1000) - (candles - i) * 60) as UTCTimestamp,
      open,
      high,
      low,
      close,
      volume: Math.abs(close - open) * 1000,
    })
  }
  return points
}

export const getCoins = async (): Promise<CoinSummary[]> => {
  await delay()
  return mockCoins.map((coin) => ({
    ...coin,
    price: Number(randomPrice(coin.price, coin.price * 0.02).toFixed(2)),
    changePct: Number(randomPrice(coin.changePct, 2).toFixed(2)),
  }))
}

export const getOHLC = async (
  symbol: string,
  timeframe: string,
): Promise<OhlcPoint[]> => {
  await delay()
  const base =
    mockCoins.find((coin) => coin.symbol === symbol)?.price ?? 2500
  const timeframeDensity: Record<string, number> = {
    '1m': 180,
    '5m': 150,
    '15m': 130,
    '1h': 120,
    '4h': 100,
    '1D': 80,
  }
  const candles = timeframeDensity[timeframe] ?? 120
  return buildOhlc(base, candles)
}

export const getOpenOrders = async (): Promise<OrderItem[]> => {
  await delay()
  return Array.from({ length: 6 }).map((_, idx) => ({
    id: `ORD-${1480 + idx}`,
    side: idx % 2 === 0 ? 'Buy' : 'Sell' as const,
    price: Number(randomPrice(2400, 400).toFixed(2)),
    amount: Number(randomPrice(0.5, 0.5).toFixed(3)),
    pnl: Number(randomPrice(120, 200).toFixed(2)),
    status: ['Open', 'Filled', 'Open', 'Cancelled'][idx % 4] as OrderItem['status'],
  }))
}

export const getDailyReport = async (): Promise<ReportSummary[]> => {
  await delay()
  const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  return labels.map((label) => ({
    label,
    profit: Number(randomPrice(1500, 800).toFixed(0)),
    orders: Math.floor(randomPrice(24, 10)),
    winRate: Number(randomPrice(58, 10).toFixed(1)),
  }))
}

export const pingMockApi = async () => {
  // helper to demonstrate axios usage
  try {
    await axios.get('https://httpbin.org/get')
  } catch {
    // ignore network errors for mock
  }
}

export const getPriceLevels = async (
  symbol: string,
  count = 220,
): Promise<PriceLevel[]> => {
  await delay()
  const base =
    mockCoins.find((coin) => coin.symbol === symbol) ??
    mockCoins[Math.floor(Math.random() * mockCoins.length)]
  const basePrice = base.price
  return Array.from({ length: count }).map((_, idx) => {
    const offset = idx - Math.floor(count / 2)
    const variance = (Math.random() - 0.5) * basePrice * 0.01
    const price = Number((basePrice + offset * 25 + variance).toFixed(2))
    const side = idx % 2 === 0 ? 'Buy' : 'Sell'
    return {
      id: `${symbol}-${idx}`,
      price,
      side,
      label: `${side} #${idx + 1}`,
    }
  })
}

// -----------------------------------------------------------------------------
// Real data services for Lightweight Charts
// -----------------------------------------------------------------------------

const INFO_PRICE_BASE_URL =
  import.meta.env.VITE_INFO_PRICE_URL ?? 'http://127.0.0.1:45441'
const BOTGRID_BASE_URL =
  import.meta.env.VITE_BOTGRID_URL ?? 'http://127.0.0.1:45441'
const BANGKOK_OFFSET_SECONDS = 7 * 60 * 60

const formatTimestampForApi = (unixSeconds: number) => {
  const date = new Date((unixSeconds - BANGKOK_OFFSET_SECONDS) * 1000)
  const year = date.getUTCFullYear()
  const month = String(date.getUTCMonth() + 1).padStart(2, '0')
  const day = String(date.getUTCDate()).padStart(2, '0')
  const hours = String(date.getUTCHours()).padStart(2, '0')
  const minutes = String(date.getUTCMinutes()).padStart(2, '0')
  const seconds = String(date.getUTCSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

const toUTCTimestamp = (ms: number): UTCTimestamp =>
  (Math.floor(ms / 1000) + BANGKOK_OFFSET_SECONDS) as UTCTimestamp

const postJson = async <T>(url: string, payload: unknown): Promise<T> => {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`)
  }
  return response.json() as Promise<T>
}

interface InfoPriceRow {
  timestamp: number
  open: number | string
  high: number | string
  low: number | string
  close: number | string
  volume?: number | string
}

const normalizeRows = (rows: InfoPriceRow[]): OhlcPoint[] =>
  rows.map((row) => ({
    time: toUTCTimestamp(row.timestamp),
    open: Number(row.open),
    high: Number(row.high),
    low: Number(row.low),
    close: Number(row.close),
    volume: row.volume ? Number(row.volume) : undefined,
  }))

const buildInfoPricePayload = (
  symbol: string,
  interval: string,
  limit?: number,
  from?: number,
  to?: number,
) => {
  // Get client timezone
  const clientTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone
  // Expected Bangkok timezone
  const expectedTimezone = 'Asia/Bangkok'
  
  return {
    symbol,
    tf: interval,
    getAll: false,
    datefrom: from ? formatTimestampForApi(from) : '',
    dateto: to ? formatTimestampForApi(to) : '',
    ohlc: 'ohlc',
    limit: limit ?? 1000,
    timezone: clientTimezone, // Send client timezone for validation
  }
}

export interface FetchChartParams {
  symbol: string
  interval: string
  from?: number
  to?: number
  limit?: number
}

export const fetchChartBootstrap = async (
  params: FetchChartParams,
): Promise<OhlcPoint[]> => {
  const rows = await postJson<InfoPriceRow[]>(
    `${INFO_PRICE_BASE_URL}/infoPrice/getprice_start`,
    buildInfoPricePayload(
      params.symbol,
      params.interval,
      params.limit,
      params.from,
      params.to,
    ),
  )
  return normalizeRows(rows)
}

export const fetchChartWindow = async (
  params: FetchChartParams,
): Promise<OhlcPoint[]> => {
  const rows = await postJson<InfoPriceRow[]>(
    `${INFO_PRICE_BASE_URL}/infoPrice/Load_bar_lazy`,
    buildInfoPricePayload(
      params.symbol,
      params.interval,
      params.limit,
      params.from,
      params.to,
    ),
  )
  return normalizeRows(rows)
}

export interface BacktestTrade {
  timestem_buy: number
  timestem_sell: number | null
  priceAction: number
  priceSell: number
  status: number
}

export interface BacktestParams {
  symbol: string
  interval: string
  startTime: number
  limit?: number
}

export const fetchBacktestTrades = async (
  params: BacktestParams,
): Promise<BacktestTrade[]> =>
  postJson<BacktestTrade[]>(
    `${BOTGRID_BASE_URL}/botgrid/data_Backtest`,
    {
      symbol: params.symbol,
      tf: params.interval,
      DateFrom: params.startTime,
      limit: params.limit ?? 1000,
    },
  )

export type KlineListener = (candle: OhlcPoint) => void

export const subscribeBinanceKlines = (
  symbol: string,
  interval: string,
  listener: KlineListener,
) => {
  if (typeof window === 'undefined' || typeof WebSocket === 'undefined') {
    return () => {}
  }
  const stream = `${symbol.toLowerCase()}@kline_${interval}`
  const socket = new WebSocket(`wss://stream.binance.com:9443/ws/${stream}`)

  socket.onmessage = (event) => {
    try {
      const payload = JSON.parse(event.data)
      const candle = payload?.k
      if (!candle) return
      const point: OhlcPoint = {
        time: toUTCTimestamp(candle.t),
        open: Number(candle.o),
        high: Number(candle.h),
        low: Number(candle.l),
        close: Number(candle.c),
        volume: Number(candle.v),
      }
      listener(point)
    } catch {
      // ignore malformed messages
    }
  }

  socket.onerror = () => {
    socket.close()
  }

  return () => {
    socket.close()
  }
}

