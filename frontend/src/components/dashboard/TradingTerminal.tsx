import React, { useState } from 'react';
import {
  Box, Paper, Typography, Grid, Stack, TextField, Button,
  Select, MenuItem, FormControl, InputLabel, Card, CardContent,
  Table, TableHead, TableBody, TableRow, TableCell, Chip,
  IconButton, Tooltip, Divider, Switch, FormControlLabel,
  Tabs, Tab, Dialog, DialogTitle, DialogContent, DialogActions
} from '@mui/material';
import {
  PlayArrow, Pause, Stop, Speed, Timeline, TrendingUp, TrendingDown,
  AccountTree, Settings, Refresh, Add, Remove, Edit, Delete,
  SwapHoriz, CompareArrows, FlashOn, RadioButtonChecked
} from '@mui/icons-material';

interface QuickTrade {
  symbol: string;
  side: 'BUY' | 'SELL';
  quantity: number;
  orderType: 'MARKET' | 'LIMIT';
  price?: number;
  filled: number;
  remaining: number;
  status: 'WORKING' | 'FILLED' | 'CANCELLED';
}

interface HotKey {
  key: string;
  action: string;
  description: string;
}

interface AlgoStrategy {
  name: string;
  description: string;
  status: 'ACTIVE' | 'PAUSED' | 'STOPPED';
  pnl: number;
  trades: number;
}

const TradingTerminal: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [quickTradeSymbol, setQuickTradeSymbol] = useState('AAPL');
  const [quickTradeQuantity, setQuickTradeQuantity] = useState(100);
  const [quickTradePrice, setQuickTradePrice] = useState(192.53);
  const [quickTradeType, setQuickTradeType] = useState<'MARKET' | 'LIMIT'>('LIMIT');
  
  const [quickTrades] = useState<QuickTrade[]>([
    {
      symbol: 'AAPL', side: 'BUY', quantity: 500, orderType: 'LIMIT',
      price: 190.50, filled: 200, remaining: 300, status: 'WORKING'
    },
    {
      symbol: 'TSLA', side: 'SELL', quantity: 100, orderType: 'MARKET',
      filled: 100, remaining: 0, status: 'FILLED'
    },
    {
      symbol: 'MSFT', side: 'BUY', quantity: 250, orderType: 'LIMIT',
      price: 420.00, filled: 0, remaining: 250, status: 'WORKING'
    }
  ]);

  const [hotKeys] = useState<HotKey[]>([
    { key: 'F1', action: 'Quick Buy', description: 'Market buy current symbol' },
    { key: 'F2', action: 'Quick Sell', description: 'Market sell current symbol' },
    { key: 'F3', action: 'Cancel All', description: 'Cancel all working orders' },
    { key: 'F4', action: 'Flatten', description: 'Close all positions' },
    { key: 'Ctrl+B', action: 'Buy Limit', description: 'Place limit buy order' },
    { key: 'Ctrl+S', action: 'Sell Limit', description: 'Place limit sell order' },
    { key: 'Ctrl+R', action: 'Refresh', description: 'Refresh market data' },
    { key: 'Space', action: 'Pause/Resume', description: 'Pause/Resume trading' }
  ]);

  const [algoStrategies] = useState<AlgoStrategy[]>([
    {
      name: 'Mean Reversion',
      description: 'Trades oversold/overbought conditions',
      status: 'ACTIVE',
      pnl: 2340.50,
      trades: 45
    },
    {
      name: 'Momentum Scalper',
      description: 'High-frequency momentum trading',
      status: 'ACTIVE',
      pnl: 1890.25,
      trades: 127
    },
    {
      name: 'Pairs Trading',
      description: 'Statistical arbitrage strategy',
      status: 'PAUSED',
      pnl: -234.75,
      trades: 23
    },
    {
      name: 'Options Flow',
      description: 'Follows large options activity',
      status: 'ACTIVE',
      pnl: 5670.80,
      trades: 78
    }
  ]);

  const quickSizes = [10, 25, 50, 100, 250, 500, 1000, 2500];
  const [selectedQuickSize, setSelectedQuickSize] = useState(100);

  const handleQuickBuy = () => {
    console.log(`Quick Buy: ${selectedQuickSize} shares of ${quickTradeSymbol}`);
  };

  const handleQuickSell = () => {
    console.log(`Quick Sell: ${selectedQuickSize} shares of ${quickTradeSymbol}`);
  };

  const formatCurrency = (amount: number) => `$${amount.toFixed(2)}`;

  return (
    <Box sx={{ width: '100%', p: 2 }}>
      {/* Quick Action Bar */}
      <Paper sx={{ p: 2, mb: 3, background: 'linear-gradient(135deg, #263238 0%, #37474f 100%)', color: 'white' }}>
        <Grid container spacing={2} alignItems="center">
          {/* Symbol Input */}
          <Grid item xs={12} sm={2}>
            <TextField
              label="Symbol"
              value={quickTradeSymbol}
              onChange={(e) => setQuickTradeSymbol(e.target.value.toUpperCase())}
              size="small"
              fullWidth
              sx={{ 
                '& .MuiOutlinedInput-root': { color: 'white' },
                '& .MuiInputLabel-root': { color: 'white' },
                '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.3)' }
              }}
            />
          </Grid>

          {/* Quick Size Buttons */}
          <Grid item xs={12} sm={6}>
            <Stack direction="row" spacing={1}>
              {quickSizes.map((size) => (
                <Button
                  key={size}
                  variant={selectedQuickSize === size ? 'contained' : 'outlined'}
                  size="small"
                  onClick={() => setSelectedQuickSize(size)}
                  sx={{ 
                    minWidth: 50,
                    color: 'white',
                    borderColor: 'rgba(255,255,255,0.3)',
                    '&:hover': { backgroundColor: 'rgba(255,255,255,0.1)' }
                  }}
                >
                  {size}
                </Button>
              ))}
            </Stack>
          </Grid>

          {/* Quick Trade Buttons */}
          <Grid item xs={12} sm={4}>
            <Stack direction="row" spacing={1}>
              <Button
                variant="contained"
                color="success"
                startIcon={<TrendingUp />}
                onClick={handleQuickBuy}
                sx={{ flex: 1, fontWeight: 'bold' }}
              >
                BUY
              </Button>
              <Button
                variant="contained"
                color="error"
                startIcon={<TrendingDown />}
                onClick={handleQuickSell}
                sx={{ flex: 1, fontWeight: 'bold' }}
              >
                SELL
              </Button>
            </Stack>
          </Grid>
        </Grid>
      </Paper>

      {/* Trading Terminal Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Order Entry" />
          <Tab label="Quick Trades" />
          <Tab label="Algo Strategies" />
          <Tab label="Hotkeys" />
        </Tabs>
      </Box>

      {/* Order Entry Tab */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>Advanced Order Entry</Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    label="Symbol"
                    value={quickTradeSymbol}
                    onChange={(e) => setQuickTradeSymbol(e.target.value.toUpperCase())}
                    size="small"
                    fullWidth
                  />
                </Grid>
                <Grid item xs={6}>
                  <FormControl size="small" fullWidth>
                    <InputLabel>Side</InputLabel>
                    <Select defaultValue="BUY">
                      <MenuItem value="BUY">BUY</MenuItem>
                      <MenuItem value="SELL">SELL</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={6}>
                  <TextField
                    label="Quantity"
                    type="number"
                    value={quickTradeQuantity}
                    onChange={(e) => setQuickTradeQuantity(Number(e.target.value))}
                    size="small"
                    fullWidth
                  />
                </Grid>
                <Grid item xs={6}>
                  <FormControl size="small" fullWidth>
                    <InputLabel>Order Type</InputLabel>
                    <Select 
                      value={quickTradeType}
                      onChange={(e) => setQuickTradeType(e.target.value as 'MARKET' | 'LIMIT')}
                    >
                      <MenuItem value="MARKET">Market</MenuItem>
                      <MenuItem value="LIMIT">Limit</MenuItem>
                      <MenuItem value="STOP">Stop</MenuItem>
                      <MenuItem value="STOP_LIMIT">Stop Limit</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                {quickTradeType === 'LIMIT' && (
                  <Grid item xs={6}>
                    <TextField
                      label="Limit Price"
                      type="number"
                      value={quickTradePrice}
                      onChange={(e) => setQuickTradePrice(Number(e.target.value))}
                      size="small"
                      fullWidth
                      inputProps={{ step: 0.01 }}
                    />
                  </Grid>
                )}
                
                <Grid item xs={6}>
                  <FormControl size="small" fullWidth>
                    <InputLabel>Time in Force</InputLabel>
                    <Select defaultValue="DAY">
                      <MenuItem value="DAY">Day</MenuItem>
                      <MenuItem value="GTC">GTC</MenuItem>
                      <MenuItem value="IOC">IOC</MenuItem>
                      <MenuItem value="FOK">FOK</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12}>
                  <Stack direction="row" spacing={2}>
                    <Button 
                      variant="contained" 
                      color="success" 
                      fullWidth 
                      size="large"
                      sx={{ fontWeight: 'bold' }}
                    >
                      Place Buy Order
                    </Button>
                    <Button 
                      variant="contained" 
                      color="error" 
                      fullWidth 
                      size="large"
                      sx={{ fontWeight: 'bold' }}
                    >
                      Place Sell Order
                    </Button>
                  </Stack>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>Order Templates</Typography>
              
              <Stack spacing={2}>
                <Card variant="outlined">
                  <CardContent sx={{ p: 2 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                      Bracket Order
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Entry + Profit Target + Stop Loss
                    </Typography>
                    <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                      <Button size="small" variant="outlined">Use Template</Button>
                      <Button size="small" variant="outlined">Edit</Button>
                    </Stack>
                  </CardContent>
                </Card>
                
                <Card variant="outlined">
                  <CardContent sx={{ p: 2 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                      Scale In/Out
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Multiple orders at different price levels
                    </Typography>
                    <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                      <Button size="small" variant="outlined">Use Template</Button>
                      <Button size="small" variant="outlined">Edit</Button>
                    </Stack>
                  </CardContent>
                </Card>
                
                <Card variant="outlined">
                  <CardContent sx={{ p: 2 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                      Covered Call
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Stock + Short Call Option
                    </Typography>
                    <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                      <Button size="small" variant="outlined">Use Template</Button>
                      <Button size="small" variant="outlined">Edit</Button>
                    </Stack>
                  </CardContent>
                </Card>
              </Stack>
            </Paper>
          </Grid>
        </Grid>
      )}

      {/* Quick Trades Tab */}
      {activeTab === 1 && (
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>Quick Trades</Typography>
          
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Symbol</TableCell>
                <TableCell>Side</TableCell>
                <TableCell align="right">Quantity</TableCell>
                <TableCell align="right">Price</TableCell>
                <TableCell align="right">Filled</TableCell>
                <TableCell align="right">Remaining</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {quickTrades.map((trade, index) => (
                <TableRow key={index} hover>
                  <TableCell sx={{ fontWeight: 'bold' }}>{trade.symbol}</TableCell>
                  <TableCell>
                    <Chip
                      label={trade.side}
                      size="small"
                      color={trade.side === 'BUY' ? 'success' : 'error'}
                    />
                  </TableCell>
                  <TableCell align="right">{trade.quantity.toLocaleString()}</TableCell>
                  <TableCell align="right">
                    {trade.orderType === 'MARKET' ? 'Market' : formatCurrency(trade.price || 0)}
                  </TableCell>
                  <TableCell align="right">{trade.filled.toLocaleString()}</TableCell>
                  <TableCell align="right">{trade.remaining.toLocaleString()}</TableCell>
                  <TableCell>
                    <Chip
                      label={trade.status}
                      size="small"
                      color={trade.status === 'FILLED' ? 'success' : 
                             trade.status === 'WORKING' ? 'warning' : 'default'}
                    />
                  </TableCell>
                  <TableCell align="center">
                    <Stack direction="row" spacing={1}>
                      <IconButton size="small" color="primary">
                        <Edit />
                      </IconButton>
                      <IconButton size="small" color="error">
                        <Stop />
                      </IconButton>
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      )}

      {/* Algo Strategies Tab */}
      {activeTab === 2 && (
        <Grid container spacing={3}>
          {algoStrategies.map((strategy, index) => (
            <Grid item xs={12} md={6} key={index}>
              <Card>
                <CardContent>
                  <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                    <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                      {strategy.name}
                    </Typography>
                    <Stack direction="row" alignItems="center" spacing={1}>
                      <RadioButtonChecked 
                        sx={{ 
                          color: strategy.status === 'ACTIVE' ? '#00C853' : 
                                 strategy.status === 'PAUSED' ? '#FFB300' : '#757575'
                        }} 
                      />
                      <Chip
                        label={strategy.status}
                        size="small"
                        color={strategy.status === 'ACTIVE' ? 'success' : 
                               strategy.status === 'PAUSED' ? 'warning' : 'default'}
                      />
                    </Stack>
                  </Stack>
                  
                  <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                    {strategy.description}
                  </Typography>
                  
                  <Grid container spacing={2} sx={{ mb: 2 }}>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="textSecondary">P&L</Typography>
                      <Typography 
                        variant="h6" 
                        sx={{ 
                          color: strategy.pnl > 0 ? '#00C853' : '#FF1744',
                          fontWeight: 'bold'
                        }}
                      >
                        {strategy.pnl > 0 ? '+' : ''}{formatCurrency(strategy.pnl)}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="textSecondary">Trades</Typography>
                      <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                        {strategy.trades}
                      </Typography>
                    </Grid>
                  </Grid>
                  
                  <Stack direction="row" spacing={1}>
                    <Button
                      size="small"
                      variant="outlined"
                      color={strategy.status === 'ACTIVE' ? 'warning' : 'success'}
                      startIcon={strategy.status === 'ACTIVE' ? <Pause /> : <PlayArrow />}
                    >
                      {strategy.status === 'ACTIVE' ? 'Pause' : 'Start'}
                    </Button>
                    <Button size="small" variant="outlined" startIcon={<Stop />}>
                      Stop
                    </Button>
                    <Button size="small" variant="outlined" startIcon={<Settings />}>
                      Config
                    </Button>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Hotkeys Tab */}
      {activeTab === 3 && (
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>Keyboard Shortcuts</Typography>
          
          <Grid container spacing={2}>
            {hotKeys.map((hotkey, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Card variant="outlined">
                  <CardContent sx={{ p: 2 }}>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Box>
                        <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                          {hotkey.action}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {hotkey.description}
                        </Typography>
                      </Box>
                      <Chip
                        label={hotkey.key}
                        size="small"
                        variant="outlined"
                        sx={{ fontFamily: 'monospace', fontWeight: 'bold' }}
                      />
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>
      )}
    </Box>
  );
};

export default TradingTerminal;