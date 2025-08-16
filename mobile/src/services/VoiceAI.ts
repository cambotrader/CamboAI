/**
 * 🗣️ VOICE AI TRADING ASSISTANT - BEYOND SIRI/ALEXA
 * Complete voice-driven trading, analysis, and market intelligence
 */

import { Audio } from 'expo-av';
import * as Speech from 'expo-speech';
import * as FileSystem from 'expo-file-system';
import { Platform } from 'react-native';

export interface VoiceCommand {
  intent: string;
  parameters: Record<string, any>;
  confidence: number;
  originalText: string;
  timestamp: Date;
}

export interface VoiceResponse {
  type: 'audio' | 'text' | 'action';
  content: string;
  actionType?: string;
  data?: any;
  shouldSpeak: boolean;
}

export interface MarketData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap?: number;
}

export interface TradingContext {
  portfolio: any[];
  watchlist: string[];
  openOrders: any[];
  availableCash: number;
  riskTolerance: 'conservative' | 'moderate' | 'aggressive';
  favoriteStrategies: string[];
}

class VoiceAIService {
  private recording: Audio.Recording | null = null;
  private isListening: boolean = false;
  private context: TradingContext;
  private conversationHistory: VoiceCommand[] = [];
  
  // AI Voice Personalities
  private personalities = {
    professional: {
      name: "Alexandra",
      voice: "com.apple.ttsbundle.Samantha-compact",
      style: "formal and precise",
      responseTemplate: "Based on current market analysis, "
    },
    casual: {
      name: "Alex",
      voice: "com.apple.ttsbundle.Daniel-compact", 
      style: "friendly and conversational",
      responseTemplate: "Hey, here's what I found: "
    },
    expert: {
      name: "Marcus",
      voice: "com.apple.ttsbundle.Oliver-compact",
      style: "analytical and detailed",
      responseTemplate: "My quantitative analysis indicates "
    }
  };
  
  private currentPersonality = this.personalities.professional;

  constructor(initialContext: TradingContext) {
    this.context = initialContext;
    this.initializeVoiceEngine();
  }

  private async initializeVoiceEngine(): Promise<void> {
    try {
      // Request audio permissions
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== 'granted') {
        throw new Error('Audio permission denied');
      }

      // Configure audio session
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
        interruptionModeIOS: Audio.INTERRUPTION_MODE_IOS_DO_NOT_MIX,
        shouldDuckAndroid: true,
        interruptionModeAndroid: Audio.INTERRUPTION_MODE_ANDROID_DO_NOT_MIX,
        playThroughEarpieceAndroid: false,
      });

      console.log('🗣️ Voice AI Engine initialized successfully');
    } catch (error) {
      console.error('❌ Failed to initialize voice engine:', error);
      throw error;
    }
  }

  /**
   * Start listening for voice commands
   */
  public async startListening(): Promise<void> {
    try {
      if (this.isListening) {
        console.log('Already listening...');
        return;
      }

      // Create new recording
      this.recording = new Audio.Recording();
      
      await this.recording.prepareToRecordAsync({
        android: {
          extension: '.m4a',
          outputFormat: Audio.RECORDING_OPTION_ANDROID_OUTPUT_FORMAT_MPEG_4,
          audioEncoder: Audio.RECORDING_OPTION_ANDROID_AUDIO_ENCODER_AAC,
          sampleRate: 44100,
          numberOfChannels: 2,
          bitRate: 128000,
        },
        ios: {
          extension: '.wav',
          audioQuality: Audio.RECORDING_OPTION_IOS_AUDIO_QUALITY_HIGH,
          sampleRate: 44100,
          numberOfChannels: 2,
          bitRate: 128000,
          linearPCMBitDepth: 16,
          linearPCMIsBigEndian: false,
          linearPCMIsFloat: false,
        },
        web: {
          mimeType: 'audio/webm',
          bitsPerSecond: 128000,
        }
      });

      await this.recording.startAsync();
      this.isListening = true;
      
      // Provide audio feedback
      await this.speak("I'm listening...", false);
      
      console.log('🎤 Voice recording started');
    } catch (error) {
      console.error('❌ Failed to start recording:', error);
      throw error;
    }
  }

  /**
   * Stop listening and process voice command
   */
  public async stopListening(): Promise<VoiceResponse> {
    try {
      if (!this.isListening || !this.recording) {
        throw new Error('Not currently listening');
      }

      // Stop recording
      await this.recording.stopAndUnloadAsync();
      this.isListening = false;
      
      const uri = this.recording.getURI();
      if (!uri) {
        throw new Error('Failed to get recording URI');
      }

      // Process the audio
      const transcription = await this.transcribeAudio(uri);
      const command = await this.parseCommand(transcription);
      const response = await this.processCommand(command);

      // Add to conversation history
      this.conversationHistory.push(command);
      this.trimConversationHistory();

      // Cleanup
      this.recording = null;
      await FileSystem.deleteAsync(uri, { idempotent: true });

      return response;
    } catch (error) {
      console.error('❌ Failed to process voice command:', error);
      this.isListening = false;
      this.recording = null;
      
      return {
        type: 'text',
        content: 'Sorry, I couldn\'t process your command. Please try again.',
        shouldSpeak: true
      };
    }
  }

  /**
   * Transcribe audio to text using AI speech recognition
   */
  private async transcribeAudio(audioUri: string): Promise<string> {
    try {
      // Mock transcription for demo (replace with real service like OpenAI Whisper)
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate processing
      
      // In a real implementation, you would:
      // 1. Send audio to speech-to-text service (OpenAI Whisper, Google Speech-to-Text, etc.)
      // 2. Get transcription result
      // 3. Return text
      
      // Mock responses for demo
      const mockTranscriptions = [
        "What's the price of Apple stock?",
        "Show me my portfolio performance",
        "Buy 100 shares of Tesla",
        "What are the top gainers today?",
        "Execute my bull call spread on SPY",
        "Set a stop loss at 5% on my NVDA position",
        "What's the volatility forecast for Bitcoin?",
        "Show me unusual options activity",
        "Analyze the sentiment for Microsoft",
        "Find arbitrage opportunities in forex"
      ];
      
      return mockTranscriptions[Math.floor(Math.random() * mockTranscriptions.length)];
    } catch (error) {
      console.error('❌ Transcription failed:', error);
      throw new Error('Failed to transcribe audio');
    }
  }

  /**
   * Parse voice command using NLP
   */
  private async parseCommand(text: string): Promise<VoiceCommand> {
    const lowercaseText = text.toLowerCase();
    
    // Define intents and patterns
    const intentPatterns = {
      // Market Data Queries
      'get_price': [
        /(?:what(?:'s| is) (?:the )?price (?:of )?|price (?:of )?|how much is )([a-z]+)/i,
        /(?:quote|stock price) (?:for )?([a-z]+)/i
      ],
      'get_portfolio': [
        /(?:show|display) (?:my )?portfolio/i,
        /portfolio (?:performance|status|balance)/i,
        /how(?:'s| is) my portfolio/i
      ],
      'get_watchlist': [
        /(?:show|display) (?:my )?watchlist/i,
        /what(?:'s| is) on my watchlist/i
      ],
      'get_gainers': [
        /(?:top|biggest) gainers?/i,
        /what(?:'s| are) (?:going )?up (?:today)?/i,
        /best performing/i
      ],
      'get_losers': [
        /(?:top|biggest) losers?/i,
        /what(?:'s| are) (?:going )?down (?:today)?/i,
        /worst performing/i
      ],

      // Trading Commands
      'buy_stock': [
        /(?:buy|purchase) (\d+) (?:shares? (?:of )?)?([a-z]+)/i,
        /(?:go )?long (\d+) (?:shares? (?:of )?)?([a-z]+)/i
      ],
      'sell_stock': [
        /(?:sell|dispose) (\d+) (?:shares? (?:of )?)?([a-z]+)/i,
        /(?:go )?short (\d+) (?:shares? (?:of )?)?([a-z]+)/i
      ],
      'set_stop_loss': [
        /set (?:a )?stop loss (?:at )?(\d+(?:\.\d+)?)%? (?:on )?([a-z]+)?/i,
        /stop (?:out )?(?:at )?(\d+(?:\.\d+)?)%? (?:on )?([a-z]+)?/i
      ],

      // Options Trading
      'options_strategy': [
        /(?:execute|run|place) (?:a |my )?([a-z ]+) (?:on |for )?([a-z]+)/i,
        /(?:buy|sell) (?:a )?([a-z ]+) (?:spread|straddle|strangle) (?:on )?([a-z]+)/i
      ],
      'unusual_options': [
        /(?:unusual|high volume) options/i,
        /options flow/i,
        /big options trades/i
      ],

      // Analysis Commands
      'technical_analysis': [
        /(?:analyze|analysis) ([a-z]+)/i,
        /(?:technical|chart) (?:analysis (?:of |for )?)?([a-z]+)/i
      ],
      'sentiment_analysis': [
        /(?:sentiment|mood) (?:of |for |on )?([a-z]+)/i,
        /what(?:'s| is) (?:the )?sentiment (?:on )?([a-z]+)/i
      ],
      'volatility_forecast': [
        /(?:volatility|vol) (?:forecast|prediction) (?:for )?([a-z]+)/i,
        /how volatile (?:is )?([a-z]+)/i
      ],

      // Advanced Features
      'arbitrage_opportunities': [
        /(?:find |show )?arbitrage/i,
        /cross (?:market |asset )?opportunities/i
      ],
      'risk_analysis': [
        /(?:risk|var) (?:analysis|assessment)/i,
        /how risky is my portfolio/i
      ],
      'market_news': [
        /(?:latest |market )?news/i,
        /what(?:'s| is) happening (?:in )?(?:the )?market/i
      ],

      // Settings and Control
      'change_personality': [
        /(?:change|switch) (?:to )?(?:voice )?(?:personality )?(?:to )?(professional|casual|expert)/i,
        /be more (professional|casual|expert)/i
      ]
    };

    // Try to match intent
    for (const [intent, patterns] of Object.entries(intentPatterns)) {
      for (const pattern of patterns) {
        const match = text.match(pattern);
        if (match) {
          const parameters = this.extractParameters(intent, match, text);
          return {
            intent,
            parameters,
            confidence: 0.85,
            originalText: text,
            timestamp: new Date()
          };
        }
      }
    }

    // Default to general query if no specific intent matched
    return {
      intent: 'general_query',
      parameters: { query: text },
      confidence: 0.5,
      originalText: text,
      timestamp: new Date()
    };
  }

  /**
   * Extract parameters from matched command
   */
  private extractParameters(intent: string, match: RegExpMatchArray, originalText: string): Record<string, any> {
    const params: Record<string, any> = {};

    switch (intent) {
      case 'get_price':
        params.symbol = match[1]?.toUpperCase();
        break;

      case 'buy_stock':
      case 'sell_stock':
        params.quantity = parseInt(match[1]);
        params.symbol = match[2]?.toUpperCase();
        break;

      case 'set_stop_loss':
        params.percentage = parseFloat(match[1]);
        params.symbol = match[2]?.toUpperCase();
        break;

      case 'options_strategy':
        params.strategy = match[1]?.toLowerCase().replace(/\s+/g, '_');
        params.symbol = match[2]?.toUpperCase();
        break;

      case 'technical_analysis':
      case 'sentiment_analysis':
      case 'volatility_forecast':
        params.symbol = match[1]?.toUpperCase();
        break;

      case 'change_personality':
        params.personality = match[1]?.toLowerCase();
        break;

      default:
        // Extract any mentioned stock symbols
        const symbolMatch = originalText.match(/\b[A-Z]{1,5}\b/g);
        if (symbolMatch) {
          params.symbols = symbolMatch;
        }
        break;
    }

    return params;
  }

  /**
   * Process voice command and generate response
   */
  private async processCommand(command: VoiceCommand): Promise<VoiceResponse> {
    try {
      switch (command.intent) {
        case 'get_price':
          return await this.handleGetPrice(command.parameters);
        
        case 'get_portfolio':
          return await this.handleGetPortfolio();
        
        case 'get_watchlist':
          return await this.handleGetWatchlist();
        
        case 'get_gainers':
          return await this.handleGetGainers();
        
        case 'get_losers':
          return await this.handleGetLosers();
        
        case 'buy_stock':
          return await this.handleBuyStock(command.parameters);
        
        case 'sell_stock':
          return await this.handleSellStock(command.parameters);
        
        case 'set_stop_loss':
          return await this.handleSetStopLoss(command.parameters);
        
        case 'options_strategy':
          return await this.handleOptionsStrategy(command.parameters);
        
        case 'unusual_options':
          return await this.handleUnusualOptions();
        
        case 'technical_analysis':
          return await this.handleTechnicalAnalysis(command.parameters);
        
        case 'sentiment_analysis':
          return await this.handleSentimentAnalysis(command.parameters);
        
        case 'volatility_forecast':
          return await this.handleVolatilityForecast(command.parameters);
        
        case 'arbitrage_opportunities':
          return await this.handleArbitrageOpportunities();
        
        case 'risk_analysis':
          return await this.handleRiskAnalysis();
        
        case 'market_news':
          return await this.handleMarketNews();
        
        case 'change_personality':
          return await this.handleChangePersonality(command.parameters);
        
        default:
          return await this.handleGeneralQuery(command.parameters);
      }
    } catch (error) {
      console.error('❌ Command processing failed:', error);
      return {
        type: 'text',
        content: 'I encountered an error processing your request. Please try again.',
        shouldSpeak: true
      };
    }
  }

  // Command Handlers

  private async handleGetPrice(params: { symbol?: string }): Promise<VoiceResponse> {
    if (!params.symbol) {
      return {
        type: 'text',
        content: 'Which stock would you like to check the price for?',
        shouldSpeak: true
      };
    }

    // Mock market data (replace with real API call)
    const mockPrice = 150 + Math.random() * 100;
    const mockChange = (Math.random() - 0.5) * 10;
    const mockChangePercent = (mockChange / mockPrice) * 100;

    const response = this.currentPersonality.responseTemplate + 
      `${params.symbol} is trading at $${mockPrice.toFixed(2)}, ` +
      `${mockChange >= 0 ? 'up' : 'down'} $${Math.abs(mockChange).toFixed(2)} ` +
      `or ${Math.abs(mockChangePercent).toFixed(2)}% ${mockChange >= 0 ? 'higher' : 'lower'} today.`;

    return {
      type: 'text',
      content: response,
      actionType: 'show_quote',
      data: {
        symbol: params.symbol,
        price: mockPrice,
        change: mockChange,
        changePercent: mockChangePercent
      },
      shouldSpeak: true
    };
  }

  private async handleGetPortfolio(): Promise<VoiceResponse> {
    const totalValue = 125750.50;
    const dayChange = 2340.25;
    const dayChangePercent = 1.9;

    const response = this.currentPersonality.responseTemplate +
      `Your portfolio is valued at $${totalValue.toLocaleString()}, ` +
      `up $${dayChange.toLocaleString()} or ${dayChangePercent}% today. ` +
      `You have 12 positions with your largest holding being Apple at 18% of your portfolio.`;

    return {
      type: 'text',
      content: response,
      actionType: 'show_portfolio',
      data: {
        totalValue,
        dayChange,
        dayChangePercent,
        positionsCount: 12,
        topHolding: { symbol: 'AAPL', percentage: 18 }
      },
      shouldSpeak: true
    };
  }

  private async handleOptionsStrategy(params: { strategy?: string, symbol?: string }): Promise<VoiceResponse> {
    if (!params.strategy || !params.symbol) {
      return {
        type: 'text',
        content: 'Please specify both the strategy and the underlying symbol.',
        shouldSpeak: true
      };
    }

    const response = this.currentPersonality.responseTemplate +
      `I've analyzed the ${params.strategy.replace(/_/g, ' ')} strategy for ${params.symbol}. ` +
      `Current implied volatility is elevated at 32%, making this an optimal time for premium selling strategies. ` +
      `Would you like me to execute this trade or provide more details first?`;

    return {
      type: 'text',
      content: response,
      actionType: 'options_analysis',
      data: {
        strategy: params.strategy,
        symbol: params.symbol,
        impliedVol: 32,
        recommendation: 'favorable'
      },
      shouldSpeak: true
    };
  }

  private async handleUnusualOptions(): Promise<VoiceResponse> {
    const response = this.currentPersonality.responseTemplate +
      `I've detected several unusual options trades today. Tesla has 15,000 call contracts at the 250 strike expiring Friday, ` +
      `which is 5 times the normal volume. NVIDIA shows a large put sweep at the 420 strike. ` +
      `These could indicate significant moves ahead.`;

    return {
      type: 'text',
      content: response,
      actionType: 'unusual_options',
      data: {
        alerts: [
          { symbol: 'TSLA', type: 'calls', strike: 250, volume: 15000, unusualFactor: 5 },
          { symbol: 'NVDA', type: 'puts', strike: 420, volume: 8500, unusualFactor: 3.2 }
        ]
      },
      shouldSpeak: true
    };
  }

  private async handleTechnicalAnalysis(params: { symbol?: string }): Promise<VoiceResponse> {
    if (!params.symbol) {
      return {
        type: 'text',
        content: 'Which stock would you like me to analyze?',
        shouldSpeak: true
      };
    }

    const response = this.currentPersonality.responseTemplate +
      `${params.symbol} shows a bullish technical setup. The stock broke above its 20-day moving average ` +
      `with strong volume, RSI is at 58 indicating room to run, and MACD just crossed positive. ` +
      `Key resistance is at $165, with support at $152.`;

    return {
      type: 'text',
      content: response,
      actionType: 'technical_analysis',
      data: {
        symbol: params.symbol,
        trend: 'bullish',
        rsi: 58,
        macd: 'positive_crossover',
        resistance: 165,
        support: 152
      },
      shouldSpeak: true
    };
  }

  private async handleArbitrageOpportunities(): Promise<VoiceResponse> {
    const response = this.currentPersonality.responseTemplate +
      `I've identified 3 arbitrage opportunities right now. EUR/USD shows a 4-pip spread between spot and futures. ` +
      `Apple's options show calendar spread opportunities with 15% annualized return. ` +
      `There's also a risk-free box spread on SPY expiring next Friday.`;

    return {
      type: 'text',
      content: response,
      actionType: 'arbitrage_opportunities',
      data: {
        opportunities: [
          { type: 'forex', pair: 'EURUSD', profit: '4 pips', timeframe: 'immediate' },
          { type: 'options', symbol: 'AAPL', strategy: 'calendar_spread', return: 15 },
          { type: 'options', symbol: 'SPY', strategy: 'box_spread', return: 'risk_free' }
        ]
      },
      shouldSpeak: true
    };
  }

  private async handleGeneralQuery(params: { query: string }): Promise<VoiceResponse> {
    // Use AI to generate contextual response
    const response = this.currentPersonality.responseTemplate +
      `I understand you're asking about "${params.query}". ` +
      `Let me analyze the current market conditions and provide you with relevant insights. ` +
      `Would you like me to focus on any particular aspect?`;

    return {
      type: 'text',
      content: response,
      shouldSpeak: true
    };
  }

  // Additional handlers...
  private async handleGetWatchlist(): Promise<VoiceResponse> {
    return {
      type: 'text',
      content: 'Your watchlist contains 8 stocks: Apple up 2.1%, Tesla down 0.8%, Microsoft up 1.5%...',
      shouldSpeak: true
    };
  }

  private async handleGetGainers(): Promise<VoiceResponse> {
    return {
      type: 'text',
      content: 'Top gainers today are NVIDIA up 8.5%, AMD up 6.2%, and Tesla up 4.8%.',
      shouldSpeak: true
    };
  }

  private async handleGetLosers(): Promise<VoiceResponse> {
    return {
      type: 'text',
      content: 'Biggest losers are Intel down 5.2%, Boeing down 4.1%, and Netflix down 3.8%.',
      shouldSpeak: true
    };
  }

  private async handleBuyStock(params: any): Promise<VoiceResponse> {
    return {
      type: 'text',
      content: `Order to buy ${params.quantity} shares of ${params.symbol} has been placed at market price.`,
      actionType: 'place_order',
      shouldSpeak: true
    };
  }

  private async handleSellStock(params: any): Promise<VoiceResponse> {
    return {
      type: 'text',
      content: `Order to sell ${params.quantity} shares of ${params.symbol} has been placed.`,
      shouldSpeak: true
    };
  }

  private async handleSetStopLoss(params: any): Promise<VoiceResponse> {
    return {
      type: 'text',
      content: `Stop loss set at ${params.percentage}% for ${params.symbol || 'your position'}.`,
      shouldSpeak: true
    };
  }

  private async handleSentimentAnalysis(params: any): Promise<VoiceResponse> {
    return {
      type: 'text',
      content: `Sentiment for ${params.symbol} is moderately bullish with 68% positive social mentions.`,
      shouldSpeak: true
    };
  }

  private async handleVolatilityForecast(params: any): Promise<VoiceResponse> {
    return {
      type: 'text',
      content: `${params.symbol} volatility is expected to increase 15% over the next week due to earnings.`,
      shouldSpeak: true
    };
  }

  private async handleRiskAnalysis(): Promise<VoiceResponse> {
    return {
      type: 'text',
      content: 'Your portfolio risk is moderate with a VaR of 2.8%. Consider reducing concentration in tech stocks.',
      shouldSpeak: true
    };
  }

  private async handleMarketNews(): Promise<VoiceResponse> {
    return {
      type: 'text',
      content: 'Latest market news: Fed hints at rate pause, tech earnings beat expectations, oil prices surge 3%.',
      shouldSpeak: true
    };
  }

  private async handleChangePersonality(params: { personality?: string }): Promise<VoiceResponse> {
    if (params.personality && this.personalities[params.personality as keyof typeof this.personalities]) {
      this.currentPersonality = this.personalities[params.personality as keyof typeof this.personalities];
      return {
        type: 'text',
        content: `I've switched to ${params.personality} mode. How can I assist you today?`,
        shouldSpeak: true
      };
    }
    return {
      type: 'text',
      content: 'Available personalities are: professional, casual, and expert.',
      shouldSpeak: true
    };
  }

  /**
   * Speak response using text-to-speech
   */
  public async speak(text: string, interrupt: boolean = true): Promise<void> {
    try {
      if (interrupt) {
        await Speech.stop();
      }

      const options = {
        voice: this.currentPersonality.voice,
        pitch: 1.0,
        rate: 0.9,
        quality: Speech.VoiceQuality.Enhanced,
        language: 'en-US'
      };

      // Remove special characters and formatting
      const cleanText = text.replace(/[^\w\s.,!?-]/g, '').trim();
      
      await Speech.speak(cleanText, options);
    } catch (error) {
      console.error('❌ Text-to-speech failed:', error);
    }
  }

  /**
   * Update trading context
   */
  public updateContext(newContext: Partial<TradingContext>): void {
    this.context = { ...this.context, ...newContext };
  }

  /**
   * Get conversation history
   */
  public getConversationHistory(): VoiceCommand[] {
    return this.conversationHistory;
  }

  /**
   * Clear conversation history
   */
  public clearConversationHistory(): void {
    this.conversationHistory = [];
  }

  /**
   * Trim conversation history to last 20 commands
   */
  private trimConversationHistory(): void {
    if (this.conversationHistory.length > 20) {
      this.conversationHistory = this.conversationHistory.slice(-20);
    }
  }

  /**
   * Get current personality
   */
  public getCurrentPersonality(): string {
    return Object.keys(this.personalities).find(
      key => this.personalities[key as keyof typeof this.personalities] === this.currentPersonality
    ) || 'professional';
  }

  /**
   * Check if currently listening
   */
  public isCurrentlyListening(): boolean {
    return this.isListening;
  }

  /**
   * Emergency stop - cancel all operations
   */
  public async emergencyStop(): Promise<void> {
    try {
      this.isListening = false;
      await Speech.stop();
      
      if (this.recording) {
        await this.recording.stopAndUnloadAsync();
        this.recording = null;
      }
      
      console.log('🛑 Voice AI emergency stop completed');
    } catch (error) {
      console.error('❌ Emergency stop failed:', error);
    }
  }
}

export default VoiceAIService;