import { useEffect, useMemo, useState } from 'react'
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  FormControlLabel,
  IconButton,
  InputAdornment,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Switch,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
  Typography,
  Chip,
} from '@mui/material'
import FullscreenIcon from '@mui/icons-material/Fullscreen'
import SettingsIcon from '@mui/icons-material/Settings'
import AddIcon from '@mui/icons-material/Add'
import DeleteIcon from '@mui/icons-material/Delete'
import AccessTimeIcon from '@mui/icons-material/AccessTime'
import type {
  IndicatorConfig,
  IndicatorType,
  Timeframe,
} from '../../store/tradingStore'
import { useTradingStore } from '../../store/tradingStore'

const timeframes: Timeframe[] = ['1m', '5m', '15m', '1h', '4h', '1D']

const indicatorOptions: Record<
  IndicatorType,
  { label: string; fields: Array<{ key: string; label: string; min?: number }> }
> = {
  sma: {
    label: 'Simple Moving Average',
    fields: [{ key: 'period', label: 'Period', min: 2 }],
  },
  ema: {
    label: 'Exponential Moving Average',
    fields: [{ key: 'period', label: 'Period', min: 2 }],
  },
  bollinger: {
    label: 'Bollinger Bands',
    fields: [
      { key: 'period', label: 'Period', min: 2 },
      { key: 'stdDev', label: 'Std Dev', min: 1 },
    ],
  },
  rsi: {
    label: 'RSI',
    fields: [{ key: 'period', label: 'Period', min: 2 }],
  },
}

const defaultColorMap: Record<IndicatorType, string> = {
  sma: '#4caf50',
  ema: '#ff9800',
  bollinger: '#ab47bc',
  rsi: '#29b6f6',
}

const indicatorPresets: Array<{
  id: string
  label: string
  config: IndicatorConfig
}> = [
  {
    id: 'preset-sma-20',
    label: 'SMA (20)',
    config: {
      id: 'preset-sma-20',
      name: 'SMA (20)',
      type: 'sma',
      color: defaultColorMap.sma,
      params: { period: 20 },
    },
  },
  {
    id: 'preset-ema-20',
    label: 'EMA (20)',
    config: {
      id: 'preset-ema-20',
      name: 'EMA (20)',
      type: 'ema',
      color: defaultColorMap.ema,
      params: { period: 20 },
    },
  },
  {
    id: 'preset-bbands-20',
    label: 'Bollinger Bands (20,2σ)',
    config: {
      id: 'preset-bbands-20',
      name: 'Bollinger Bands (20,2σ)',
      type: 'bollinger',
      color: defaultColorMap.bollinger,
      params: { period: 20, stdDev: 2 },
    },
  },
  {
    id: 'preset-rsi-14',
    label: 'RSI (14)',
    config: {
      id: 'preset-rsi-14',
      name: 'RSI (14)',
      type: 'rsi',
      color: defaultColorMap.rsi,
      params: { period: 14 },
    },
  },
]

interface IndicatorDialogProps {
  open: boolean
  initialConfig?: IndicatorConfig | null
  onClose: () => void
  onSave: (config: IndicatorConfig) => void
}

const IndicatorDialog = ({
  open,
  initialConfig,
  onClose,
  onSave,
}: IndicatorDialogProps) => {
  const [type, setType] = useState<IndicatorType>('sma')
  const [name, setName] = useState('')
  const [color, setColor] = useState('#4caf50')
  const [params, setParams] = useState<Record<string, number>>({ period: 20 })

  useEffect(() => {
    if (initialConfig) {
      setType(initialConfig.type)
      setName(initialConfig.name)
      setParams(initialConfig.params)
      setColor(initialConfig.color)
    } else {
      setType('sma')
      setName('')
      setParams({ period: 20 })
      setColor(defaultColorMap.sma)
    }
  }, [initialConfig, open])

  const generateId = () =>
    typeof crypto !== 'undefined' && crypto.randomUUID
      ? crypto.randomUUID()
      : `${Date.now()}-${Math.random()}`

  const handleSave = () => {
    const id = initialConfig?.id ?? generateId()
    onSave({
      id,
      name: name || `${indicatorOptions[type].label} (${params.period ?? ''})`,
      type,
      color,
      params,
    })
    onClose()
  }

  const handleParamChange = (key: string, value: number) => {
    setParams((prev) => ({ ...prev, [key]: value }))
  }

  return (
    <Dialog
      open={open}
      onClose={onClose}
      fullWidth
      maxWidth="sm"
      PaperProps={{
        sx: {
          backgroundColor: '#0d1117',
          color: '#e4e7ef',
        },
      }}
    >
      <DialogTitle>
        {initialConfig ? 'Update Indicator' : 'Add Indicator'}
      </DialogTitle>
      <DialogContent dividers sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <FormControl fullWidth size="small">
          <InputLabel id="indicator-type-label">Indicator</InputLabel>
          <Select
            labelId="indicator-type-label"
            label="Indicator"
            value={type}
            onChange={(event) => {
              const newType = event.target.value as IndicatorType
              setType(newType)
              setParams(
                indicatorOptions[newType].fields.reduce(
                  (acc, field) => {
                    acc[field.key] =
                      field.key === 'stdDev' ? 2 : field.min ?? 2
                    return acc
                  },
                  {} as Record<string, number>,
                ),
              )
              setColor(defaultColorMap[newType])
              if (!initialConfig) {
                setName('')
              }
            }}
          >
            {Object.entries(indicatorOptions).map(([key, value]) => (
              <MenuItem key={key} value={key}>
                {value.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <TextField
          size="small"
          label="Display Name"
          value={name}
          onChange={(event) => setName(event.target.value)}
        />
        <TextField
          size="small"
          label="Color"
          value={color}
          onChange={(event) => setColor(event.target.value)}
          type="color"
          InputLabelProps={{ shrink: true }}
        />
        <Stack direction="row" spacing={2}>
          {indicatorOptions[type].fields.map((field) => (
            <TextField
              key={field.key}
              size="small"
              fullWidth
              type="number"
              label={field.label}
              value={params[field.key] ?? field.min ?? 2}
              inputProps={{ min: field.min ?? 1 }}
              onChange={(event) =>
                handleParamChange(field.key, Number(event.target.value))
              }
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    {field.label === 'Std Dev' ? 'σ' : ''}
                  </InputAdornment>
                ),
              }}
            />
          ))}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} sx={{ color: '#e4e7ef' }}>
          Cancel
        </Button>
        <Button variant="contained" onClick={handleSave}>
          Save
        </Button>
      </DialogActions>
    </Dialog>
  )
}

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
    setShowSettingsDialog,
  } = useTradingStore()

  const indicatorConfigs = useTradingStore((state) => state.indicatorConfigs)
  const loadIndicatorConfigs = useTradingStore(
    (state) => state.loadIndicatorConfigs,
  )
  const addIndicatorConfig = useTradingStore(
    (state) => state.addIndicatorConfig,
  )
  const updateIndicatorConfig = useTradingStore(
    (state) => state.updateIndicatorConfig,
  )
  const removeIndicatorConfig = useTradingStore(
    (state) => state.removeIndicatorConfig,
  )

  const [indicatorDialogOpen, setIndicatorDialogOpen] = useState(false)
  const [editingConfig, setEditingConfig] = useState<IndicatorConfig | null>(
    null,
  )

  useEffect(() => {
    loadIndicatorConfigs()
  }, [loadIndicatorConfigs])

  const handleSaveIndicator = (config: IndicatorConfig) => {
    const exists = indicatorConfigs.some((item) => item.id === config.id)
    if (exists) {
      updateIndicatorConfig(config)
    } else {
      addIndicatorConfig(config)
    }
  }

  const displayConfigs = useMemo(() => {
    const clone = [...indicatorConfigs]
    return clone.sort((a, b) =>
      a.name.localeCompare(b.name, undefined, { sensitivity: 'base' }),
    )
  }, [indicatorConfigs])

  const handlePresetToggle = (
    preset: (typeof indicatorPresets)[number],
    enabled: boolean,
  ) => {
    const exists = indicatorConfigs.some((config) => config.id === preset.id)
    if (enabled && !exists) {
      addIndicatorConfig(preset.config)
    }
    if (!enabled && exists) {
      removeIndicatorConfig(preset.id)
    }
  }

  return (
    <>
      <Box
        sx={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: 0.5,
          alignItems: 'center',
          justifyContent: 'space-between',
          backgroundColor: 'rgba(255,255,255,0.04)',
          borderRadius: 3,
          border: '3px solid rgba(255,255,255,0.08)',
          px: 0,
          py: 0,
          height: 35,
          minHeight: 35,
          maxHeight: 35,
        }}
      >
        <Box sx={{ display: 'flex', gap: 0.75, flexWrap: 'wrap', alignItems: 'center', px: 1, py: 0 }}>
          <Box sx={{ display: { xs: 'none', sm: 'flex' }, alignItems: 'center', gap: 0.5 }}>
            <AccessTimeIcon fontSize="small" sx={{ color: 'text.secondary', fontSize: 14 }} />
            <Typography 
              variant="subtitle2" 
              color="text.secondary"
              sx={{ fontSize: '0.7rem' }}
            >
              TF
            </Typography>
          </Box>
          <ToggleButtonGroup
            size="small"
            color="primary"
            value={timeframe}
            exclusive
            onChange={(_, value) => value && setTimeframe(value)}
            sx={{
              '& .MuiToggleButton-root': {
                border: '3px solid',
                borderColor: 'rgba(255,255,255,0.12)',
                fontWeight: 'bold',
                px: 0.75,
                py: 0.25,
                fontSize: '0.7rem',
                minWidth: 32,
                height: 24,
                '&.Mui-selected': {
                  borderColor: 'primary.main',
                  borderWidth: '3px',
                  backgroundColor: 'rgba(25,118,210,0.2)',
                },
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.08)',
                },
              },
            }}
          >
            {timeframes.map((tf) => (
              <ToggleButton key={tf} value={tf}>
                {tf}
              </ToggleButton>
            ))}
          </ToggleButtonGroup>

          <ToggleButtonGroup
            size="small"
            color="primary"
            value={chartMode}
            exclusive
            onChange={(_, value) => value && setChartMode(value)}
            sx={{
              '& .MuiToggleButton-root': {
                fontSize: '0.7rem',
                px: 0.75,
                py: 0.25,
                height: 24,
              },
            }}
          >
            <ToggleButton value="candle">Candle</ToggleButton>
            <ToggleButton value="line">Line</ToggleButton>
          </ToggleButtonGroup>
        </Box>

        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.75, alignItems: 'center', px: 1, py: 0 }}>
          <FormControlLabel
            control={<Switch checked={showIndicators} onChange={toggleIndicators} size="small" />}
            label={
              <Typography sx={{ fontSize: '0.7rem' }}>
                Indicators
              </Typography>
            }
            sx={{ margin: 0 }}
          />
          <FormControlLabel
            control={<Switch checked={showVolume} onChange={toggleVolume} size="small" />}
            label={
              <Typography sx={{ fontSize: '0.7rem' }}>
                Volume
              </Typography>
            }
            sx={{ display: { xs: 'none', sm: 'flex' }, margin: 0 }}
          />
          <Tooltip title="Chart Settings">
            <IconButton 
              color="inherit" 
              onClick={() => setShowSettingsDialog(true)}
              size="small"
              sx={{ padding: 0.25 }}
            >
              <SettingsIcon sx={{ fontSize: 16 }} />
            </IconButton>
          </Tooltip>
          <Tooltip title={fullscreenChart ? 'Exit Fullscreen' : 'Fullscreen'}>
            <IconButton 
              color="inherit" 
              onClick={toggleFullscreen}
              size="small"
              sx={{ padding: 0.25 }}
            >
              <FullscreenIcon 
                color={fullscreenChart ? 'primary' : 'inherit'} 
                sx={{ fontSize: 16 }}
              />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Indicator Management Section */}
      <Box
        sx={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: 0.5,
          alignItems: 'center',
          backgroundColor: 'rgba(255,255,255,0.02)',
          borderRadius: 3,
          border: '3px solid rgba(255,255,255,0.08)',
          px: 0,
          py: 0,
          mt: 1,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75, flex: 1, flexWrap: 'wrap', px: 1, py: 0.75 }}>
          <Typography 
            variant="subtitle2" 
            color="text.secondary" 
            sx={{ 
              minWidth: 60,
              fontSize: '0.7rem',
            }}
          >
            Indicators:
          </Typography>
          <Stack direction="row" flexWrap="wrap" spacing={0.5} useFlexGap sx={{ flex: 1 }}>
            {indicatorPresets.map((preset) => {
              const active = indicatorConfigs.some(
                (config) => config.id === preset.id,
              )
              return (
                <FormControlLabel
                  key={preset.id}
                  control={
                    <Switch
                      size="small"
                      checked={active}
                      onChange={(event) =>
                        handlePresetToggle(preset, event.target.checked)
                      }
                    />
                  }
                  label={preset.label}
                />
              )
            })}
          </Stack>
        </Box>
        <Button
          startIcon={<AddIcon />}
          variant="outlined"
          size="small"
          onClick={() => {
            setEditingConfig(null)
            setIndicatorDialogOpen(true)
          }}
        >
          Add Custom
        </Button>
      </Box>

      {/* Active Indicators Display */}
      {displayConfigs.length > 0 && (
        <Box
          sx={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: 1,
            alignItems: 'center',
            backgroundColor: 'rgba(255,255,255,0.02)',
            borderRadius: 3,
            px: 3,
            py: 1.5,
            mt: 1,
          }}
        >
          <Typography variant="caption" color="text.secondary" sx={{ minWidth: 80 }}>
            Active:
          </Typography>
          <Stack direction="row" flexWrap="wrap" spacing={1} useFlexGap>
            {displayConfigs.map((config) => (
              <Chip
                key={config.id}
                label={config.name}
                size="small"
                sx={{
                  backgroundColor: 'rgba(255,255,255,0.08)',
                  border: `1px solid ${config.color}`,
                  '& .MuiChip-label': {
                    color: '#e4e7ef',
                  },
                }}
                icon={
                  <Box
                    sx={{
                      width: 10,
                      height: 10,
                      borderRadius: '50%',
                      backgroundColor: config.color,
                    }}
                  />
                }
                onDelete={() => removeIndicatorConfig(config.id)}
                deleteIcon={
                  <IconButton
                    size="small"
                    onClick={() => removeIndicatorConfig(config.id)}
                    sx={{ color: '#e4e7ef' }}
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                }
                onClick={() => {
                  setEditingConfig(config)
                  setIndicatorDialogOpen(true)
                }}
              />
            ))}
          </Stack>
        </Box>
      )}

      <IndicatorDialog
        open={indicatorDialogOpen}
        initialConfig={editingConfig}
        onClose={() => {
          setIndicatorDialogOpen(false)
          setEditingConfig(null)
        }}
        onSave={handleSaveIndicator}
      />
    </>
  )
}

export default TopChartToolbar
