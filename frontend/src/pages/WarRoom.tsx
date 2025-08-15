import React, { useState } from 'react';
import { Button, Card, CardContent, Grid, Stack, TextField, Typography } from '@mui/material';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000';

interface AgentReply { agent: string; role: string; view: string; confidence: number; }

export default function WarRoomPage() {
  const [prompt, setPrompt] = useState('');
  const [replies, setReplies] = useState<AgentReply[]>([]);
  const [consensus, setConsensus] = useState('');

  const runDebate = async () => {
    try {
      const { data } = await axios.post(`${API_BASE}/api/war-room/debate`, {
        user_id: 'demo-user',
        user_prompt: prompt,
      });
      setReplies(data.replies || []);
      setConsensus(data.consensus || '');
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <Stack spacing={2} sx={{ p: 2 }}>
      <Typography variant="h5">AI War Room</Typography>
      <TextField label="Your prompt" value={prompt} onChange={(e) => setPrompt(e.target.value)} />
      <Button variant="contained" onClick={runDebate}>Run Debate</Button>

      {consensus && (
        <Typography variant="subtitle1" color="primary">{consensus}</Typography>
      )}

      <Grid container spacing={2}>
        {replies.map((r, i) => (
          <Grid item md={4} xs={12} key={i}>
            <Card>
              <CardContent>
                <Typography variant="subtitle2">{r.agent} ({r.role})</Typography>
                <Typography variant="body2" sx={{ mt: 1 }}>{r.view}</Typography>
                <Typography variant="caption" sx={{ mt: 1, display: 'block' }}>Confidence: {Math.round(r.confidence * 100)}%</Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Stack>
  );
}