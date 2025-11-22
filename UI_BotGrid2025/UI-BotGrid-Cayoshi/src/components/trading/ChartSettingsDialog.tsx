import { useState } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Switch,
  Box,
  Typography,
  Divider,
} from '@mui/material'
import { useTradingStore } from '../../store/tradingStore'

export const ChartSettingsDialog = () => {
  const {
    showSettingsDialog,
    setShowSettingsDialog,
    chartMode,
    setChartMode,
    showIndicators,
    toggleIndicators,
    showVolume,
    toggleVolume,
  } = useTradingStore()

  return (
    <Dialog
      open={showSettingsDialog}
      onClose={() => setShowSettingsDialog(false)}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          backgroundColor: '#0d1117',
          color: '#e4e7ef',
        },
      }}
    >
      <DialogTitle>Chart Settings</DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          <FormControl>
            <FormLabel sx={{ color: '#e4e7ef', mb: 1 }}>Chart Mode</FormLabel>
            <RadioGroup
              value={chartMode}
              onChange={(e) => setChartMode(e.target.value as 'candle' | 'line')}
            >
              <FormControlLabel
                value="candle"
                control={<Radio sx={{ color: '#e4e7ef' }} />}
                label="Candlestick"
                sx={{ color: '#e4e7ef' }}
              />
              <FormControlLabel
                value="line"
                control={<Radio sx={{ color: '#e4e7ef' }} />}
                label="Line"
                sx={{ color: '#e4e7ef' }}
              />
            </RadioGroup>
          </FormControl>

          <Divider sx={{ borderColor: 'rgba(255,255,255,0.08)' }} />

          <Box>
            <FormLabel sx={{ color: '#e4e7ef', mb: 1, display: 'block' }}>
              Display Options
            </FormLabel>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <Typography variant="body2" sx={{ color: '#e4e7ef' }}>
                  Show Indicators
                </Typography>
                <Switch
                  checked={showIndicators}
                  onChange={toggleIndicators}
                  sx={{
                    '& .MuiSwitch-switchBase.Mui-checked': {
                      color: '#1976d2',
                    },
                    '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                      backgroundColor: '#1976d2',
                    },
                  }}
                />
              </Box>
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <Typography variant="body2" sx={{ color: '#e4e7ef' }}>
                  Show Volume
                </Typography>
                <Switch
                  checked={showVolume}
                  onChange={toggleVolume}
                  sx={{
                    '& .MuiSwitch-switchBase.Mui-checked': {
                      color: '#1976d2',
                    },
                    '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                      backgroundColor: '#1976d2',
                    },
                  }}
                />
              </Box>
            </Box>
          </Box>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button
          onClick={() => setShowSettingsDialog(false)}
          sx={{ color: '#e4e7ef' }}
        >
          Close
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default ChartSettingsDialog

