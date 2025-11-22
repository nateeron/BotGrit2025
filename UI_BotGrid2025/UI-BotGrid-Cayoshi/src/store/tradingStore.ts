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

export interface PriceLevel {
  id: string
  price: number
  side: 'Buy' | 'Sell'
  label?: string
}

export interface StudyConfig {
  id: string
  overlay: boolean
  label?: string
}

interface TradingState {
  selectedCoin: string
  timeframe: Timeframe
  chartMode: ChartMode
  showIndicators: boolean
  showVolume: boolean
  fullscreenChart: boolean
  sidebarCollapsed: boolean
  showSettingsDialog: boolean
  syncRsiChart: boolean
  indicatorConfigs: IndicatorConfig[]
  tvStudies: StudyConfig[]
  priceLevels: PriceLevel[]
  setSelectedCoin: (symbol: string) => void
  setTimeframe: (timeframe: Timeframe) => void
  setChartMode: (mode: ChartMode) => void
  toggleIndicators: () => void
  toggleVolume: () => void
  toggleFullscreen: () => void
  toggleSidebar: () => void
  setShowSettingsDialog: (show: boolean) => void
  toggleSyncRsiChart: () => void
  loadIndicatorConfigs: () => void
  addIndicatorConfig: (config: IndicatorConfig) => void
  updateIndicatorConfig: (config: IndicatorConfig) => void
  removeIndicatorConfig: (id: string) => void
  loadTradingViewStudies: () => void
  toggleTradingViewStudy: (study: StudyConfig) => void
  setPriceLevels: (levels: PriceLevel[]) => void
  resetToDefaults: () => void
  loadSettings: () => void
  showBuySellLines: boolean
  setShowBuySellLines: (show: boolean) => void
  reloadBacktestData: (() => void) | null
  setReloadBacktestData: (fn: (() => void) | null) => void
}

const INDICATOR_STORAGE_KEY = 'trading.indicators'
const TV_STUDY_STORAGE_KEY = 'trading.tvStudies'
const SETTINGS_STORAGE_KEY = 'trading.settings'

interface TradingSettings {
  selectedCoin: string
  timeframe: Timeframe
  chartMode: ChartMode
  showIndicators: boolean
  showVolume: boolean
  syncRsiChart: boolean
}

const DEFAULT_SETTINGS: TradingSettings = {
  selectedCoin: 'BTC',
  timeframe: '1h',
  chartMode: 'candle',
  showIndicators: true,
  showVolume: true,
  syncRsiChart: true,
}

const readSettingsFromSession = (): TradingSettings | null => {
  if (typeof window === 'undefined') {
    return null
  }
  const raw = window.sessionStorage.getItem(SETTINGS_STORAGE_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as TradingSettings
  } catch {
    return null
  }
}

const persistSettings = (settings: TradingSettings) => {
  if (typeof window === 'undefined') {
    return
  }
  window.sessionStorage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(settings))
}

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

const readTradingViewStudies = (): StudyConfig[] => {
  if (typeof window === 'undefined') {
    return []
  }
  const raw = window.sessionStorage.getItem(TV_STUDY_STORAGE_KEY)
  if (!raw) return []
  try {
    const parsed = JSON.parse(raw) as Record<string, StudyConfig>
    return Object.values(parsed)
  } catch {
    return []
  }
}

const persistTradingViewStudies = (studies: StudyConfig[]) => {
  if (typeof window === 'undefined') {
    return
  }
  const mapped = studies.reduce<Record<string, StudyConfig>>((acc, study) => {
    acc[study.id] = study
    return acc
  }, {})
  window.sessionStorage.setItem(TV_STUDY_STORAGE_KEY, JSON.stringify(mapped))
}

export const useTradingStore = create<TradingState>((set, get) => {
  // Initialize from sessionStorage or use defaults
  const savedSettings = readSettingsFromSession()
  const initialSettings = savedSettings || DEFAULT_SETTINGS

  return {
    selectedCoin: initialSettings.selectedCoin,
    timeframe: initialSettings.timeframe,
    chartMode: initialSettings.chartMode,
    showIndicators: initialSettings.showIndicators,
    showVolume: initialSettings.showVolume,
    fullscreenChart: false,
    sidebarCollapsed: false,
    showSettingsDialog: false,
    syncRsiChart: initialSettings.syncRsiChart,
    indicatorConfigs: [],
    tvStudies: [],
    priceLevels: [],
    showBuySellLines: true,
    setShowBuySellLines: (show) => set({ showBuySellLines: show }),
    reloadBacktestData: null,
    setReloadBacktestData: (fn) => set({ reloadBacktestData: fn }),
    setSelectedCoin: (symbol) => {
      set({ selectedCoin: symbol })
      const current = get()
      persistSettings({
        selectedCoin: symbol,
        timeframe: current.timeframe,
        chartMode: current.chartMode,
        showIndicators: current.showIndicators,
        showVolume: current.showVolume,
        syncRsiChart: current.syncRsiChart,
      })
    },
    setTimeframe: (timeframe) => {
      set({ timeframe })
      const current = get()
      persistSettings({
        selectedCoin: current.selectedCoin,
        timeframe,
        chartMode: current.chartMode,
        showIndicators: current.showIndicators,
        showVolume: current.showVolume,
        syncRsiChart: current.syncRsiChart,
      })
    },
    setChartMode: (chartMode) => {
      set({ chartMode })
      const current = get()
      persistSettings({
        selectedCoin: current.selectedCoin,
        timeframe: current.timeframe,
        chartMode,
        showIndicators: current.showIndicators,
        showVolume: current.showVolume,
        syncRsiChart: current.syncRsiChart,
      })
    },
  toggleIndicators: () => {
    const current = get()
    const newValue = !current.showIndicators
    set({ showIndicators: newValue })
    persistSettings({
      selectedCoin: current.selectedCoin,
      timeframe: current.timeframe,
      chartMode: current.chartMode,
      showIndicators: newValue,
      showVolume: current.showVolume,
      syncRsiChart: current.syncRsiChart,
    })
  },
  toggleVolume: () => {
    const current = get()
    const newValue = !current.showVolume
    set({ showVolume: newValue })
    persistSettings({
      selectedCoin: current.selectedCoin,
      timeframe: current.timeframe,
      chartMode: current.chartMode,
      showIndicators: current.showIndicators,
      showVolume: newValue,
      syncRsiChart: current.syncRsiChart,
    })
  },
  toggleFullscreen: () =>
    set((state) => ({ fullscreenChart: !state.fullscreenChart })),
  toggleSidebar: () =>
    set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
  setShowSettingsDialog: (show) => set({ showSettingsDialog: show }),
  toggleSyncRsiChart: () => {
    const current = get()
    const newValue = !current.syncRsiChart
    set({ syncRsiChart: newValue })
    persistSettings({
      selectedCoin: current.selectedCoin,
      timeframe: current.timeframe,
      chartMode: current.chartMode,
      showIndicators: current.showIndicators,
      showVolume: current.showVolume,
      syncRsiChart: newValue,
    })
  },
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
  loadTradingViewStudies: () => {
    const studies = readTradingViewStudies()
    set({ tvStudies: studies })
  },
  toggleTradingViewStudy: (study) => {
    const exists = get().tvStudies.find((item) => item.id === study.id)
    const next = exists
      ? get().tvStudies.filter((item) => item.id !== study.id)
      : [...get().tvStudies, study]
    persistTradingViewStudies(next)
    set({ tvStudies: next })
  },
  setPriceLevels: (levels) => set({ priceLevels: levels }),
  resetToDefaults: () => {
    set({
      selectedCoin: DEFAULT_SETTINGS.selectedCoin,
      timeframe: DEFAULT_SETTINGS.timeframe,
      chartMode: DEFAULT_SETTINGS.chartMode,
      showIndicators: DEFAULT_SETTINGS.showIndicators,
      showVolume: DEFAULT_SETTINGS.showVolume,
      syncRsiChart: DEFAULT_SETTINGS.syncRsiChart,
      indicatorConfigs: [],
    })
    persistSettings(DEFAULT_SETTINGS)
    persistIndicators([])
  },
  loadSettings: () => {
    const saved = readSettingsFromSession()
    if (saved) {
      set({
        selectedCoin: saved.selectedCoin,
        timeframe: saved.timeframe,
        chartMode: saved.chartMode,
        showIndicators: saved.showIndicators,
        showVolume: saved.showVolume,
        syncRsiChart: saved.syncRsiChart,
      })
    }
  },
  }
})

