import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { Provider as PaperProvider } from 'react-native-paper';
import { StatusBar } from 'expo-status-bar';

// Import screens
import HomeScreen from './src/screens/HomeScreen';
import TradingScreen from './src/screens/TradingScreen';
import AnalyticsScreen from './src/screens/AnalyticsScreen';
import PortfolioScreen from './src/screens/PortfolioScreen';

const Stack = createStackNavigator();

export default function App() {
  return (
    <PaperProvider>
      <NavigationContainer>
        <Stack.Navigator
          initialRouteName="Home"
          screenOptions={{
            headerStyle: {
              backgroundColor: '#1976d2',
            },
            headerTintColor: '#fff',
            headerTitleStyle: {
              fontWeight: 'bold',
            },
          }}
        >
          <Stack.Screen 
            name="Home" 
            component={HomeScreen} 
            options={{ title: 'CamboStation Vision' }}
          />
          <Stack.Screen 
            name="Trading" 
            component={TradingScreen} 
            options={{ title: 'Trading Dashboard' }}
          />
          <Stack.Screen 
            name="Analytics" 
            component={AnalyticsScreen} 
            options={{ title: 'Market Analytics' }}
          />
          <Stack.Screen 
            name="Portfolio" 
            component={PortfolioScreen} 
            options={{ title: 'Portfolio' }}
          />
        </Stack.Navigator>
        <StatusBar style="light" />
      </NavigationContainer>
    </PaperProvider>
  );
}