import { create } from 'zustand'

type ChartMode = 'candle' | 'line'

export type Timeframe = '1m' | '5m' | '15m' | '1h' | '4h' | '1D'

interface TradingState {
  selectedCoin: string
  timeframe: Timeframe
  chartMode: ChartMode
  showIndicators: boolean
  showVolume: boolean
  fullscreenChart: boolean
  setSelectedCoin: (symbol: string) => void
  setTimeframe: (timeframe: Timeframe) => void
  setChartMode: (mode: ChartMode) => void
  toggleIndicators: () => void
  toggleVolume: () => void
  toggleFullscreen: () => void
}

export const useTradingStore = create<TradingState>((set) => ({
  selectedCoin: 'BTC',
  timeframe: '1h',
  chartMode: 'candle',
  showIndicators: true,
  showVolume: true,
  fullscreenChart: false,
  setSelectedCoin: (symbol) => set({ selectedCoin: symbol }),
  setTimeframe: (timeframe) => set({ timeframe }),
  setChartMode: (chartMode) => set({ chartMode }),
  toggleIndicators: () =>
    set((state) => ({ showIndicators: !state.showIndicators })),
  toggleVolume: () => set((state) => ({ showVolume: !state.showVolume })),
  toggleFullscreen: () =>
    set((state) => ({ fullscreenChart: !state.fullscreenChart })),
}))

