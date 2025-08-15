import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Dimensions,
} from 'react-native';
import { Card, Title, Paragraph, Chip } from 'react-native-paper';
import { LineChart, BarChart, PieChart } from 'react-native-chart-kit';

const screenWidth = Dimensions.get('window').width;

export default function AnalyticsScreen() {
  const [selectedTimeframe, setSelectedTimeframe] = useState('1D');

  const chartConfig = {
    backgroundGradientFrom: '#ffffff',
    backgroundGradientFromOpacity: 0,
    backgroundGradientTo: '#ffffff',
    backgroundGradientToOpacity: 0,
    color: (opacity = 1) => `rgba(25, 118, 210, ${opacity})`,
    strokeWidth: 2,
    barPercentage: 0.5,
    useShadowColorFromDataset: false,
  };

  const priceData = {
    labels: ['9AM', '12PM', '3PM', '6PM', '9PM'],
    datasets: [{
      data: [45000, 45200, 44800, 45100, 45300],
      strokeWidth: 3,
    }]
  };

  const volumeData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
    datasets: [{
      data: [120, 150, 180, 140, 200]
    }]
  };

  const portfolioData = [
    {
      name: 'BTC',
      population: 45,
      color: '#f39c12',
      legendFontColor: '#7F7F7F',
      legendFontSize: 15,
    },
    {
      name: 'ETH',
      population: 25,
      color: '#3498db',
      legendFontColor: '#7F7F7F',
      legendFontSize: 15,
    },
    {
      name: 'Stocks',
      population: 20,
      color: '#2ecc71',
      legendFontColor: '#7F7F7F',
      legendFontSize: 15,
    },
    {
      name: 'Cash',
      population: 10,
      color: '#95a5a6',
      legendFontColor: '#7F7F7F',
      legendFontSize: 15,
    },
  ];

  const timeframes = ['1H', '1D', '1W', '1M', '1Y'];

  const marketMetrics = [
    { label: 'Total Portfolio Value', value: '$125,430', change: '+2.4%', positive: true },
    { label: 'Today\'s P&L', value: '+$2,340', change: '+1.9%', positive: true },
    { label: 'Total Return', value: '+$15,430', change: '+14.1%', positive: true },
    { label: 'Win Rate', value: '68%', change: '+3%', positive: true },
  ];

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.metricsCard}>
        <Card.Content>
          <Title>Portfolio Metrics</Title>
          <View style={styles.metricsGrid}>
            {marketMetrics.map((metric, index) => (
              <View key={index} style={styles.metricItem}>
                <Text style={styles.metricLabel}>{metric.label}</Text>
                <Text style={styles.metricValue}>{metric.value}</Text>
                <Text style={[
                  styles.metricChange,
                  { color: metric.positive ? '#4caf50' : '#f44336' }
                ]}>
                  {metric.change}
                </Text>
              </View>
            ))}
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.chartCard}>
        <Card.Content>
          <View style={styles.chartHeader}>
            <Title>Price Chart</Title>
            <View style={styles.timeframeContainer}>
              {timeframes.map((timeframe) => (
                <Chip
                  key={timeframe}
                  selected={selectedTimeframe === timeframe}
                  onPress={() => setSelectedTimeframe(timeframe)}
                  style={styles.timeframeChip}
                  compact
                >
                  {timeframe}
                </Chip>
              ))}
            </View>
          </View>
          <LineChart
            data={priceData}
            width={screenWidth - 60}
            height={220}
            chartConfig={chartConfig}
            bezier
            style={styles.chart}
          />
        </Card.Content>
      </Card>

      <Card style={styles.chartCard}>
        <Card.Content>
          <Title>Trading Volume</Title>
          <BarChart
            data={volumeData}
            width={screenWidth - 60}
            height={220}
            chartConfig={chartConfig}
            style={styles.chart}
          />
        </Card.Content>
      </Card>

      <Card style={styles.chartCard}>
        <Card.Content>
          <Title>Portfolio Allocation</Title>
          <PieChart
            data={portfolioData}
            width={screenWidth - 60}
            height={220}
            chartConfig={chartConfig}
            accessor="population"
            backgroundColor="transparent"
            paddingLeft="15"
            style={styles.chart}
          />
        </Card.Content>
      </Card>

      <Card style={styles.insightsCard}>
        <Card.Content>
          <Title>AI Insights</Title>
          <View style={styles.insightItem}>
            <Text style={styles.insightTitle}>🚀 Bullish Signal</Text>
            <Paragraph>BTC showing strong momentum with RSI at 65. Consider increasing position.</Paragraph>
          </View>
          <View style={styles.insightItem}>
            <Text style={styles.insightTitle}>⚠️ Risk Alert</Text>
            <Paragraph>High volatility expected in tech stocks. Consider reducing exposure.</Paragraph>
          </View>
          <View style={styles.insightItem}>
            <Text style={styles.insightTitle}>💡 Opportunity</Text>
            <Paragraph>ETH/USD showing oversold conditions. Potential buying opportunity.</Paragraph>
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
    padding: 20,
  },
  metricsCard: {
    marginBottom: 20,
    elevation: 4,
  },
  chartCard: {
    marginBottom: 20,
    elevation: 4,
  },
  insightsCard: {
    elevation: 4,
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  metricItem: {
    width: '48%',
    marginBottom: 15,
  },
  metricLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 5,
  },
  metricValue: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 2,
  },
  metricChange: {
    fontSize: 12,
    fontWeight: 'bold',
  },
  chartHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  timeframeContainer: {
    flexDirection: 'row',
  },
  timeframeChip: {
    marginLeft: 4,
    height: 28,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  insightItem: {
    marginBottom: 15,
    paddingBottom: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  insightTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5,
  },
});