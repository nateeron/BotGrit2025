import { create } from 'zustand'
import type { OhlcPoint } from '../../services/api'

interface ChartDataState {
  chartData: OhlcPoint[]
  setChartData: (data: OhlcPoint[]) => void
}

export const useChartDataStore = create<ChartDataState>((set) => ({
  chartData: [],
  setChartData: (data: OhlcPoint[]) => set({ chartData: data }),
}))

