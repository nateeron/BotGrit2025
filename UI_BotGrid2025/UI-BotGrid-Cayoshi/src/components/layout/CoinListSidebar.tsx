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
} from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'
import RefreshIcon from '@mui/icons-material/Refresh'
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
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: 'rgba(255,255,255,0.02)',
        borderRadius: 3,
        p: 2,
      }}
    >
      <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', mb: 2 }}>
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
                  borderRadius: 2,
                  mb: 0.5,
                  '&.Mui-selected': {
                    backgroundColor: 'rgba(25,118,210,0.2)',
                  },
                }}
              >
                <Avatar
                  sx={{
                    width: 36,
                    height: 36,
                    mr: 2,
                    fontSize: 14,
                    bgcolor: 'rgba(255,255,255,0.08)',
                  }}
                >
                  {getAvatarChar(coin.symbol)}
                </Avatar>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Typography variant="subtitle2">{coin.symbol}</Typography>
                      <Typography variant="subtitle2">${coin.price.toLocaleString()}</Typography>
                    </Box>
                  }
                  secondary={
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Typography variant="caption" color="text.secondary">
                        {coin.name}
                      </Typography>
                      <Typography
                        variant="caption"
                        color={coin.changePct >= 0 ? 'success.main' : 'error.main'}
                      >
                        {coin.changePct > 0 ? '+' : ''}
                        {coin.changePct.toFixed(2)}%
                      </Typography>
                    </Box>
                  }
                  primaryTypographyProps={{ component: 'div' }}
                  secondaryTypographyProps={{ component: 'div' }}
                />
              </ListItemButton>
            )
          })}
          <Divider sx={{ my: 1, borderColor: 'rgba(255,255,255,0.08)' }} />
          <Typography variant="caption" color="text.secondary">
            {filteredCoins.length} markets
          </Typography>
        </List>
      )}
    </Box>
  )
}

export default CoinListSidebar

