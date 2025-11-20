import { useMemo, useState } from 'react'
import {
  AppBar,
  Box,
  CssBaseline,
  Tab,
  Tabs,
  ThemeProvider,
  Toolbar,
  Typography,
  createTheme,
} from '@mui/material'
import TradingPage from './pages/TradingPage'
import ReportPage from './pages/ReportPage'
import LeftMenuMini from './components/layout/LeftMenuMini'

const App = () => {
  const [activeTab, setActiveTab] = useState<'trading' | 'report'>('trading')

  const darkTheme = useMemo(
    () =>
      createTheme({
        palette: {
          mode: 'dark',
          background: {
            default: '#0d1117',
            paper: '#111826',
          },
        },
        shape: {
          borderRadius: 12,
        },
        typography: {
          fontFamily: 'Inter, "Prompt", "Noto Sans Thai", sans-serif',
        },
        components: {
          MuiCard: {
            styleOverrides: {
              root: {
                backgroundColor: '#111826',
                border: '1px solid rgba(255,255,255,0.05)',
                boxShadow: '0 10px 30px rgba(0,0,0,0.3)',
              },
            },
          },
          MuiButton: {
            defaultProps: {
              disableElevation: true,
            },
            styleOverrides: {
              root: {
                borderRadius: 12,
              },
            },
          },
        },
      }),
    [],
  )

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', minHeight: '100vh', backgroundColor: '#0d1117' }}>
        <LeftMenuMini />
        <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
          <AppBar
            position="sticky"
            elevation={0}
            sx={{
              background: 'rgba(13,17,23,0.85)',
              backdropFilter: 'blur(12px)',
              borderBottom: '1px solid rgba(255,255,255,0.08)',
            }}
          >
            <Toolbar sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Box>
                <Typography variant="h6" fontWeight={600}>
                  BotGrid Pro
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  React + MUI Trading Workbench
                </Typography>
              </Box>
              <Tabs
                value={activeTab}
                onChange={(_, value) => setActiveTab(value)}
                textColor="inherit"
                indicatorColor="primary"
              >
                <Tab label="Trading" value="trading" />
                <Tab label="Report" value="report" />
              </Tabs>
            </Toolbar>
          </AppBar>

          <Box component="main" sx={{ flexGrow: 1 }}>
            {activeTab === 'trading' ? <TradingPage /> : <ReportPage />}
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  )
}

export default App
