import { Box, Grid, Typography, IconButton, Tooltip } from '@mui/material'
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft'
import ChevronRightIcon from '@mui/icons-material/ChevronRight'
import TopChartToolbar from '../components/layout/TopChartToolbar'
import PriceChart from '../components/trading/PriceChart'
import CoinListSidebar from '../components/layout/CoinListSidebar'
import CardBotSetting from '../components/trading/CardBotSetting'
import CardOrderList from '../components/trading/CardOrderList'
import CardReport from '../components/trading/CardReport'
import { useTradingStore } from '../store/tradingStore'

export const TradingPage = () => {
  const sidebarCollapsed = useTradingStore((state) => state.sidebarCollapsed)
  const toggleSidebar = useTradingStore((state) => state.toggleSidebar)

  return (
    <Box sx={{ width: '100%', px: { xs: 1, sm: 2, md: 3 }, py: { xs: 2, md: 3 } }}>
      <Grid container spacing={{ xs: 2, md: 3 }}>
        <Grid size={12}>
          <TopChartToolbar />
        </Grid>

        <Grid size={{ xs: 12, lg: sidebarCollapsed ? 12 : 8 }}>
          <Box sx={{ position: 'relative' }}>
            <PriceChart />
            {sidebarCollapsed && (
              <Tooltip title="Show Symbol List">
                <IconButton
                  onClick={toggleSidebar}
                  size="small"
                  sx={{
                    position: 'absolute',
                    top: { xs: 8, md: 16 },
                    right: { xs: 8, md: 16 },
                    zIndex: 20,
                    backgroundColor: 'rgba(255,255,255,0.08)',
                    color: '#e4e7ef',
                    '&:hover': {
                      backgroundColor: 'rgba(255,255,255,0.12)',
                    },
                  }}
                >
                  <ChevronLeftIcon sx={{ fontSize: { xs: 20, md: 24 } }} />
                </IconButton>
              </Tooltip>
            )}
          </Box>
        </Grid>
        {!sidebarCollapsed && (
          <Grid size={{ xs: 12, lg: 4 }}>
            <Box sx={{ maxWidth: 250, width: '100%' }}>
              <CoinListSidebar />
            </Box>
          </Grid>
        )}

        <Grid size={{ xs: 12, md: 4 }}>
          <CardBotSetting />
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <CardOrderList />
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <CardReport />
        </Grid>
      </Grid>
    </Box>
  )
}

export default TradingPage

