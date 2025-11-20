import { useState } from 'react'
import {
  Box,
  Button,
  Card,
  CardContent,
  Divider,
  FormControl,
  InputAdornment,
  MenuItem,
  Select,
  TextField,
  Typography,
} from '@mui/material'

const strategies = ['Grid', 'DCA', 'Scalping']

export const CardBotSetting = () => {
  const [strategy, setStrategy] = useState('Grid')
  const [tp, setTp] = useState('5')
  const [sl, setSl] = useState('2')
  const [gridDistance, setGridDistance] = useState('0.8')
  const [running, setRunning] = useState(false)

  return (
    <Card sx={{ p: 2, borderRadius: 2, height: '100%' }}>
      <CardContent sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Bot Setting</Typography>
          <Typography variant="caption" color={running ? 'success.main' : 'text.secondary'}>
            {running ? 'Running' : 'Idle'}
          </Typography>
        </Box>
        <FormControl size="small" fullWidth>
          <Typography variant="caption" color="text.secondary">
            Strategy
          </Typography>
          <Select value={strategy} onChange={(event) => setStrategy(event.target.value)}>
            {strategies.map((name) => (
              <MenuItem key={name} value={name}>
                {name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 1.5 }}>
          <TextField
            size="small"
            label="Take Profit"
            value={tp}
            onChange={(event) => setTp(event.target.value)}
            InputProps={{
              endAdornment: <InputAdornment position="end">%</InputAdornment>,
            }}
          />
          <TextField
            size="small"
            label="Stop Loss"
            value={sl}
            onChange={(event) => setSl(event.target.value)}
            InputProps={{
              endAdornment: <InputAdornment position="end">%</InputAdornment>,
            }}
          />
          <TextField
            size="small"
            label="Grid Distance"
            value={gridDistance}
            onChange={(event) => setGridDistance(event.target.value)}
            InputProps={{
              endAdornment: <InputAdornment position="end">%</InputAdornment>,
            }}
          />
          <TextField
            size="small"
            label="Budget"
            value="10,000"
            InputProps={{
              startAdornment: <InputAdornment position="start">$</InputAdornment>,
            }}
          />
        </Box>

        <Divider flexItem />

        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            fullWidth
            variant="contained"
            color={running ? 'warning' : 'primary'}
            onClick={() => setRunning(!running)}
          >
            {running ? 'Pause' : 'Start'}
          </Button>
          <Button
            fullWidth
            variant="outlined"
            color="error"
            disabled={!running}
            onClick={() => setRunning(false)}
          >
            Stop
          </Button>
        </Box>
      </CardContent>
    </Card>
  )
}

export default CardBotSetting

