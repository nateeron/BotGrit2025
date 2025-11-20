import { Box, Grid, Typography } from '@mui/material'
import CardReport from '../components/trading/CardReport'
import CardOrderList from '../components/trading/CardOrderList'

export const ReportPage = () => (
  <Box sx={{ width: '100%', px: { xs: 2, md: 3 }, py: 3 }}>
    <Typography variant="h4" sx={{ mb: 3 }}>
      Performance Report
    </Typography>
    <Grid container spacing={3}>
      <Grid size={{ xs: 12, md: 6 }}>
        <CardReport />
      </Grid>
      <Grid size={{ xs: 12, md: 6 }}>
        <CardOrderList />
      </Grid>
    </Grid>
  </Box>
)

export default ReportPage

