import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { Card, Title, Button, TextInput, Chip } from 'react-native-paper';
import { apiService, Trade } from '../services/apiService';

export default function TradingScreen() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState('BTC/USD');
  const [amount, setAmount] = useState('');
  const [price, setPrice] = useState('');

  useEffect(() => {
    fetchTrades();
  }, []);

  const fetchTrades = async () => {
    try {
      // Use your actual CamboAI backend API service
      const data = await apiService.getTrades();
      setTrades(data);
    } catch (error) {
      console.log('Error fetching trades:', error);
      // Mock data for demo
      setTrades([
        {
          id: '1',
          symbol: 'BTC/USD',
          type: 'buy',
          amount: 0.1,
          price: 45000,
          timestamp: new Date().toISOString(),
        },
        {
          id: '2',
          symbol: 'ETH/USD',
          type: 'sell',
          amount: 2.5,
          price: 3200,
          timestamp: new Date().toISOString(),
        },
      ]);
    }
  };

  const executeTrade = async (type: 'buy' | 'sell') => {
    if (!amount || !price) {
      Alert.alert('Error', 'Please enter amount and price');
      return;
    }

    try {
      const tradeData = {
        symbol: selectedSymbol,
        type,
        amount: parseFloat(amount),
        price: parseFloat(price),
      };

      // Use your actual CamboAI backend API service
      await apiService.placeOrder(tradeData);
      
      Alert.alert('Success', `${type.toUpperCase()} order placed successfully!`);
      setAmount('');
      setPrice('');
      fetchTrades();
    } catch (error) {
      Alert.alert('Error', 'Failed to place order');
      console.log('Trade error:', error);
    }
  };

  const symbols = ['BTC/USD', 'ETH/USD', 'AAPL', 'GOOGL', 'TSLA'];

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.tradingCard}>
        <Card.Content>
          <Title>Place Order</Title>
          
          <Text style={styles.label}>Select Symbol</Text>
          <View style={styles.symbolContainer}>
            {symbols.map((symbol) => (
              <Chip
                key={symbol}
                selected={selectedSymbol === symbol}
                onPress={() => setSelectedSymbol(symbol)}
                style={styles.symbolChip}
              >
                {symbol}
              </Chip>
            ))}
          </View>

          <TextInput
            label="Amount"
            value={amount}
            onChangeText={setAmount}
            keyboardType="numeric"
            style={styles.input}
          />

          <TextInput
            label="Price"
            value={price}
            onChangeText={setPrice}
            keyboardType="numeric"
            style={styles.input}
          />

          <View style={styles.buttonRow}>
            <Button
              mode="contained"
              onPress={() => executeTrade('buy')}
              style={[styles.tradeButton, styles.buyButton]}
            >
              BUY
            </Button>
            <Button
              mode="contained"
              onPress={() => executeTrade('sell')}
              style={[styles.tradeButton, styles.sellButton]}
            >
              SELL
            </Button>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.historyCard}>
        <Card.Content>
          <Title>Recent Trades</Title>
          {trades.map((trade) => (
            <View key={trade.id} style={styles.tradeItem}>
              <View style={styles.tradeHeader}>
                <Text style={styles.tradeSymbol}>{trade.symbol}</Text>
                <Chip
                  style={[
                    styles.tradeTypeChip,
                    trade.type === 'buy' ? styles.buyChip : styles.sellChip
                  ]}
                >
                  {trade.type.toUpperCase()}
                </Chip>
              </View>
              <Text style={styles.tradeDetails}>
                Amount: {trade.amount} | Price: ${trade.price.toLocaleString()}
              </Text>
              <Text style={styles.tradeTime}>
                {new Date(trade.timestamp).toLocaleString()}
              </Text>
            </View>
          ))}
        </Card.Content>
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 20,
  },
  tradingCard: {
    marginBottom: 20,
    elevation: 4,
  },
  historyCard: {
    elevation: 4,
  },
  label: {
    fontSize: 16,
    fontWeight: 'bold',
    marginTop: 15,
    marginBottom: 10,
  },
  symbolContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 15,
  },
  symbolChip: {
    margin: 4,
  },
  input: {
    marginBottom: 15,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 20,
  },
  tradeButton: {
    flex: 0.45,
  },
  buyButton: {
    backgroundColor: '#4caf50',
  },
  sellButton: {
    backgroundColor: '#f44336',
  },
  tradeItem: {
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
    paddingVertical: 15,
  },
  tradeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 5,
  },
  tradeSymbol: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  tradeTypeChip: {
    height: 24,
  },
  buyChip: {
    backgroundColor: '#e8f5e8',
  },
  sellChip: {
    backgroundColor: '#ffeaea',
  },
  tradeDetails: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
  },
  tradeTime: {
    fontSize: 12,
    color: '#999',
  },
});