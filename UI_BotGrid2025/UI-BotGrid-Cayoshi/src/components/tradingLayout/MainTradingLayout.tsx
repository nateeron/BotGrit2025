import { useEffect, useRef } from 'react'
import { Box } from '@mui/material'
import { useTradingLayoutStore } from './useTradingLayoutStore'
import { Splitter } from './Splitter'
import PriceChart from '../trading/PriceChart'
import { RSIChart } from '../trading/RSIChart'
import CoinListSidebar from '../layout/CoinListSidebar'
import TopChartToolbar from '../layout/TopChartToolbar'
import { Box as MuiBox } from '@mui/material'
import './tradingLayout.css'

export const MainTradingLayout = () => {
  const containerRef = useRef<HTMLDivElement>(null)
  const { leftWidth, topHeight, setLeftWidth, setTopHeight, initFromStorage } =
    useTradingLayoutStore()

  // Initialize from sessionStorage on mount
  useEffect(() => {
    initFromStorage()
  }, [initFromStorage])

  // Handle horizontal resize (left/right)
  const handleHorizontalResize = (delta: number) => {
    if (!containerRef.current) return
    const containerWidth = containerRef.current.offsetWidth
    const deltaPercent = (delta / containerWidth) * 100
    const newLeftWidth = leftWidth + deltaPercent
    setLeftWidth(newLeftWidth)
  }

  // Handle vertical resize (top/bottom)
  const handleVerticalResize = (delta: number) => {
    if (!containerRef.current) return
    const leftPanel = containerRef.current.querySelector(
      '.trading-layout-left',
    ) as HTMLElement
    if (!leftPanel) return
    const containerHeight = leftPanel.offsetHeight
    const deltaPercent = (delta / containerHeight) * 100
    const newTopHeight = topHeight + deltaPercent
    setTopHeight(newTopHeight)
  }

  return (
    <MuiBox
      sx={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <MuiBox sx={{ mb: 1, flexShrink: 0 }}>
        <TopChartToolbar />
      </MuiBox>
      <Box
        ref={containerRef}
        className="trading-layout-container"
        sx={{
          width: '100%',
          flexGrow: 1,
          minHeight: 0,
          display: 'flex',
          position: 'relative',
          overflow: 'hidden',
          backgroundColor: '#0d1117',
        }}
      >
      {/* Left Panel */}
      <Box
        className="trading-layout-left"
        sx={{
          width: `${leftWidth}%`,
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
          overflow: 'hidden',
          borderRight: '1px solid rgba(255,255,255,0.08)',
        }}
      >
        {/* Top: Price Chart */}
        <Box
          className="trading-layout-top"
          sx={{
            height: `${topHeight}%`,
            width: '100%',
            position: 'relative',
            overflow: 'hidden',
            flexShrink: 0,
            borderBottom: '1px solid rgba(255,255,255,0.08)',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <PriceChart />
        </Box>

        {/* Horizontal Splitter */}
        <Splitter direction="horizontal" onResize={handleVerticalResize} />

        {/* Bottom: RSI/Indicators */}
        <Box
          className="trading-layout-bottom"
          sx={{
            height: `${100 - topHeight}%`,
            width: '100%',
            position: 'relative',
            overflow: 'hidden',
            flexShrink: 0,
          }}
        >
          <RSIChart />
        </Box>
      </Box>

      {/* Vertical Splitter */}
      <Splitter direction="vertical" onResize={handleHorizontalResize} />

      {/* Right Panel: Coin List */}
      <Box
        className="trading-layout-right"
        sx={{
          width: `${100 - leftWidth}%`,
          maxWidth: '300px',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
          overflow: 'hidden',
          flexShrink: 0,
        }}
      >
        <CoinListSidebar />
      </Box>
      </Box>
    </MuiBox>
  )
}

