import { Box } from '@mui/material'
import { MainTradingLayout } from '../components/tradingLayout/MainTradingLayout'

export const TradingPage = () => {
  return (
    <Box
      sx={{
        width: '100%',
        height: 'calc(100vh - 120px)',
        px: { xs: 1, sm: 2, md: 3 },
        py: { xs: 1, md: 2 },
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}
    >
      <MainTradingLayout />
    </Box>
  )
}

export default TradingPage

