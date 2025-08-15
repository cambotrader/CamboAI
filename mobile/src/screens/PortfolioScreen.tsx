import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { Card, Title, Paragraph, Chip, Button } from 'react-native-paper';
import { LinearGradient } from 'expo-linear-gradient';
import { apiService, Position, Portfolio } from '../services/apiService';

export default function PortfolioScreen() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [totalValue, setTotalValue] = useState(0);
  const [totalPnL, setTotalPnL] = useState(0);

  useEffect(() => {
    fetchPortfolio();
  }, []);

  const fetchPortfolio = async () => {
    try {
      // Use your actual CamboAI backend API service
      const portfolio = await apiService.getPortfolio();
      setPositions(portfolio.positions);
      setTotalValue(portfolio.totalValue);
      setTotalPnL(portfolio.totalPnL);
    } catch (error) {
      console.log('Error fetching portfolio:', error);
      // Mock data for demo
      const mockPositions: Position[] = [
        {
          symbol: 'BTC',
          quantity: 0.5,
          avgPrice: 42000,
          currentPrice: 45000,
          value: 22500,
          pnl: 1500,
          pnlPercent: 7.14,
        },
        {
          symbol: 'ETH',
          quantity: 10,
          avgPrice: 3000,
          currentPrice: 3200,
          value: 32000,
          pnl: 2000,
          pnlPercent: 6.67,
        },
        {
          symbol: 'AAPL',
          quantity: 50,
          avgPrice: 170,
          currentPrice: 175,
          value: 8750,
          pnl: 250,
          pnlPercent: 2.94,
        },
        {
          symbol: 'GOOGL',
          quantity: 20,
          avgPrice: 2800,
          currentPrice: 2750,
          value: 55000,
          pnl: -1000,
          pnlPercent: -1.79,
        },
      ];

      setPositions(mockPositions);
      
      const total = mockPositions.reduce((sum, pos) => sum + pos.value, 0);
      const totalPnL = mockPositions.reduce((sum, pos) => sum + pos.pnl, 0);
      
      setTotalValue(total);
      setTotalPnL(totalPnL);
    }
  };

  const totalPnLPercent = totalValue > 0 ? (totalPnL / (totalValue - totalPnL)) * 100 : 0;

  return (
    <ScrollView style={styles.container}>
      <LinearGradient
        colors={totalPnL >= 0 ? ['#4caf50', '#66bb6a'] : ['#f44336', '#ef5350']}
        style={styles.summaryCard}
      >
        <Text style={styles.summaryTitle}>Total Portfolio Value</Text>
        <Text style={styles.summaryValue}>${totalValue.toLocaleString()}</Text>
        <View style={styles.pnlContainer}>
          <Text style={styles.pnlLabel}>Total P&L:</Text>
          <Text style={styles.pnlValue}>
            {totalPnL >= 0 ? '+' : ''}${totalPnL.toLocaleString()} ({totalPnLPercent >= 0 ? '+' : ''}{totalPnLPercent.toFixed(2)}%)
          </Text>
        </View>
      </LinearGradient>

      <View style={styles.positionsContainer}>
        <Text style={styles.sectionTitle}>Positions</Text>
        {positions.map((position, index) => (
          <Card key={index} style={styles.positionCard}>
            <Card.Content>
              <View style={styles.positionHeader}>
                <View>
                  <Title style={styles.symbol}>{position.symbol}</Title>
                  <Paragraph style={styles.quantity}>
                    {position.quantity} shares
                  </Paragraph>
                </View>
                <View style={styles.valueContainer}>
                  <Text style={styles.currentValue}>
                    ${position.value.toLocaleString()}
                  </Text>
                  <Chip
                    style={[
                      styles.pnlChip,
                      { backgroundColor: position.pnl >= 0 ? '#e8f5e8' : '#ffeaea' }
                    ]}
                  >
                    <Text style={{
                      color: position.pnl >= 0 ? '#4caf50' : '#f44336',
                      fontWeight: 'bold'
                    }}>
                      {position.pnl >= 0 ? '+' : ''}${position.pnl.toLocaleString()}
                    </Text>
                  </Chip>
                </View>
              </View>
              
              <View style={styles.priceInfo}>
                <View style={styles.priceItem}>
                  <Text style={styles.priceLabel}>Avg Price</Text>
                  <Text style={styles.priceValue}>${position.avgPrice.toLocaleString()}</Text>
                </View>
                <View style={styles.priceItem}>
                  <Text style={styles.priceLabel}>Current Price</Text>
                  <Text style={styles.priceValue}>${position.currentPrice.toLocaleString()}</Text>
                </View>
                <View style={styles.priceItem}>
                  <Text style={styles.priceLabel}>Return</Text>
                  <Text style={[
                    styles.priceValue,
                    { color: position.pnlPercent >= 0 ? '#4caf50' : '#f44336' }
                  ]}>
                    {position.pnlPercent >= 0 ? '+' : ''}{position.pnlPercent.toFixed(2)}%
                  </Text>
                </View>
              </View>

              <View style={styles.actionButtons}>
                <Button
                  mode="outlined"
                  onPress={() => {}}
                  style={styles.actionButton}
                  compact
                >
                  Buy More
                </Button>
                <Button
                  mode="outlined"
                  onPress={() => {}}
                  style={styles.actionButton}
                  compact
                >
                  Sell
                </Button>
              </View>
            </Card.Content>
          </Card>
        ))}
      </View>

      <Card style={styles.performanceCard}>
        <Card.Content>
          <Title>Performance Summary</Title>
          <View style={styles.performanceGrid}>
            <View style={styles.performanceItem}>
              <Text style={styles.performanceLabel}>Best Performer</Text>
              <Text style={styles.performanceValue}>BTC (+7.14%)</Text>
            </View>
            <View style={styles.performanceItem}>
              <Text style={styles.performanceLabel}>Worst Performer</Text>
              <Text style={styles.performanceValue}>GOOGL (-1.79%)</Text>
            </View>
            <View style={styles.performanceItem}>
              <Text style={styles.performanceLabel}>Largest Position</Text>
              <Text style={styles.performanceValue}>GOOGL (46.6%)</Text>
            </View>
            <View style={styles.performanceItem}>
              <Text style={styles.performanceLabel}>Cash Available</Text>
              <Text style={styles.performanceValue}>$5,000</Text>
            </View>
          </View>
        </Card.Content>
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  summaryCard: {
    padding: 30,
    alignItems: 'center',
    margin: 20,
    borderRadius: 15,
  },
  summaryTitle: {
    fontSize: 16,
    color: 'white',
    opacity: 0.9,
    marginBottom: 10,
  },
  summaryValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 15,
  },
  pnlContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  pnlLabel: {
    fontSize: 14,
    color: 'white',
    opacity: 0.9,
    marginRight: 10,
  },
  pnlValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: 'white',
  },
  positionsContainer: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  positionCard: {
    marginBottom: 15,
    elevation: 4,
  },
  positionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 15,
  },
  symbol: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  quantity: {
    fontSize: 14,
    color: '#666',
  },
  valueContainer: {
    alignItems: 'flex-end',
  },
  currentValue: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  pnlChip: {
    height: 24,
  },
  priceInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  priceItem: {
    alignItems: 'center',
  },
  priceLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 5,
  },
  priceValue: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  actionButton: {
    flex: 0.4,
  },
  performanceCard: {
    margin: 20,
    elevation: 4,
  },
  performanceGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  performanceItem: {
    width: '48%',
    marginBottom: 15,
  },
  performanceLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 5,
  },
  performanceValue: {
    fontSize: 14,
    fontWeight: 'bold',
  },
});