import React, { useEffect, useState } from 'react';
import { Button, Chip, Grid, List, ListItem, ListItemText, Stack, TextField, Typography } from '@mui/material';
import { apiService } from '../services/api';

interface Room { slug: string; title: string; }
interface Message { room: string; user_id: string; text: string; timestamp: string; }

export default function CommunityPage() {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [active, setActive] = useState<string>('stocks');
  const [messages, setMessages] = useState<Message[]>([]);
  const [text, setText] = useState('');
  const [redactions, setRedactions] = useState<any>({});

  const loadRooms = async () => {
    await apiService.post('/api/community/init'); // idempotent
    const { data } = await apiService.get<{ rooms: Room[] }>('/api/community/rooms');
    setRooms(data.rooms || []);
  };

  const loadHistory = async (room: string) => {
    const { data } = await apiService.get<Message[]>(`/api/community/history/${room}`);
    setMessages(data || []);
  };

  const send = async () => {
    const { data } = await apiService.post<{ ok: boolean; redactions: any }>(`/api/community/post`, {
      room: active,
      user_id: 'demo-user',
      text,
    });
    setRedactions(data.redactions || {});
    setText('');
    await loadHistory(active);
  };

  useEffect(() => { loadRooms(); }, []);
  useEffect(() => { if (active) loadHistory(active); }, [active]);

  return (
    <Grid container spacing={2} sx={{ p: 2 }}>
      <Grid item md={3} xs={12}>
        <Typography variant="h6">Rooms</Typography>
        <List>
          {rooms.map(r => (
            <ListItem key={r.slug} button selected={active === r.slug} onClick={() => setActive(r.slug)}>
              <ListItemText primary={r.title} />
            </ListItem>
          ))}
        </List>
      </Grid>
      <Grid item md={9} xs={12}>
        <Typography variant="h6">{active.toUpperCase()}</Typography>
        <Stack spacing={1} sx={{ mb: 2 }}>
          {messages.map((m, i) => (
            <Stack key={i}>
              <Typography variant="caption">{m.user_id} • {new Date(m.timestamp).toLocaleTimeString()}</Typography>
              <Typography>{m.text}</Typography>
            </Stack>
          ))}
        </Stack>
        <Stack direction="row" spacing={1}>
          <TextField fullWidth value={text} onChange={(e) => setText(e.target.value)} />
          <Button variant="contained" onClick={send}>Send</Button>
        </Stack>
        <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
          {Object.entries(redactions).filter(([_, v]) => v).map(([k]) => (
            <Chip key={k} color="error" label={`PII redacted: ${k}`} />
          ))}
        </Stack>
      </Grid>
    </Grid>
  );
}