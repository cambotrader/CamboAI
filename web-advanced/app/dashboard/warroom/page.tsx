"use client";
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';

type DebateAgent = {
  name: string;
  role: 'strategist' | 'risk' | 'sentiment' | 'macro' | 'technicals' | 'options';
  emoji: string;
  color: string;
};

type AgentReply = {
  agent: string;
  role: string;
  view: string;
  confidence: number;
  emoji: string;
  color: string;
};

type DebateResult = {
  sanitized_prompt: string;
  replies: AgentReply[];
  consensus: string;
  debate_id: string;
  timestamp: string;
};

const AGENTS: DebateAgent[] = [
  { name: 'Strategist', role: 'strategist', emoji: '🎯', color: 'bg-blue-100 text-blue-800' },
  { name: 'Risk Manager', role: 'risk', emoji: '⚠️', color: 'bg-red-100 text-red-800' },
  { name: 'Sentiment Analyzer', role: 'sentiment', emoji: '📊', color: 'bg-green-100 text-green-800' },
  { name: 'Macro Economist', role: 'macro', emoji: '🌍', color: 'bg-purple-100 text-purple-800' },
  { name: 'Technical Analyst', role: 'technicals', emoji: '📈', color: 'bg-orange-100 text-orange-800' },
  { name: 'Options Specialist', role: 'options', emoji: '⚛️', color: 'bg-indigo-100 text-indigo-800' }
];

export default function WarRoomPage() {
  const [prompt, setPrompt] = useState('');
  const [selectedAgents, setSelectedAgents] = useState<string[]>(AGENTS.map(a => a.name));
  const [debateResult, setDebateResult] = useState<DebateResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState<DebateResult[]>([]);

  const runDebate = async () => {
    if (!prompt.trim()) return;
    
    setLoading(true);
    try {
      // Mock API call - replace with real API call to /api/war-room/debate
      const mockReplies: AgentReply[] = selectedAgents.map(agentName => {
        const agent = AGENTS.find(a => a.name === agentName);
        if (!agent) return null;
        
        // Mock responses based on agent type
        const responses = {
          strategist: `Looking at the fundamentals and market positioning, I see this as a strategic opportunity with moderate upside potential. The key is timing and position sizing.`,
          risk: `I'm concerned about the current volatility levels and correlation risks. We need to consider downside protection and position limits before proceeding.`,
          sentiment: `Market sentiment indicators are showing mixed signals. Social sentiment is bullish but institutional flows suggest caution. Fear/greed index at neutral.`,
          macro: `Macro environment presents headwinds with rising rates and inflation concerns. Global growth dynamics favor defensive positioning over aggressive risk-taking.`,
          technicals: `Chart patterns show potential breakout above resistance, but volume confirmation is lacking. RSI approaching overbought territory. Watch for reversal signals.`,
          options: `Implied volatility is elevated providing opportunities for premium selling strategies. Delta-hedged approaches could capitalize on time decay while limiting directional risk.`
        };
        
        return {
          agent: agent.name,
          role: agent.role,
          view: responses[agent.role] || 'Analysis pending...',
          confidence: 0.6 + Math.random() * 0.3,
          emoji: agent.emoji,
          color: agent.color
        };
      }).filter(Boolean) as AgentReply[];

      const result: DebateResult = {
        sanitized_prompt: prompt,
        replies: mockReplies,
        consensus: `Consensus: Mixed outlook with cautious optimism. Risk-adjusted approach recommended with defensive hedging. 3 agents bullish, 2 neutral, 1 bearish.`,
        debate_id: `debate_${Date.now()}`,
        timestamp: new Date().toISOString()
      };

      setDebateResult(result);
      setChatHistory(prev => [result, ...prev]);
      setPrompt('');
      
    } catch (error) {
      console.error('Debate failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleAgent = (agentName: string) => {
    setSelectedAgents(prev => 
      prev.includes(agentName) 
        ? prev.filter(name => name !== agentName)
        : [...prev, agentName]
    );
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">👥 AI War Room</h1>
        <div className="flex items-center space-x-2">
          <Badge variant="outline">{selectedAgents.length} agents active</Badge>
          <Button variant="outline" size="sm">
            📊 Debate History
          </Button>
        </div>
      </div>

      {/* Agent Selection */}
      <Card>
        <CardHeader>
          <CardTitle>🤖 Select AI Agents for Debate</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {AGENTS.map((agent) => (
              <Button
                key={agent.name}
                variant={selectedAgents.includes(agent.name) ? 'default' : 'outline'}
                onClick={() => toggleAgent(agent.name)}
                className="h-auto p-4 flex flex-col space-y-2"
              >
                <span className="text-2xl">{agent.emoji}</span>
                <span className="font-semibold text-sm">{agent.name}</span>
                <span className="text-xs opacity-70 capitalize">{agent.role}</span>
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Prompt Input */}
      <Card>
        <CardHeader>
          <CardTitle>💬 Start AI Debate</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Textarea
              placeholder="Enter your trading question or market analysis request..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={4}
              className="resize-none"
            />
            <div className="flex justify-between items-center">
              <div className="text-sm text-gray-500">
                {selectedAgents.length} agents will analyze your prompt
              </div>
              <Button 
                onClick={runDebate} 
                disabled={loading || !prompt.trim() || selectedAgents.length === 0}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
              >
                {loading ? 'Debating...' : '🚀 Start Debate'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Latest Debate Result */}
      {debateResult && (
        <Card className="border-2 border-blue-200 bg-gradient-to-r from-blue-50 to-purple-50">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <span>🎯 Latest Debate Results</span>
              <Badge>{new Date(debateResult.timestamp).toLocaleTimeString()}</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {/* Original Question */}
              <div className="p-4 bg-white rounded border border-gray-200">
                <div className="text-sm font-medium text-gray-600 mb-2">Your Question:</div>
                <div className="text-gray-800">{debateResult.sanitized_prompt}</div>
              </div>

              {/* Agent Responses */}
              <div className="space-y-4">
                <h3 className="font-semibold text-lg">🗣️ Agent Responses</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {debateResult.replies.map((reply, index) => (
                    <Card key={index} className="border-l-4 border-l-blue-500">
                      <CardContent className="pt-4">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center space-x-2">
                            <span className="text-2xl">{reply.emoji}</span>
                            <div>
                              <div className="font-semibold">{reply.agent}</div>
                              <Badge className={reply.color} variant="secondary">
                                {reply.role}
                              </Badge>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-sm text-gray-600">Confidence</div>
                            <div className="font-bold">{(reply.confidence * 100).toFixed(0)}%</div>
                          </div>
                        </div>
                        <div className="text-sm text-gray-700 leading-relaxed">
                          {reply.view}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>

              {/* Consensus */}
              <Card className="bg-gradient-to-r from-green-50 to-blue-50 border-green-200">
                <CardContent className="pt-4">
                  <div className="flex items-center space-x-2 mb-3">
                    <span className="text-2xl">🏆</span>
                    <h3 className="font-semibold text-lg text-green-800">Consensus Analysis</h3>
                  </div>
                  <div className="text-green-700 leading-relaxed">
                    {debateResult.consensus}
                  </div>
                </CardContent>
              </Card>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Chat History */}
      {chatHistory.length > 1 && (
        <Card>
          <CardHeader>
            <CardTitle>📚 Recent Debates</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {chatHistory.slice(1, 4).map((debate, index) => (
                <div key={debate.debate_id} className="p-4 border rounded bg-gray-50">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="text-sm font-medium text-gray-800 mb-2">
                        "{debate.sanitized_prompt.slice(0, 100)}..."
                      </div>
                      <div className="text-xs text-gray-500">
                        {debate.replies.length} agents responded • {new Date(debate.timestamp).toLocaleString()}
                      </div>
                    </div>
                    <Button size="sm" variant="outline">
                      View Full
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Prompts */}
      <Card>
        <CardHeader>
          <CardTitle>💡 Quick Debate Starters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {[
              "Should I buy AAPL calls before earnings?",
              "Is the market due for a correction?",
              "Best hedging strategy for tech portfolio?",
              "Will Fed rate cuts boost growth stocks?",
              "Is crypto correlation with stocks breaking down?",
              "Time to rotate from growth to value?"
            ].map((quickPrompt, index) => (
              <Button
                key={index}
                variant="outline"
                className="text-left justify-start h-auto p-3"
                onClick={() => setPrompt(quickPrompt)}
              >
                <span className="text-sm">{quickPrompt}</span>
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}