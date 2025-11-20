import {
  Box,
  FormControlLabel,
  IconButton,
  MenuItem,
  Select,
  Switch,
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
  Typography,
} from '@mui/material'
import FullscreenIcon from '@mui/icons-material/Fullscreen'
import type { Timeframe } from '../../store/tradingStore'
import { useTradingStore } from '../../store/tradingStore'

const timeframes: Timeframe[] = ['1m', '5m', '15m', '1h', '4h', '1D']

export const TopChartToolbar = () => {
  const {
    timeframe,
    chartMode,
    showIndicators,
    showVolume,
    fullscreenChart,
    setTimeframe,
    setChartMode,
    toggleIndicators,
    toggleVolume,
    toggleFullscreen,
  } = useTradingStore()

  return (
    <Box
      sx={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: 2,
        alignItems: 'center',
        justifyContent: 'space-between',
        backgroundColor: 'rgba(255,255,255,0.04)',
        borderRadius: 3,
        px: 3,
        py: 2,
      }}
    >
      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
        <Typography variant="subtitle2" color="text.secondary">
          Timeframe
        </Typography>
        <Select
          size="small"
          value={timeframe}
          onChange={(event) => setTimeframe(event.target.value as Timeframe)}
          sx={{ minWidth: 100, backgroundColor: 'rgba(255,255,255,0.06)' }}
        >
          {timeframes.map((tf) => (
            <MenuItem key={tf} value={tf}>
              {tf}
            </MenuItem>
          ))}
        </Select>

        <ToggleButtonGroup
          size="small"
          color="primary"
          value={chartMode}
          exclusive
          onChange={(_, value) => value && setChartMode(value)}
        >
          <ToggleButton value="candle">Candle</ToggleButton>
          <ToggleButton value="line">Line</ToggleButton>
        </ToggleButtonGroup>
      </Box>

      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, alignItems: 'center' }}>
        <FormControlLabel
          control={<Switch checked={showIndicators} onChange={toggleIndicators} />}
          label="Indicators"
        />
        <FormControlLabel
          control={<Switch checked={showVolume} onChange={toggleVolume} />}
          label="Volume"
        />
        <Tooltip title={fullscreenChart ? 'Exit Fullscreen' : 'Fullscreen'}>
          <IconButton color="inherit" onClick={toggleFullscreen}>
            <FullscreenIcon color={fullscreenChart ? 'primary' : 'inherit'} />
          </IconButton>
        </Tooltip>
      </Box>
    </Box>
  )
}

export default TopChartToolbar

