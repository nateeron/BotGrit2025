import { create } from 'zustand'

type ChartMode = 'candle' | 'line'

export type Timeframe = '1m' | '5m' | '15m' | '1h' | '4h' | '1D'

export type IndicatorType = 'sma' | 'ema' | 'bollinger' | 'rsi'

export interface IndicatorConfig {
  id: string
  name: string
  type: IndicatorType
  params: Record<string, number>
  color: string
}

interface TradingState {
  selectedCoin: string
  timeframe: Timeframe
  chartMode: ChartMode
  showIndicators: boolean
  showVolume: boolean
  fullscreenChart: boolean
  indicatorConfigs: IndicatorConfig[]
  setSelectedCoin: (symbol: string) => void
  setTimeframe: (timeframe: Timeframe) => void
  setChartMode: (mode: ChartMode) => void
  toggleIndicators: () => void
  toggleVolume: () => void
  toggleFullscreen: () => void
  loadIndicatorConfigs: () => void
  addIndicatorConfig: (config: IndicatorConfig) => void
  updateIndicatorConfig: (config: IndicatorConfig) => void
  removeIndicatorConfig: (id: string) => void
}

const INDICATOR_STORAGE_KEY = 'trading.indicators'

const readIndicatorsFromSession = (): IndicatorConfig[] => {
  if (typeof window === 'undefined') {
    return []
  }
  const raw = window.sessionStorage.getItem(INDICATOR_STORAGE_KEY)
  if (!raw) return []
  try {
    const parsed = JSON.parse(raw) as Record<string, IndicatorConfig>
    return Object.values(parsed)
  } catch {
    return []
  }
}

const persistIndicators = (configs: IndicatorConfig[]) => {
  if (typeof window === 'undefined') {
    return
  }
  const mapped = configs.reduce<Record<string, IndicatorConfig>>(
    (acc, config) => {
      acc[config.id] = config
      return acc
    },
    {},
  )
  window.sessionStorage.setItem(
    INDICATOR_STORAGE_KEY,
    JSON.stringify(mapped),
  )
}

export const useTradingStore = create<TradingState>((set, get) => ({
  selectedCoin: 'BTC',
  timeframe: '1h',
  chartMode: 'candle',
  showIndicators: true,
  showVolume: true,
  fullscreenChart: false,
  indicatorConfigs: [],
  setSelectedCoin: (symbol) => set({ selectedCoin: symbol }),
  setTimeframe: (timeframe) => set({ timeframe }),
  setChartMode: (chartMode) => set({ chartMode }),
  toggleIndicators: () =>
    set((state) => ({ showIndicators: !state.showIndicators })),
  toggleVolume: () => set((state) => ({ showVolume: !state.showVolume })),
  toggleFullscreen: () =>
    set((state) => ({ fullscreenChart: !state.fullscreenChart })),
  loadIndicatorConfigs: () => {
    const configs = readIndicatorsFromSession()
    set({ indicatorConfigs: configs })
  },
  addIndicatorConfig: (config) => {
    const next = [...get().indicatorConfigs, config]
    persistIndicators(next)
    set({ indicatorConfigs: next })
  },
  updateIndicatorConfig: (config) => {
    const next = get().indicatorConfigs.map((item) =>
      item.id === config.id ? config : item,
    )
    persistIndicators(next)
    set({ indicatorConfigs: next })
  },
  removeIndicatorConfig: (id) => {
    const next = get().indicatorConfigs.filter((item) => item.id !== id)
    persistIndicators(next)
    set({ indicatorConfigs: next })
  },
}))

