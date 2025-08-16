"use client";
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';

type NewsArticle = {
  title: string;
  description: string;
  url: string;
  source: string;
  published_at: string;
  sentiment_score: number;
  sentiment_label: 'bullish' | 'bearish' | 'neutral';
  confidence: number;
  emoji: string;
  timestamp_relative: string;
};

type SentimentSummary = {
  overall_mood: string;
  sentiment_distribution: {
    bullish: string;
    bearish: string;
    neutral: string;
  };
  market_tone: string;
  top_themes: string[];
};

export default function NewsPage() {
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [summary, setSummary] = useState<SentimentSummary | null>(null);
  const [marketMood, setMarketMood] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [symbolFilter, setSymbolFilter] = useState('');
  const [customText, setCustomText] = useState('');
  const [textAnalysis, setTextAnalysis] = useState<any>(null);

  useEffect(() => {
    loadNews();
    loadMarketMood();
  }, []);

  const loadNews = async (symbol?: string) => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (symbol) params.append('symbol', symbol);
      params.append('limit', '15');
      params.append('hours', '24');

      const response = await fetch(`/api/news/sentiment?${params}`);
      if (response.ok) {
        const data = await response.json();
        setArticles(data.articles);
        setSummary(data.summary);
      }
    } catch (error) {
      console.error('Failed to load news:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMarketMood = async () => {
    try {
      const response = await fetch('/api/news/market-mood');
      if (response.ok) {
        const data = await response.json();
        setMarketMood(data);
      }
    } catch (error) {
      console.error('Failed to load market mood:', error);
    }
  };

  const analyzeCustomText = async () => {
    if (!customText.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch('/api/news/analyze-text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: customText })
      });
      
      if (response.ok) {
        const data = await response.json();
        setTextAnalysis(data);
      }
    } catch (error) {
      console.error('Failed to analyze text:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSymbolFilter = () => {
    loadNews(symbolFilter || undefined);
  };

  const getSentimentColor = (label: string) => {
    switch (label) {
      case 'bullish': return 'text-green-600 bg-green-50 border-green-200';
      case 'bearish': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getSentimentBadgeVariant = (label: string) => {
    switch (label) {
      case 'bullish': return 'default' as const;
      case 'bearish': return 'destructive' as const;  
      default: return 'secondary' as const;
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">📰 News & Sentiment</h1>
        <Button onClick={loadMarketMood} disabled={loading}>
          🔄 Refresh Mood
        </Button>
      </div>

      {/* Market Mood Overview */}
      {marketMood && (
        <Card className="border-blue-200 bg-gradient-to-r from-blue-50 to-purple-50">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold">{marketMood.mood}</h2>
                <p className="text-blue-700 mt-1">{marketMood.description}</p>
                <div className="flex space-x-4 mt-3 text-sm">
                  <span className="text-green-600">
                    🟢 Bullish: {marketMood.bullish_percentage.toFixed(0)}%
                  </span>
                  <span className="text-red-600">
                    🔴 Bearish: {marketMood.bearish_percentage.toFixed(0)}%
                  </span>
                </div>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-blue-600">
                  {marketMood.score > 0 ? '+' : ''}{(marketMood.score * 100).toFixed(1)}
                </div>
                <div className="text-sm text-blue-500">Sentiment Score</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* News Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Filter News</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex space-x-2">
              <Input
                placeholder="Enter symbol (e.g., AAPL, TECH)"
                value={symbolFilter}
                onChange={(e) => setSymbolFilter(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSymbolFilter()}
              />
              <Button onClick={handleSymbolFilter} disabled={loading}>
                {loading ? 'Loading...' : 'Filter'}
              </Button>
              <Button variant="outline" onClick={() => { setSymbolFilter(''); loadNews(); }}>
                Clear
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Analyze Custom Text</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Input
                placeholder="Enter headline or text to analyze..."
                value={customText}
                onChange={(e) => setCustomText(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && analyzeCustomText()}
              />
              <Button onClick={analyzeCustomText} disabled={loading || !customText.trim()} className="w-full">
                🧠 Analyze Sentiment
              </Button>
              {textAnalysis && (
                <div className={`p-3 border rounded ${getSentimentColor(textAnalysis.sentiment_label)}`}>
                  <div className="flex items-center justify-between">
                    <span>{textAnalysis.emoji} {textAnalysis.sentiment_label.toUpperCase()}</span>
                    <Badge variant={getSentimentBadgeVariant(textAnalysis.sentiment_label)}>
                      {Math.abs(textAnalysis.sentiment_score * 100).toFixed(0)}% confidence
                    </Badge>
                  </div>
                  <p className="text-xs mt-1">{textAnalysis.interpretation}</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Sentiment Summary */}
      {summary && (
        <Card>
          <CardHeader>
            <CardTitle>📊 Sentiment Analysis Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div>
                <h3 className="font-semibold text-lg mb-2">{summary.overall_mood}</h3>
                <p className="text-gray-600 mb-3">{summary.market_tone}</p>
                <div className="space-y-1 text-sm">
                  <div>🟢 {summary.sentiment_distribution.bullish}</div>
                  <div>🔴 {summary.sentiment_distribution.bearish}</div>
                  <div>⚪ {summary.sentiment_distribution.neutral}</div>
                </div>
              </div>
              <div className="lg:col-span-2">
                <h4 className="font-semibold mb-2">🏷️ Top Themes</h4>
                <div className="flex flex-wrap gap-2">
                  {summary.top_themes.map((theme, i) => (
                    <Badge key={i} variant="outline">{theme}</Badge>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* News Articles */}
      <Card>
        <CardHeader>
          <CardTitle>Latest Market News ({articles.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {articles.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              {loading ? 'Loading news...' : 'No news articles found'}
            </div>
          ) : (
            <div className="space-y-4">
              {articles.map((article, i) => (
                <div key={i} className={`p-4 border rounded-lg ${getSentimentColor(article.sentiment_label)}`}>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="text-2xl">{article.emoji}</span>
                        <Badge variant={getSentimentBadgeVariant(article.sentiment_label)}>
                          {article.sentiment_label.toUpperCase()}
                        </Badge>
                        <span className="text-xs text-gray-500">{article.confidence.toFixed(0)}% confidence</span>
                      </div>
                      <h3 className="font-semibold text-lg mb-2">
                        <a href={article.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                          {article.title}
                        </a>
                      </h3>
                      <p className="text-gray-700 mb-3">{article.description}</p>
                      <div className="flex items-center justify-between text-sm text-gray-500">
                        <span className="font-medium">{article.source}</span>
                        <span>{article.timestamp_relative}</span>
                      </div>
                    </div>
                    <div className="ml-4 text-right">
                      <div className={`text-lg font-bold ${
                        article.sentiment_score > 0 ? 'text-green-600' : 
                        article.sentiment_score < 0 ? 'text-red-600' : 'text-gray-600'
                      }`}>
                        {article.sentiment_score > 0 ? '+' : ''}{(article.sentiment_score * 100).toFixed(0)}
                      </div>
                      <div className="text-xs text-gray-500">Score</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}