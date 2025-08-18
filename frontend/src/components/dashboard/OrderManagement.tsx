import React, { useState, useEffect } from 'react';
import {
  Paper, Typography, Box, Grid, Tabs, Tab, Table, TableHead, TableBody, 
  TableRow, TableCell, Button, TextField, Select, MenuItem, FormControl, 
  InputLabel, Chip, IconButton, Dialog, DialogTitle, DialogContent, 
  DialogActions, Stack, Card, CardContent, Slider, Switch, FormControlLabel
} from '@mui/material';
import {
  Add, Edit, Delete, PlayArrow, Pause, Stop, Schedule, 
  TrendingUp, TrendingDown, Warning, CheckCircle, Cancel,
  Speed, Timeline, AccountTree
} from '@mui/icons-material';

interface Order {
  id: string;
  symbol: string;
  side: 'BUY' | 'SELL';
  orderType: 'MARKET' | 'LIMIT' | 'STOP' | 'STOP_LIMIT' | 'TWAP' | 'VWAP' | 'ICEBERG';
  quantity: number;
  price?: number;
  stopPrice?: number;
  status: 'PENDING' | 'WORKING' | 'FILLED' | 'CANCELLED' | 'REJECTED';
  timeInForce: 'DAY' | 'GTC' | 'IOC' | 'FOK';
  filledQuantity: number;
  avgFillPrice: number;
  timestamp: string;
  estimatedCommission: number;
  algorithm?: string;
  parentOrderId?: string;
}

interface AlgoOrder {
  name: string;
  description: string;
  parameters: { [key: string]: any };
  icon: React.ReactNode;
}

const OrderManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [openOrderDialog, setOpenOrderDialog] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  
  const [newOrder, setNewOrder] = useState({
    symbol: 'AAPL',
    side: 'BUY' as const,
    orderType: 'LIMIT' as const,
    quantity: 100,
    price: 0,
    stopPrice: 0,
    timeInForce: 'DAY' as const,
    algorithm: ''
  });

  const [orders] = useState<Order[]>([
    {
      id: '1', symbol: 'AAPL', side: 'BUY', orderType: 'LIMIT', quantity: 500, price: 190.50,
      status: 'WORKING', timeInForce: 'GTC', filledQuantity: 200, avgFillPrice: 190.45,
      timestamp: '2024-01-12 09:30:15', estimatedCommission: 2.50
    },
    {
      id: '2', symbol: 'TSLA', side: 'SELL', orderType: 'STOP_LIMIT', quantity: 100, price: 1050.00, stopPrice: 1080.00,
      status: 'PENDING', timeInForce: 'DAY', filledQuantity: 0, avgFillPrice: 0,
      timestamp: '2024-01-12 10:15:30', estimatedCommission: 1.50
    },
    {
      id: '3', symbol: 'MSFT', side: 'BUY', orderType: 'TWAP', quantity: 1000, price: 420.00,
      status: 'WORKING', timeInForce: 'DAY', filledQuantity: 350, avgFillPrice: 419.75,
      timestamp: '2024-01-12 08:45:20', estimatedCommission: 5.00, algorithm: 'TWAP-30min'
    },
    {
      id: '4', symbol: 'GOOGL', side: 'BUY', orderType: 'ICEBERG', quantity: 200, price: 2750.00,
      status: 'WORKING', timeInForce: 'GTC', filledQuantity: 75, avgFillPrice: 2748.50,
      timestamp: '2024-01-12 11:20:45', estimatedCommission: 3.75, algorithm: 'ICEBERG-25'
    }
  ]);

  const algorithmicOrders: AlgoOrder[] = [
    {
      name: 'TWAP',
      description: 'Time-Weighted Average Price - spreads order over time',
      parameters: { duration: 30, slices: 6 },
      icon: <Timeline />
    },
    {
      name: 'VWAP',
      description: 'Volume-Weighted Average Price - trades based on historical volume patterns',
      parameters: { participation: 0.15, maxVolume: 0.25 },
      icon: <Speed />
    },
    {
      name: 'ICEBERG',
      description: 'Hides large orders by showing only small portions',
      parameters: { displaySize: 100, variance: 0.1 },
      icon: <AccountTree />
    },
    {
      name: 'IMPLEMENTATION SHORTFALL',
      description: 'Minimizes market impact and timing risk',
      parameters: { urgency: 0.5, riskAversion: 0.3 },
      icon: <TrendingUp />
    }
  ];

  const orderStatistics = {
    totalOrders: 156,
    workingOrders: 12,
    filledOrders: 134,
    cancelledOrders: 10,
    fillRate: 95.7,
    avgFillTime: 2.3,
    totalCommissions: 1234.56,
    savingsFromAlgos: 5678.90
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'FILLED': return '#00C853';
      case 'WORKING': return '#2196F3';
      case 'PENDING': return '#FFB300';
      case 'CANCELLED': return '#757575';
      case 'REJECTED': return '#FF1744';
      default: return '#757575';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'FILLED': return <CheckCircle sx={{ fontSize: 16 }} />;
      case 'WORKING': return <PlayArrow sx={{ fontSize: 16 }} />;
      case 'PENDING': return <Schedule sx={{ fontSize: 16 }} />;
      case 'CANCELLED': return <Cancel sx={{ fontSize: 16 }} />;
      case 'REJECTED': return <Warning sx={{ fontSize: 16 }} />;
      default: return null;
    }
  };

  const formatCurrency = (amount: number) => `$${amount.toFixed(2)}`;

  const handleNewOrder = () => {
    setSelectedOrder(null);
    setOpenOrderDialog(true);
  };

  const handleEditOrder = (order: Order) => {
    setSelectedOrder(order);
    setNewOrder({
      symbol: order.symbol,
      side: order.side,
      orderType: order.orderType,
      quantity: order.quantity,
      price: order.price || 0,
      stopPrice: order.stopPrice || 0,
      timeInForce: order.timeInForce,
      algorithm: order.algorithm || ''
    });
    setOpenOrderDialog(true);
  };

  return (
    <Box sx={{ width: '100%', p: 2 }}>
      {/* Order Statistics */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                {orderStatistics.workingOrders}
              </Typography>
              <Typography variant="subtitle1">Working Orders</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                {orderStatistics.fillRate}%
              </Typography>
              <Typography variant="subtitle1">Fill Rate</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', color: 'white' }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                {orderStatistics.avgFillTime}s
              </Typography>
              <Typography variant="subtitle1">Avg Fill Time</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', color: 'white' }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                {formatCurrency(orderStatistics.savingsFromAlgos)}
              </Typography>
              <Typography variant="subtitle1">Algo Savings</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Action Buttons */}
      <Box sx={{ mb: 3 }}>
        <Stack direction="row" spacing={2}>
          <Button 
            variant="contained" 
            startIcon={<Add />} 
            onClick={handleNewOrder}
            sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
          >
            New Order
          </Button>
          <Button variant="outlined" startIcon={<Timeline />}>
            Algo Builder
          </Button>
          <Button variant="outlined" startIcon={<Speed />}>
            Strategy Optimizer
          </Button>
        </Stack>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Working Orders" />
          <Tab label="Order History" />
          <Tab label="Algorithmic Orders" />
          <Tab label="Order Analytics" />
        </Tabs>
      </Box>

      {/* Orders Table */}
      {activeTab === 0 && (
        <Paper sx={{ width: '100%' }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Symbol</TableCell>
                <TableCell>Side</TableCell>
                <TableCell>Type</TableCell>
                <TableCell align="right">Quantity</TableCell>
                <TableCell align="right">Price</TableCell>
                <TableCell align="right">Filled</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>TIF</TableCell>
                <TableCell>Algorithm</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {orders.filter(order => ['PENDING', 'WORKING'].includes(order.status)).map((order) => (
                <TableRow key={order.id} hover>
                  <TableCell sx={{ fontWeight: 'bold' }}>{order.symbol}</TableCell>
                  <TableCell>
                    <Chip
                      label={order.side}
                      size="small"
                      color={order.side === 'BUY' ? 'success' : 'error'}
                      icon={order.side === 'BUY' ? <TrendingUp /> : <TrendingDown />}
                    />
                  </TableCell>
                  <TableCell>
                    <Chip label={order.orderType} size="small" variant="outlined" />
                  </TableCell>
                  <TableCell align="right">{order.quantity.toLocaleString()}</TableCell>
                  <TableCell align="right">
                    {order.price ? formatCurrency(order.price) : 'Market'}
                  </TableCell>
                  <TableCell align="right">
                    <Box>
                      <Typography variant="body2">
                        {order.filledQuantity.toLocaleString()} / {order.quantity.toLocaleString()}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {order.avgFillPrice > 0 && `@ ${formatCurrency(order.avgFillPrice)}`}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={order.status}
                      size="small"
                      sx={{ 
                        backgroundColor: getStatusColor(order.status),
                        color: 'white'
                      }}
                      icon={getStatusIcon(order.status)}
                    />
                  </TableCell>
                  <TableCell>
                    <Chip label={order.timeInForce} size="small" variant="outlined" />
                  </TableCell>
                  <TableCell>
                    {order.algorithm && (
                      <Chip label={order.algorithm} size="small" color="primary" variant="outlined" />
                    )}
                  </TableCell>
                  <TableCell align="center">
                    <Stack direction="row" spacing={1}>
                      <IconButton 
                        size="small" 
                        color="primary"
                        onClick={() => handleEditOrder(order)}
                      >
                        <Edit />
                      </IconButton>
                      <IconButton size="small" color="error">
                        <Cancel />
                      </IconButton>
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      )}

      {/* Algorithmic Orders Tab */}
      {activeTab === 2 && (
        <Grid container spacing={3}>
          {algorithmicOrders.map((algo, index) => (
            <Grid item xs={12} md={6} key={index}>
              <Card sx={{ height: '100%', border: '1px solid #e0e0e0' }}>
                <CardContent>
                  <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2 }}>
                    <Box sx={{ color: 'primary.main' }}>{algo.icon}</Box>
                    <Typography variant="h6">{algo.name}</Typography>
                  </Stack>
                  <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                    {algo.description}
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" sx={{ mb: 1 }}>Parameters:</Typography>
                    {Object.entries(algo.parameters).map(([key, value]) => (
                      <Typography key={key} variant="caption" display="block">
                        {key}: {typeof value === 'number' ? value.toFixed(2) : value}
                      </Typography>
                    ))}
                  </Box>
                  <Button
                    variant="contained"
                    fullWidth
                    size="small"
                    sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
                  >
                    Use Algorithm
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* New Order Dialog */}
      <Dialog 
        open={openOrderDialog} 
        onClose={() => setOpenOrderDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedOrder ? 'Edit Order' : 'New Order'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={4}>
              <TextField
                label="Symbol"
                value={newOrder.symbol}
                onChange={(e) => setNewOrder({...newOrder, symbol: e.target.value.toUpperCase()})}
                fullWidth
                size="small"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Side</InputLabel>
                <Select
                  value={newOrder.side}
                  onChange={(e) => setNewOrder({...newOrder, side: e.target.value as 'BUY' | 'SELL'})}
                >
                  <MenuItem value="BUY">BUY</MenuItem>
                  <MenuItem value="SELL">SELL</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Order Type</InputLabel>
                <Select
                  value={newOrder.orderType}
                  onChange={(e) => setNewOrder({...newOrder, orderType: e.target.value as any})}
                >
                  <MenuItem value="MARKET">Market</MenuItem>
                  <MenuItem value="LIMIT">Limit</MenuItem>
                  <MenuItem value="STOP">Stop</MenuItem>
                  <MenuItem value="STOP_LIMIT">Stop Limit</MenuItem>
                  <MenuItem value="TWAP">TWAP</MenuItem>
                  <MenuItem value="VWAP">VWAP</MenuItem>
                  <MenuItem value="ICEBERG">Iceberg</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                label="Quantity"
                type="number"
                value={newOrder.quantity}
                onChange={(e) => setNewOrder({...newOrder, quantity: Number(e.target.value)})}
                fullWidth
                size="small"
              />
            </Grid>
            {newOrder.orderType !== 'MARKET' && (
              <Grid item xs={12} md={4}>
                <TextField
                  label="Price"
                  type="number"
                  value={newOrder.price}
                  onChange={(e) => setNewOrder({...newOrder, price: Number(e.target.value)})}
                  fullWidth
                  size="small"
                />
              </Grid>
            )}
            <Grid item xs={12} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Time in Force</InputLabel>
                <Select
                  value={newOrder.timeInForce}
                  onChange={(e) => setNewOrder({...newOrder, timeInForce: e.target.value as any})}
                >
                  <MenuItem value="DAY">Day</MenuItem>
                  <MenuItem value="GTC">Good Till Canceled</MenuItem>
                  <MenuItem value="IOC">Immediate or Cancel</MenuItem>
                  <MenuItem value="FOK">Fill or Kill</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenOrderDialog(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
          >
            {selectedOrder ? 'Update Order' : 'Place Order'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default OrderManagement;