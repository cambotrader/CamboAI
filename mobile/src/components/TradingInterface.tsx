/**
 * 📱 MOBILE TRADING INTERFACE - BEYOND ROBINHOOD
 * Professional-grade mobile trading with advanced features
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  Dimensions,
  Animated,
  PanGestureHandler,
  PinchGestureHandler,
  State
} from 'react-native';
import { LineChart, CandlestickChart } from 'react-native-wagmi-charts';
import { Ionicons, MaterialIcons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import * as Haptics from 'expo-haptics';
import { BlurView } from 'expo-blur';

interface MarketData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  high: number;
  low: number;
  open: number;
  bid: number;
  ask: number;
}

interface Position {
  symbol: string;
  quantity: number;
  avgPrice: number;
  currentPrice: number;
  unrealizedPnL: number;
  unrealizedPnLPercent: number;
  marketValue: number;
}

interface Order {
  id: string;
  symbol: string;
  side: 'buy' | 'sell';
  quantity: number;
  price: number;
  type: 'market' | 'limit' | 'stop' | 'stop_limit';
  status: 'pending' | 'filled' | 'cancelled' | 'partial';
  timestamp: Date;
}

interface TradingInterfaceProps {
  initialSymbol?: string;
  theme?: 'dark' | 'light';
}

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

const TradingInterface: React.FC<TradingInterfaceProps> = ({
  initialSymbol = 'AAPL',
  theme = 'dark'
}) => {
  // State management
  const [selectedSymbol, setSelectedSymbol] = useState(initialSymbol);
  const [marketData, setMarketData] = useState<Record<string, MarketData>>({});
  const [positions, setPositions] = useState<Position[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [watchlist, setWatchlist] = useState<string[]>(['AAPL', 'TSLA', 'MSFT', 'NVDA', 'SPY']);
  const [activeTab, setActiveTab] = useState<'trade' | 'positions' | 'orders' | 'watchlist'>('trade');
  const [chartTimeframe, setChartTimeframe] = useState<'1m' | '5m' | '1h' | '1d' | '1w'>('1h');
  const [orderType, setOrderType] = useState<'market' | 'limit'>('market');
  const [orderSide, setOrderSide] = useState<'buy' | 'sell'>('buy');
  const [orderQuantity, setOrderQuantity] = useState('');
  const [orderPrice, setOrderPrice] = useState('');
  const [showOrderForm, setShowOrderForm] = useState(false);
  const [chartData, setChartData] = useState<any[]>([]);

  // Animation refs
  const orderFormAnimation = useRef(new Animated.Value(0)).current;
  const priceAnimation = useRef(new Animated.Value(1)).current;

  // Mock data generation
  const generateMockData = useCallback((symbol: string): MarketData => {
    const basePrice = {
      'AAPL': 180,
      'TSLA': 220,
      'MSFT': 340,
      'NVDA': 850,
      'SPY': 450
    }[symbol] || 100;

    const change = (Math.random() - 0.5) * 10;
    const changePercent = (change / basePrice) * 100;

    return {
      symbol,
      price: basePrice + change,
      change,
      changePercent,
      volume: Math.floor(Math.random() * 10000000),
      high: basePrice + Math.abs(change) + Math.random() * 5,
      low: basePrice - Math.abs(change) - Math.random() * 5,
      open: basePrice + (Math.random() - 0.5) * 5,
      bid: basePrice + change - 0.05,
      ask: basePrice + change + 0.05
    };
  }, []);

  // Generate mock chart data
  const generateChartData = useCallback(() => {
    const data = [];
    const now = Date.now();
    const interval = chartTimeframe === '1m' ? 60000 : 
                    chartTimeframe === '5m' ? 300000 :
                    chartTimeframe === '1h' ? 3600000 :
                    chartTimeframe === '1d' ? 86400000 : 604800000;

    for (let i = 100; i >= 0; i--) {
      const timestamp = now - (i * interval);
      const basePrice = marketData[selectedSymbol]?.price || 180;
      const volatility = 0.02;
      const price = basePrice + (Math.random() - 0.5) * basePrice * volatility;
      
      data.push({
        timestamp,
        value: price
      });
    }
    return data;
  }, [selectedSymbol, chartTimeframe, marketData]);

  // Initialize data
  useEffect(() => {
    const updateData = () => {
      const newMarketData: Record<string, MarketData> = {};
      watchlist.forEach(symbol => {
        newMarketData[symbol] = generateMockData(symbol);
      });
      setMarketData(newMarketData);
    };

    updateData();
    const interval = setInterval(updateData, 1000);
    return () => clearInterval(interval);
  }, [watchlist, generateMockData]);

  // Update chart data
  useEffect(() => {
    setChartData(generateChartData());
  }, [generateChartData]);

  // Animate price changes
  useEffect(() => {
    Animated.sequence([
      Animated.timing(priceAnimation, {
        toValue: 1.1,
        duration: 100,
        useNativeDriver: true,
      }),
      Animated.timing(priceAnimation, {
        toValue: 1,
        duration: 100,
        useNativeDriver: true,
      }),
    ]).start();
  }, [marketData[selectedSymbol]?.price]);

  // Handle order submission
  const handlePlaceOrder = async () => {
    if (!orderQuantity || (orderType === 'limit' && !orderPrice)) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    const currentData = marketData[selectedSymbol];
    if (!currentData) {
      Alert.alert('Error', 'Market data not available');
      return;
    }

    const newOrder: Order = {
      id: `order_${Date.now()}`,
      symbol: selectedSymbol,
      side: orderSide,
      quantity: parseInt(orderQuantity),
      price: orderType === 'market' ? currentData.price : parseFloat(orderPrice),
      type: orderType,
      status: 'pending',
      timestamp: new Date()
    };

    setOrders(prev => [newOrder, ...prev]);
    
    // Simulate order filling
    setTimeout(() => {
      setOrders(prev => 
        prev.map(order => 
          order.id === newOrder.id 
            ? { ...order, status: 'filled' as const }
            : order
        )
      );
      
      // Add to positions
      const existingPosition = positions.find(p => p.symbol === selectedSymbol);
      if (existingPosition) {
        // Update existing position
        const newQuantity = orderSide === 'buy' 
          ? existingPosition.quantity + newOrder.quantity
          : existingPosition.quantity - newOrder.quantity;
        
        if (newQuantity !== 0) {
          const newAvgPrice = orderSide === 'buy'
            ? ((existingPosition.avgPrice * existingPosition.quantity) + (newOrder.price * newOrder.quantity)) / newQuantity
            : existingPosition.avgPrice;
          
          setPositions(prev =>
            prev.map(pos =>
              pos.symbol === selectedSymbol
                ? {
                    ...pos,
                    quantity: newQuantity,
                    avgPrice: newAvgPrice,
                    marketValue: newQuantity * currentData.price,
                    unrealizedPnL: (currentData.price - newAvgPrice) * newQuantity,
                    unrealizedPnLPercent: ((currentData.price - newAvgPrice) / newAvgPrice) * 100
                  }
                : pos
            )
          );
        } else {
          // Remove position if quantity becomes 0
          setPositions(prev => prev.filter(pos => pos.symbol !== selectedSymbol));
        }
      } else if (orderSide === 'buy') {
        // Create new position
        const newPosition: Position = {
          symbol: selectedSymbol,
          quantity: newOrder.quantity,
          avgPrice: newOrder.price,
          currentPrice: currentData.price,
          marketValue: newOrder.quantity * currentData.price,
          unrealizedPnL: (currentData.price - newOrder.price) * newOrder.quantity,
          unrealizedPnLPercent: ((currentData.price - newOrder.price) / newOrder.price) * 100
        };
        setPositions(prev => [...prev, newPosition]);
      }
      
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    }, Math.random() * 2000 + 1000); // 1-3 second delay

    // Close order form
    setShowOrderForm(false);
    setOrderQuantity('');
    setOrderPrice('');
    
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
  };

  // Toggle order form
  const toggleOrderForm = () => {
    setShowOrderForm(!showOrderForm);
    Animated.timing(orderFormAnimation, {
      toValue: showOrderForm ? 0 : 1,
      duration: 300,
      useNativeDriver: true,
    }).start();
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
  };

  // Render watchlist item
  const renderWatchlistItem = (symbol: string) => {
    const data = marketData[symbol];
    if (!data) return null;

    const isSelected = symbol === selectedSymbol;
    const isPositive = data.change >= 0;

    return (
      <TouchableOpacity
        key={symbol}
        style={[
          styles.watchlistItem,
          isSelected && styles.watchlistItemSelected,
          { backgroundColor: isSelected ? '#007AFF20' : 'transparent' }
        ]}
        onPress={() => {
          setSelectedSymbol(symbol);
          Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
        }}
      >
        <View style={styles.watchlistItemLeft}>
          <Text style={[styles.symbolText, { color: isSelected ? '#007AFF' : '#FFFFFF' }]}>
            {symbol}
          </Text>
          <Animated.Text 
            style={[
              styles.priceText, 
              { 
                color: isPositive ? '#00FF88' : '#FF6B6B',
                transform: [{ scale: isSelected ? priceAnimation : 1 }]
              }
            ]}
          >
            ${data.price.toFixed(2)}
          </Animated.Text>
        </View>
        <View style={styles.watchlistItemRight}>
          <Text style={[styles.changeText, { color: isPositive ? '#00FF88' : '#FF6B6B' }]}>
            {isPositive ? '+' : ''}{data.change.toFixed(2)}
          </Text>
          <Text style={[styles.changePercentText, { color: isPositive ? '#00FF88' : '#FF6B6B' }]}>
            {isPositive ? '+' : ''}{data.changePercent.toFixed(2)}%
          </Text>
        </View>
      </TouchableOpacity>
    );
  };

  // Render chart
  const renderChart = () => {
    const currentData = marketData[selectedSymbol];
    const isPositive = currentData ? currentData.change >= 0 : true;

    return (
      <View style={styles.chartContainer}>
        <View style={styles.chartHeader}>
          <View>
            <Text style={styles.chartSymbol}>{selectedSymbol}</Text>
            {currentData && (
              <Animated.Text 
                style={[
                  styles.chartPrice,
                  { transform: [{ scale: priceAnimation }] }
                ]}
              >
                ${currentData.price.toFixed(2)}
              </Animated.Text>
            )}
          </View>
          <View style={styles.timeframeSelector}>
            {['1m', '5m', '1h', '1d', '1w'].map((tf) => (
              <TouchableOpacity
                key={tf}
                style={[
                  styles.timeframeButton,
                  chartTimeframe === tf && styles.timeframeButtonActive
                ]}
                onPress={() => {
                  setChartTimeframe(tf as any);
                  Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
                }}
              >
                <Text style={[
                  styles.timeframeText,
                  chartTimeframe === tf && styles.timeframeTextActive
                ]}>
                  {tf}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
        
        <View style={styles.chart}>
          <LineChart.Provider data={chartData}>
            <LineChart height={250}>
              <LineChart.Path color={isPositive ? '#00FF88' : '#FF6B6B'} width={2} />
              <LineChart.CursorCrosshair color="#FFFFFF50" />
            </LineChart>
          </LineChart.Provider>
        </View>

        {currentData && (
          <View style={styles.marketStats}>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Open</Text>
              <Text style={styles.statValue}>${currentData.open.toFixed(2)}</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>High</Text>
              <Text style={styles.statValue}>${currentData.high.toFixed(2)}</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Low</Text>
              <Text style={styles.statValue}>${currentData.low.toFixed(2)}</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Volume</Text>
              <Text style={styles.statValue}>{(currentData.volume / 1000000).toFixed(1)}M</Text>
            </View>
          </View>
        )}
      </View>
    );
  };

  // Render order form
  const renderOrderForm = () => (
    <Animated.View
      style={[
        styles.orderForm,
        {
          transform: [{
            translateY: orderFormAnimation.interpolate({
              inputRange: [0, 1],
              outputRange: [300, 0],
            }),
          }],
          opacity: orderFormAnimation,
        },
      ]}
    >
      <BlurView intensity={90} style={styles.orderFormBlur}>
        <View style={styles.orderFormContent}>
          <View style={styles.orderFormHeader}>
            <Text style={styles.orderFormTitle}>Place Order - {selectedSymbol}</Text>
            <TouchableOpacity onPress={toggleOrderForm}>
              <Ionicons name="close" size={24} color="#FFFFFF" />
            </TouchableOpacity>
          </View>

          {/* Order Side Selector */}
          <View style={styles.orderSideSelector}>
            <TouchableOpacity
              style={[
                styles.orderSideButton,
                styles.buyButton,
                orderSide === 'buy' && styles.orderSideButtonActive
              ]}
              onPress={() => setOrderSide('buy')}
            >
              <Text style={[
                styles.orderSideButtonText,
                orderSide === 'buy' && styles.orderSideButtonTextActive
              ]}>
                BUY
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[
                styles.orderSideButton,
                styles.sellButton,
                orderSide === 'sell' && styles.orderSideButtonActive
              ]}
              onPress={() => setOrderSide('sell')}
            >
              <Text style={[
                styles.orderSideButtonText,
                orderSide === 'sell' && styles.orderSideButtonTextActive
              ]}>
                SELL
              </Text>
            </TouchableOpacity>
          </View>

          {/* Order Type Selector */}
          <View style={styles.orderTypeSelector}>
            <TouchableOpacity
              style={[
                styles.orderTypeButton,
                orderType === 'market' && styles.orderTypeButtonActive
              ]}
              onPress={() => setOrderType('market')}
            >
              <Text style={styles.orderTypeButtonText}>Market</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[
                styles.orderTypeButton,
                orderType === 'limit' && styles.orderTypeButtonActive
              ]}
              onPress={() => setOrderType('limit')}
            >
              <Text style={styles.orderTypeButtonText}>Limit</Text>
            </TouchableOpacity>
          </View>

          {/* Quantity Input */}
          <View style={styles.inputGroup}>
            <Text style={styles.inputLabel}>Quantity</Text>
            <TextInput
              style={styles.input}
              value={orderQuantity}
              onChangeText={setOrderQuantity}
              placeholder="Enter quantity"
              placeholderTextColor="#666666"
              keyboardType="numeric"
            />
          </View>

          {/* Price Input (for limit orders) */}
          {orderType === 'limit' && (
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Limit Price</Text>
              <TextInput
                style={styles.input}
                value={orderPrice}
                onChangeText={setOrderPrice}
                placeholder="Enter price"
                placeholderTextColor="#666666"
                keyboardType="numeric"
              />
            </View>
          )}

          {/* Order Summary */}
          {orderQuantity && marketData[selectedSymbol] && (
            <View style={styles.orderSummary}>
              <Text style={styles.orderSummaryTitle}>Order Summary</Text>
              <View style={styles.orderSummaryRow}>
                <Text style={styles.orderSummaryLabel}>Estimated Total:</Text>
                <Text style={styles.orderSummaryValue}>
                  ${(
                    parseInt(orderQuantity || '0') * 
                    (orderType === 'limit' ? parseFloat(orderPrice || '0') : marketData[selectedSymbol].price)
                  ).toLocaleString()}
                </Text>
              </View>
            </View>
          )}

          {/* Submit Button */}
          <TouchableOpacity
            style={[
              styles.submitButton,
              orderSide === 'buy' ? styles.buySubmitButton : styles.sellSubmitButton
            ]}
            onPress={handlePlaceOrder}
          >
            <Text style={styles.submitButtonText}>
              {orderSide.toUpperCase()} {orderQuantity} {selectedSymbol}
            </Text>
          </TouchableOpacity>
        </View>
      </BlurView>
    </Animated.View>
  );

  return (
    <View style={styles.container}>
      {/* Main Content */}
      <View style={styles.mainContent}>
        {activeTab === 'trade' && (
          <>
            {renderChart()}
            <ScrollView style={styles.watchlist} showsVerticalScrollIndicator={false}>
              {watchlist.map(renderWatchlistItem)}
            </ScrollView>
          </>
        )}

        {activeTab === 'positions' && (
          <ScrollView style={styles.tabContent}>
            <Text style={styles.tabTitle}>Positions</Text>
            {positions.map((position, index) => (
              <View key={index} style={styles.positionItem}>
                <View style={styles.positionHeader}>
                  <Text style={styles.positionSymbol}>{position.symbol}</Text>
                  <Text style={[
                    styles.positionPnL,
                    { color: position.unrealizedPnL >= 0 ? '#00FF88' : '#FF6B6B' }
                  ]}>
                    {position.unrealizedPnL >= 0 ? '+' : ''}${position.unrealizedPnL.toFixed(2)}
                  </Text>
                </View>
                <View style={styles.positionDetails}>
                  <Text style={styles.positionDetail}>
                    {position.quantity} shares @ ${position.avgPrice.toFixed(2)}
                  </Text>
                  <Text style={styles.positionDetail}>
                    Current: ${position.currentPrice.toFixed(2)}
                  </Text>
                  <Text style={styles.positionDetail}>
                    Value: ${position.marketValue.toLocaleString()}
                  </Text>
                </View>
              </View>
            ))}
            {positions.length === 0 && (
              <Text style={styles.emptyMessage}>No positions</Text>
            )}
          </ScrollView>
        )}

        {activeTab === 'orders' && (
          <ScrollView style={styles.tabContent}>
            <Text style={styles.tabTitle}>Orders</Text>
            {orders.map((order, index) => (
              <View key={index} style={styles.orderItem}>
                <View style={styles.orderHeader}>
                  <Text style={styles.orderSymbol}>{order.symbol}</Text>
                  <View style={[
                    styles.orderStatus,
                    { backgroundColor: order.status === 'filled' ? '#00FF88' : '#FFA500' }
                  ]}>
                    <Text style={styles.orderStatusText}>{order.status}</Text>
                  </View>
                </View>
                <Text style={styles.orderDetails}>
                  {order.side.toUpperCase()} {order.quantity} @ ${order.price.toFixed(2)}
                </Text>
                <Text style={styles.orderTime}>
                  {order.timestamp.toLocaleTimeString()}
                </Text>
              </View>
            ))}
            {orders.length === 0 && (
              <Text style={styles.emptyMessage}>No orders</Text>
            )}
          </ScrollView>
        )}
      </View>

      {/* Bottom Navigation */}
      <View style={styles.bottomNav}>
        {[
          { key: 'trade', icon: 'trending-up', label: 'Trade' },
          { key: 'positions', icon: 'pie-chart', label: 'Positions' },
          { key: 'orders', icon: 'receipt', label: 'Orders' },
          { key: 'watchlist', icon: 'star', label: 'Watchlist' },
        ].map((tab) => (
          <TouchableOpacity
            key={tab.key}
            style={styles.tabButton}
            onPress={() => {
              setActiveTab(tab.key as any);
              Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
            }}
          >
            <Ionicons
              name={tab.icon as any}
              size={24}
              color={activeTab === tab.key ? '#007AFF' : '#666666'}
            />
            <Text style={[
              styles.tabLabel,
              { color: activeTab === tab.key ? '#007AFF' : '#666666' }
            ]}>
              {tab.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Floating Action Button */}
      {activeTab === 'trade' && (
        <TouchableOpacity style={styles.fab} onPress={toggleOrderForm}>
          <LinearGradient
            colors={['#007AFF', '#0051D5']}
            style={styles.fabGradient}
          >
            <Ionicons name="add" size={32} color="#FFFFFF" />
          </LinearGradient>
        </TouchableOpacity>
      )}

      {/* Order Form Modal */}
      {showOrderForm && renderOrderForm()}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000000',
  },
  mainContent: {
    flex: 1,
    paddingTop: 50,
  },
  // Chart styles
  chartContainer: {
    backgroundColor: '#111111',
    margin: 16,
    borderRadius: 12,
    padding: 16,
  },
  chartHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  chartSymbol: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  chartPrice: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginTop: 4,
  },
  timeframeSelector: {
    flexDirection: 'row',
    backgroundColor: '#222222',
    borderRadius: 8,
    padding: 4,
  },
  timeframeButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
  },
  timeframeButtonActive: {
    backgroundColor: '#007AFF',
  },
  timeframeText: {
    fontSize: 12,
    color: '#666666',
  },
  timeframeTextActive: {
    color: '#FFFFFF',
  },
  chart: {
    height: 250,
    marginVertical: 16,
  },
  marketStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    borderTopWidth: 1,
    borderTopColor: '#333333',
    paddingTop: 16,
  },
  statItem: {
    alignItems: 'center',
  },
  statLabel: {
    fontSize: 12,
    color: '#666666',
    marginBottom: 4,
  },
  statValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  // Watchlist styles
  watchlist: {
    flex: 1,
    paddingHorizontal: 16,
  },
  watchlistItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 16,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#222222',
    borderRadius: 8,
    marginBottom: 8,
  },
  watchlistItemSelected: {
    borderColor: '#007AFF',
    borderWidth: 1,
  },
  watchlistItemLeft: {
    flex: 1,
  },
  watchlistItemRight: {
    alignItems: 'flex-end',
  },
  symbolText: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  priceText: {
    fontSize: 16,
    marginTop: 4,
  },
  changeText: {
    fontSize: 14,
    fontWeight: '600',
  },
  changePercentText: {
    fontSize: 12,
    marginTop: 2,
  },
  // Tab content styles
  tabContent: {
    flex: 1,
    padding: 16,
  },
  tabTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 16,
  },
  emptyMessage: {
    fontSize: 16,
    color: '#666666',
    textAlign: 'center',
    marginTop: 50,
  },
  // Position styles
  positionItem: {
    backgroundColor: '#111111',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  positionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  positionSymbol: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  positionPnL: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  positionDetails: {
    gap: 4,
  },
  positionDetail: {
    fontSize: 14,
    color: '#AAAAAA',
  },
  // Order styles
  orderItem: {
    backgroundColor: '#111111',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  orderHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  orderSymbol: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  orderStatus: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  orderStatusText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#000000',
  },
  orderDetails: {
    fontSize: 14,
    color: '#AAAAAA',
    marginBottom: 4,
  },
  orderTime: {
    fontSize: 12,
    color: '#666666',
  },
  // Bottom navigation
  bottomNav: {
    flexDirection: 'row',
    backgroundColor: '#111111',
    borderTopWidth: 1,
    borderTopColor: '#333333',
    paddingBottom: 34, // Safe area
  },
  tabButton: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 12,
  },
  tabLabel: {
    fontSize: 12,
    marginTop: 4,
  },
  // FAB styles
  fab: {
    position: 'absolute',
    bottom: 100,
    right: 20,
    width: 64,
    height: 64,
    borderRadius: 32,
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  fabGradient: {
    width: 64,
    height: 64,
    borderRadius: 32,
    justifyContent: 'center',
    alignItems: 'center',
  },
  // Order form styles
  orderForm: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: SCREEN_HEIGHT * 0.7,
  },
  orderFormBlur: {
    flex: 1,
  },
  orderFormContent: {
    flex: 1,
    padding: 20,
    paddingBottom: 40,
  },
  orderFormHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  },
  orderFormTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  orderSideSelector: {
    flexDirection: 'row',
    marginBottom: 20,
  },
  orderSideButton: {
    flex: 1,
    paddingVertical: 16,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: 'transparent',
    alignItems: 'center',
    marginHorizontal: 4,
  },
  buyButton: {
    backgroundColor: '#00FF8820',
  },
  sellButton: {
    backgroundColor: '#FF6B6B20',
  },
  orderSideButtonActive: {
    borderColor: '#007AFF',
  },
  orderSideButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  orderSideButtonTextActive: {
    color: '#007AFF',
  },
  orderTypeSelector: {
    flexDirection: 'row',
    backgroundColor: '#222222',
    borderRadius: 8,
    padding: 4,
    marginBottom: 20,
  },
  orderTypeButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 6,
    alignItems: 'center',
  },
  orderTypeButtonActive: {
    backgroundColor: '#007AFF',
  },
  orderTypeButtonText: {
    fontSize: 14,
    color: '#FFFFFF',
  },
  inputGroup: {
    marginBottom: 16,
  },
  inputLabel: {
    fontSize: 14,
    color: '#AAAAAA',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#222222',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    color: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#333333',
  },
  orderSummary: {
    backgroundColor: '#111111',
    borderRadius: 8,
    padding: 16,
    marginVertical: 16,
  },
  orderSummaryTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 8,
  },
  orderSummaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  orderSummaryLabel: {
    fontSize: 14,
    color: '#AAAAAA',
  },
  orderSummaryValue: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  submitButton: {
    paddingVertical: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 20,
  },
  buySubmitButton: {
    backgroundColor: '#00FF88',
  },
  sellSubmitButton: {
    backgroundColor: '#FF6B6B',
  },
  submitButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
});

export default TradingInterface;