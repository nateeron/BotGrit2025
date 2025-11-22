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
          borderRadius: 3,
        },
        typography: {
          fontFamily: 'Inter, "Prompt", "Noto Sans Thai", sans-serif',
        },
        components: {
          MuiCard: {
            styleOverrides: {
              root: {
                backgroundColor: '#111826',
                border: '3px solid rgba(255,255,255,0.08)',
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
                borderRadius: 3,
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
        <Box sx={{ display: { xs: 'none', md: 'block' } }}>
          <LeftMenuMini />
        </Box>
        <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', width: { xs: '100%', md: 'auto' } }}>
          <AppBar
            position="sticky"
            elevation={0}
            sx={{
              background: 'rgba(13,17,23,0.85)',
              backdropFilter: 'blur(12px)',
              borderBottom: '1px solid rgba(255,255,255,0.08)',
            }}
          >
            <Toolbar 
              sx={{ 
                display: 'flex', 
                justifyContent: 'space-between',
                flexWrap: { xs: 'wrap', sm: 'nowrap' },
                gap: { xs: 1, sm: 0 },
                minHeight: { xs: 64, sm: 64 },
                py: { xs: 1, sm: 0 },
              }}
            >
              <Box sx={{ flexShrink: 0 }}>
                <Typography 
                  variant="h6" 
                  fontWeight={600}
                  sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }}
                >
                  BotGrid Pro
                </Typography>
                <Typography 
                  variant="caption" 
                  color="text.secondary"
                  sx={{ display: { xs: 'none', sm: 'block' } }}
                >
                  React + MUI Trading Workbench
                </Typography>
              </Box>
              <Tabs
                value={activeTab}
                onChange={(_, value) => setActiveTab(value)}
                textColor="inherit"
                indicatorColor="primary"
                sx={{ 
                  minHeight: { xs: 40, sm: 48 },
                  '& .MuiTab-root': {
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    minWidth: { xs: 60, sm: 72 },
                    padding: { xs: '8px 12px', sm: '12px 16px' },
                  },
                }}
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
