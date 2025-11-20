import { useEffect, useMemo, useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  Tab,
  Tabs,
  Typography,
} from '@mui/material'
import type { ReportSummary } from '../../services/api'
import { getDailyReport } from '../../services/api'

type RangeKey = 'daily' | 'monthly' | 'yearly'

const tabConfig: Record<RangeKey, string> = {
  daily: 'Daily',
  monthly: 'Monthly',
  yearly: 'Yearly',
}

export const CardReport = () => {
  const [activeTab, setActiveTab] = useState<RangeKey>('daily')
  const [data, setData] = useState<Record<RangeKey, ReportSummary[]>>({
    daily: [],
    monthly: [],
    yearly: [],
  })

  useEffect(() => {
    const fetchReport = async () => {
      const report = await getDailyReport()
      setData((prev) => ({
        ...prev,
        [activeTab]: report.map((entry) => ({
          ...entry,
          profit:
            activeTab === 'monthly'
              ? entry.profit * 2
              : activeTab === 'yearly'
                ? entry.profit * 6
                : entry.profit,
        })),
      }))
    }
    if (data[activeTab].length === 0) {
      fetchReport()
    }
  }, [activeTab, data])

  const activeData = data[activeTab]

  const { totals, maxProfit } = useMemo(() => {
    if (activeData.length === 0) {
      return {
        totals: { profit: 0, orders: 0, winRate: 0 },
        maxProfit: 1,
      }
    }
    const profit = activeData.reduce((sum, item) => sum + item.profit, 0)
    const orders = activeData.reduce((sum, item) => sum + item.orders, 0)
    const winRate = activeData.reduce((sum, item) => sum + item.winRate, 0) / activeData.length
    const maxProfit = Math.max(...activeData.map((item) => item.profit))
    return {
      totals: { profit, orders, winRate },
      maxProfit,
    }
  }, [activeData])

  return (
    <Card sx={{ p: 2, borderRadius: 2, height: '100%' }}>
      <CardContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, height: '100%' }}>
        <Typography variant="h6">Performance</Typography>
        <Tabs
          value={activeTab}
          onChange={(_, value) => setActiveTab(value)}
          variant="fullWidth"
          textColor="inherit"
        >
          {Object.entries(tabConfig).map(([value, label]) => (
            <Tab key={value} value={value} label={label} />
          ))}
        </Tabs>

        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: 1.5,
            textAlign: 'center',
          }}
        >
          <Box>
            <Typography variant="caption" color="text.secondary">
              Total Profit
            </Typography>
            <Typography variant="h6">${totals.profit.toLocaleString()}</Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary">
              Orders
            </Typography>
            <Typography variant="h6">{totals.orders}</Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary">
              Win Rate
            </Typography>
            <Typography variant="h6">{totals.winRate.toFixed(1)}%</Typography>
          </Box>
        </Box>

        <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'flex-end', gap: 1, minHeight: 140 }}>
          {activeData.map((item) => {
            const height = Math.max(10, (item.profit / maxProfit) * 100)
            return (
              <Box key={item.label} sx={{ flex: 1, textAlign: 'center' }}>
                <Box
                  sx={{
                    height: `${height}%`,
                    background: 'linear-gradient(180deg,#43a047,#1b5e20)',
                    borderRadius: 1,
                  }}
                />
                <Typography variant="caption" color="text.secondary">
                  {item.label}
                </Typography>
              </Box>
            )
          })}
        </Box>
      </CardContent>
    </Card>
  )
}

export default CardReport

