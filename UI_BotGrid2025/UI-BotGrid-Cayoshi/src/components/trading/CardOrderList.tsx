import { useEffect, useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material'
import type { OrderItem } from '../../services/api'
import { getOpenOrders } from '../../services/api'

const statusColor: Record<OrderItem['status'], 'info' | 'success' | 'warning'> = {
  Open: 'info',
  Filled: 'success',
  Cancelled: 'warning',
}

export const CardOrderList = () => {
  const [orders, setOrders] = useState<OrderItem[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const fetchOrders = async () => {
      setLoading(true)
      const data = await getOpenOrders()
      setOrders(data)
      setLoading(false)
    }
    fetchOrders()
  }, [])

  return (
    <Card sx={{ p: 2, borderRadius: 2, height: '100%' }}>
      <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">Orders</Typography>
          <Typography variant="caption" color="text.secondary">
            Updated just now
          </Typography>
        </Box>
        {loading ? (
          <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <CircularProgress size={24} />
          </Box>
        ) : (
          <Table size="small" stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>Order ID</TableCell>
                <TableCell>Side</TableCell>
                <TableCell>Price</TableCell>
                <TableCell>Amount</TableCell>
                <TableCell>PnL</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {orders.map((order) => (
                <TableRow key={order.id} hover>
                  <TableCell>{order.id}</TableCell>
                  <TableCell>
                    <Typography color={order.side === 'Buy' ? 'success.main' : 'error.main'}>
                      {order.side}
                    </Typography>
                  </TableCell>
                  <TableCell>${order.price.toLocaleString()}</TableCell>
                  <TableCell>{order.amount.toFixed(3)}</TableCell>
                  <TableCell
                    sx={{ color: order.pnl >= 0 ? 'success.main' : 'error.main' }}
                  >
                    {order.pnl >= 0 ? '+' : '-'}${Math.abs(order.pnl).toFixed(2)}
                  </TableCell>
                  <TableCell>
                    <Chip label={order.status} color={statusColor[order.status]} size="small" />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  )
}

export default CardOrderList

