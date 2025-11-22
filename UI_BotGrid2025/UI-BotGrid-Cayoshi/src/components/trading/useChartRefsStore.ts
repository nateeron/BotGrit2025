import { create } from 'zustand'
import type { IChartApi } from 'lightweight-charts'

interface ChartRefsState {
  mainChartRef: IChartApi | null
  rsiChartRef: IChartApi | null
  mainMousePos: { x: number; y: number } | null
  rsiMousePos: { x: number; y: number } | null
  setMainChartRef: (chart: IChartApi | null) => void
  setRsiChartRef: (chart: IChartApi | null) => void
  setMainMousePos: (pos: { x: number; y: number } | null) => void
  setRsiMousePos: (pos: { x: number; y: number } | null) => void
}

export const useChartRefsStore = create<ChartRefsState>((set) => ({
  mainChartRef: null,
  rsiChartRef: null,
  mainMousePos: null,
  rsiMousePos: null,
  setMainChartRef: (chart) => set({ mainChartRef: chart }),
  setRsiChartRef: (chart) => set({ rsiChartRef: chart }),
  setMainMousePos: (pos) => set({ mainMousePos: pos }),
  setRsiMousePos: (pos) => set({ rsiMousePos: pos }),
}))

