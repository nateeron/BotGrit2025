import { useEffect, useMemo, useState } from 'react'
import {
  Box,
  Button,
  Card,
  CardContent,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  IconButton,
  InputAdornment,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material'
import SettingsIcon from '@mui/icons-material/Settings'
import DeleteIcon from '@mui/icons-material/Delete'
import AddIcon from '@mui/icons-material/Add'
import type { IndicatorConfig, IndicatorType } from '../../store/tradingStore'
import { useTradingStore } from '../../store/tradingStore'

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

interface IndicatorDialogProps {
  open: boolean
  initialConfig?: IndicatorConfig | null
  onClose: () => void
  onSave: (config: IndicatorConfig) => void
}

const defaultColorMap: Record<IndicatorType, string> = {
  sma: '#4caf50',
  ema: '#ff9800',
  bollinger: '#ab47bc',
  rsi: '#29b6f6',
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
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
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
                      field.key === 'stdDev'
                        ? 2
                        : field.min ?? 2
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
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" onClick={handleSave}>
          Save
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export const IndicatorManager = () => {
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

  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingConfig, setEditingConfig] = useState<IndicatorConfig | null>(
    null,
  )

  useEffect(() => {
    loadIndicatorConfigs()
  }, [loadIndicatorConfigs])

  const handleSave = (config: IndicatorConfig) => {
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

  return (
    <>
      <Card sx={{ p: 0, borderRadius: 2 }}>
        <CardContent sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Indicator Manager</Typography>
            <Button
              startIcon={<AddIcon />}
              variant="contained"
              onClick={() => {
                setEditingConfig(null)
                setDialogOpen(true)
              }}
            >
              Add Indicator
            </Button>
          </Box>
          {displayConfigs.length === 0 && (
            <Typography variant="body2" color="text.secondary">
              No custom indicators yet. Click &quot;Add Indicator&quot; to begin.
            </Typography>
          )}
          {displayConfigs.length > 0 && (
            <Stack direction="row" flexWrap="wrap" spacing={1} useFlexGap>
              {displayConfigs.map((config) => (
                <Box
                  key={config.id}
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: 2,
                    px: 2,
                    py: 1,
                    gap: 1,
                  }}
                >
                  <Box
                    sx={{
                      width: 12,
                      height: 12,
                      borderRadius: '50%',
                      backgroundColor: config.color,
                    }}
                  />
                  <Typography variant="body2">{config.name}</Typography>
                  <Tooltip title="Edit settings">
                    <IconButton
                      size="small"
                      onClick={() => {
                        setEditingConfig(config)
                        setDialogOpen(true)
                      }}
                    >
                      <SettingsIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Remove indicator">
                    <IconButton
                      size="small"
                      onClick={() => removeIndicatorConfig(config.id)}
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
              ))}
            </Stack>
          )}
        </CardContent>
      </Card>
      <IndicatorDialog
        open={dialogOpen}
        initialConfig={editingConfig}
        onClose={() => setDialogOpen(false)}
        onSave={handleSave}
      />
    </>
  )
}

export default IndicatorManager

