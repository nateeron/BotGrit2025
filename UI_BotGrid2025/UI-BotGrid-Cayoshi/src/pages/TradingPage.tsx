import { Box, Grid, Typography } from '@mui/material'
import TopChartToolbar from '../components/layout/TopChartToolbar'
import PriceChart from '../components/trading/PriceChart'
import CoinListSidebar from '../components/layout/CoinListSidebar'
import CardBotSetting from '../components/trading/CardBotSetting'
import CardOrderList from '../components/trading/CardOrderList'
import CardReport from '../components/trading/CardReport'

export const TradingPage = () => {
  return (
    <Box sx={{ width: '100%', px: { xs: 2, md: 3 }, py: 3 }}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        Trading Dashboard
      </Typography>
      <Grid container spacing={3}>
        <Grid size={12}>
          <TopChartToolbar />
        </Grid>

        <Grid size={{ xs: 12, lg: 8 }}>
          <PriceChart />
        </Grid>
        <Grid size={{ xs: 12, lg: 4 }}>
          <CoinListSidebar />
        </Grid>

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

