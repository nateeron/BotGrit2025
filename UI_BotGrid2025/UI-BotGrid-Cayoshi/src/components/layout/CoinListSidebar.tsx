import { useEffect, useMemo, useState } from 'react'
import {
  Avatar,
  Box,
  CircularProgress,
  Divider,
  IconButton,
  InputAdornment,
  List,
  ListItemButton,
  ListItemText,
  TextField,
  Typography,
  Tooltip,
} from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'
import RefreshIcon from '@mui/icons-material/Refresh'
import ChevronRightIcon from '@mui/icons-material/ChevronRight'
import type { CoinSummary } from '../../services/api'
import { getCoins } from '../../services/api'
import { useTradingStore } from '../../store/tradingStore'

const getAvatarChar = (symbol: string) => symbol.slice(0, 2).toUpperCase()

export const CoinListSidebar = () => {
  const [coins, setCoins] = useState<CoinSummary[]>([])
  const [loading, setLoading] = useState(false)
  const [query, setQuery] = useState('')
  const selectedCoin = useTradingStore((state) => state.selectedCoin)
  const setSelectedCoin = useTradingStore((state) => state.setSelectedCoin)
  const toggleSidebar = useTradingStore((state) => state.toggleSidebar)

  const fetchCoins = async () => {
    setLoading(true)
    const data = await getCoins()
    setCoins(data)
    setLoading(false)
  }

  useEffect(() => {
    fetchCoins()
  }, [])

  const filteredCoins = useMemo(() => {
    const lower = query.toLowerCase()
    return coins.filter(
      (coin) =>
        coin.symbol.toLowerCase().includes(lower) ||
        coin.name.toLowerCase().includes(lower),
    )
  }, [coins, query])

  return (
    <Box
      sx={{
        height: '100%',
        width: '100%',
        maxWidth: 250,
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: 'rgba(255,255,255,0.02)',
        borderRadius: 3,
        border: '3px solid rgba(255,255,255,0.08)',
        p: 1,
      }}
    >
      <Box sx={{ display: 'flex', gap: 0.75, alignItems: 'center', mb: 1 }}>
        <TextField
          fullWidth
          size="small"
          placeholder="Search coin..."
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            ),
          }}
        />
        <IconButton onClick={fetchCoins} disabled={loading}>
          <RefreshIcon fontSize="small" />
        </IconButton>
        <Tooltip title="Hide Symbol List">
          <IconButton onClick={toggleSidebar} size="small">
            <ChevronRightIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>

      {loading && (
        <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <CircularProgress size={28} />
        </Box>
      )}

      {!loading && (
        <List sx={{ flexGrow: 1, overflowY: 'auto' }}>
          {filteredCoins.map((coin) => {
            const isSelected = coin.symbol === selectedCoin
            return (
              <ListItemButton
                key={coin.symbol}
                onClick={() => setSelectedCoin(coin.symbol)}
                selected={isSelected}
                sx={{
                  borderRadius: 3,
                  mb: 0.25,
                  px: 1,
                  py: 0.5,
                  '&.Mui-selected': {
                    backgroundColor: 'rgba(25,118,210,0.2)',
                  },
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, fontSize: '0.75rem' }}>
                    {coin.symbol}
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 0.125 }}>
                    <Typography variant="subtitle2" sx={{ fontSize: '0.7rem' }}>
                      ${coin.price.toLocaleString()}
                    </Typography>
                    <Typography
                      variant="caption"
                      sx={{
                        fontSize: '0.65rem',
                        color: coin.changePct >= 0 ? 'success.main' : 'error.main',
                        fontWeight: 500,
                      }}
                    >
                      {coin.changePct > 0 ? '+' : ''}
                      {coin.changePct.toFixed(2)}%
                    </Typography>
                  </Box>
                </Box>
              </ListItemButton>
            )
          })}
          <Divider sx={{ my: 0.75, borderColor: 'rgba(255,255,255,0.08)' }} />
          <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.65rem' }}>
            {filteredCoins.length} markets
          </Typography>
        </List>
      )}
    </Box>
  )
}

export default CoinListSidebar

