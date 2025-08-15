import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import { Card, Title, Paragraph, Button } from 'react-native-paper';
import { LineChart } from 'react-native-chart-kit';
import { LinearGradient } from 'expo-linear-gradient';
import { apiService, MarketData } from '../services/apiService';

const screenWidth = Dimensions.get('window').width;

export default function HomeScreen({ navigation }: any) {
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [chartData, setChartData] = useState({
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [{
      data: [20, 45, 28, 80, 99, 43],
      strokeWidth: 2,
    }]
  });

  useEffect(() => {
    fetchMarketData();
  }, []);

  const fetchMarketData = async () => {
    try {
      // Use your actual CamboAI backend API service
      const data = await apiService.getMarketOverview();
      setMarketData(data);
    } catch (error) {
      console.log('Error fetching market data:', error);
      // Fallback to mock data for demo
      setMarketData([
        { symbol: 'BTC/USD', price: 45000, change: 1200, changePercent: 2.74 },
        { symbol: 'ETH/USD', price: 3200, change: -50, changePercent: -1.54 },
        { symbol: 'AAPL', price: 175, change: 2.5, changePercent: 1.45 },
        { symbol: 'GOOGL', price: 2800, change: -25, changePercent: -0.89 },
        { symbol: 'TSLA', price: 250, change: 15, changePercent: 6.38 },
      ]);
    }
  };

  const chartConfig = {
    backgroundGradientFrom: '#1E2923',
    backgroundGradientFromOpacity: 0,
    backgroundGradientTo: '#08130D',
    backgroundGradientToOpacity: 0.5,
    color: (opacity = 1) => `rgba(26, 255, 146, ${opacity})`,
    strokeWidth: 2,
    barPercentage: 0.5,
    useShadowColorFromDataset: false,
  };

  return (
    <ScrollView style={styles.container}>
      <LinearGradient
        colors={['#1976d2', '#42a5f5']}
        style={styles.header}
      >
        <Text style={styles.headerTitle}>Welcome to CamboStation</Text>
        <Text style={styles.headerSubtitle}>AI-Powered Trading Intelligence</Text>
      </LinearGradient>

      <View style={styles.content}>
        <Card style={styles.chartCard}>
          <Card.Content>
            <Title>Portfolio Performance</Title>
            <LineChart
              data={chartData}
              width={screenWidth - 60}
              height={220}
              chartConfig={chartConfig}
              bezier
              style={styles.chart}
            />
          </Card.Content>
        </Card>

        <Text style={styles.sectionTitle}>Market Overview</Text>
        {marketData.map((item, index) => (
          <Card key={index} style={styles.marketCard}>
            <Card.Content>
              <View style={styles.marketRow}>
                <View>
                  <Title style={styles.symbol}>{item.symbol}</Title>
                  <Paragraph style={styles.price}>${item.price.toLocaleString()}</Paragraph>
                </View>
                <View style={styles.changeContainer}>
                  <Text style={[
                    styles.change,
                    { color: item.change >= 0 ? '#4caf50' : '#f44336' }
                  ]}>
                    {item.change >= 0 ? '+' : ''}{item.change.toFixed(2)}
                  </Text>
                  <Text style={[
                    styles.changePercent,
                    { color: item.changePercent >= 0 ? '#4caf50' : '#f44336' }
                  ]}>
                    ({item.changePercent >= 0 ? '+' : ''}{item.changePercent.toFixed(2)}%)
                  </Text>
                </View>
              </View>
            </Card.Content>
          </Card>
        ))}

        <View style={styles.buttonContainer}>
          <Button
            mode="contained"
            onPress={() => navigation.navigate('Trading')}
            style={styles.navButton}
          >
            Trading Dashboard
          </Button>
          <Button
            mode="contained"
            onPress={() => navigation.navigate('Analytics')}
            style={styles.navButton}
          >
            Market Analytics
          </Button>
          <Button
            mode="contained"
            onPress={() => navigation.navigate('Portfolio')}
            style={styles.navButton}
          >
            Portfolio
          </Button>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 30,
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 5,
  },
  headerSubtitle: {
    fontSize: 16,
    color: 'white',
    opacity: 0.9,
  },
  content: {
    padding: 20,
  },
  chartCard: {
    marginBottom: 20,
    elevation: 4,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  marketCard: {
    marginBottom: 10,
    elevation: 2,
  },
  marketRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  symbol: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  price: {
    fontSize: 14,
    color: '#666',
  },
  changeContainer: {
    alignItems: 'flex-end',
  },
  change: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  changePercent: {
    fontSize: 12,
  },
  buttonContainer: {
    marginTop: 30,
  },
  navButton: {
    marginBottom: 10,
  },
});