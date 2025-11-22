import { create } from 'zustand'

interface TradingLayoutState {
  leftWidth: number // percentage (0-100)
  topHeight: number // percentage (0-100)
  setLeftWidth: (width: number) => void
  setTopHeight: (height: number) => void
  initFromStorage: () => void
}

const STORAGE_KEYS = {
  LEFT_WIDTH: 'tradingLayout.leftWidth',
  TOP_HEIGHT: 'tradingLayout.topHeight',
}

const DEFAULT_LEFT_WIDTH = 75 // 75% left, 25% right
const DEFAULT_TOP_HEIGHT = 70 // 70% top, 30% bottom

export const useTradingLayoutStore = create<TradingLayoutState>((set, get) => ({
  leftWidth: DEFAULT_LEFT_WIDTH,
  topHeight: DEFAULT_TOP_HEIGHT,

  setLeftWidth: (width: number) => {
    const clamped = Math.max(30, Math.min(95, width))
    set({ leftWidth: clamped })
    sessionStorage.setItem(STORAGE_KEYS.LEFT_WIDTH, clamped.toString())
  },

  setTopHeight: (height: number) => {
    const clamped = Math.max(30, Math.min(90, height))
    set({ topHeight: clamped })
    sessionStorage.setItem(STORAGE_KEYS.TOP_HEIGHT, clamped.toString())
  },

  initFromStorage: () => {
    if (typeof window === 'undefined') return

    const savedLeftWidth = sessionStorage.getItem(STORAGE_KEYS.LEFT_WIDTH)
    const savedTopHeight = sessionStorage.getItem(STORAGE_KEYS.TOP_HEIGHT)

    if (savedLeftWidth) {
      const width = parseFloat(savedLeftWidth)
      if (!isNaN(width) && width >= 30 && width <= 95) {
        set({ leftWidth: width })
      }
    }

    if (savedTopHeight) {
      const height = parseFloat(savedTopHeight)
      if (!isNaN(height) && height >= 30 && height <= 90) {
        set({ topHeight: height })
      }
    }
  },
}))

