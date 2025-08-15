import React, { useEffect, useRef, useState } from 'react';
import { Button, Chip, Stack, TextField, Typography } from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000';

export default function CoachTherapyPage() {
  const [mode, setMode] = useState<'coach' | 'therapy'>('coach');
  const [userMessage, setUserMessage] = useState('');
  const [reply, setReply] = useState('');
  const [alerts, setAlerts] = useState<string[]>([]);
  const [redactions, setRedactions] = useState<any>({});
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  // STT: record audio and post to /api/voice/transcribe
  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mr = new MediaRecorder(stream);
    mediaRecorderRef.current = mr;
    chunksRef.current = [];
    mr.ondataavailable = (e) => chunksRef.current.push(e.data);
    mr.onstop = async () => {
      const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
      const formData = new FormData();
      formData.append('file', blob, 'audio.webm');
      try {
        const { data } = await axios.post(`${API_BASE}/api/voice/transcribe`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        setUserMessage((prev) => `${prev} ${data.text}`.trim());
        setRedactions(data.redactions || {});
      } catch (e) {
        console.error(e);
      }
    };
    mr.start();
    setRecording(true);
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setRecording(false);
  };

  // TTS: use browser speech synthesis with SSML wrapper
  const speak = async () => {
    if (!reply) return;
    try {
      const { data } = await axios.post(`${API_BASE}/api/voice/speak`, { text: reply });
      const utter = new SpeechSynthesisUtterance(data.text);
      window.speechSynthesis.speak(utter);
    } catch (e) {
      console.error(e);
    }
  };

  const sendMessage = async () => {
    try {
      const { data } = await axios.post(`${API_BASE}/api/coach/message`, {
        user_id: 'demo-user',
        user_message: userMessage,
        mode,
      });
      setReply(data.reply);
      setAlerts(data.alerts || []);
      setRedactions(data.redactions || {});
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <Stack spacing={2} sx={{ p: 2 }}>
      <Typography variant="h5">AI Coach & Therapy</Typography>
      <Stack direction="row" spacing={1}>
        <Button variant={mode === 'coach' ? 'contained' : 'outlined'} onClick={() => setMode('coach')}>Coach</Button>
        <Button variant={mode === 'therapy' ? 'contained' : 'outlined'} onClick={() => setMode('therapy')}>Therapy</Button>
      </Stack>

      <TextField
        label="Your message"
        multiline
        minRows={3}
        value={userMessage}
        onChange={(e) => setUserMessage(e.target.value)}
      />

      <Stack direction="row" spacing={1}>
        {!recording ? (
          <Button variant="outlined" startIcon={<MicIcon />} onClick={startRecording}>Record</Button>
        ) : (
          <Button color="error" variant="contained" startIcon={<StopIcon />} onClick={stopRecording}>Stop</Button>
        )}
        <Button variant="contained" onClick={sendMessage}>Send</Button>
      </Stack>

      {alerts.length > 0 && (
        <Stack direction="row" spacing={1}>
          {alerts.map((a, i) => (
            <Chip key={i} color="warning" label={a} />
          ))}
        </Stack>
      )}

      {reply && (
        <Stack spacing={1}>
          <Typography variant="subtitle1">AI Reply</Typography>
          <Typography>{reply}</Typography>
          <Button startIcon={<PlayArrowIcon />} onClick={speak}>Play</Button>
        </Stack>
      )}

      <Stack direction="row" spacing={1}>
        {Object.entries(redactions).filter(([_, v]) => v).map(([k]) => (
          <Chip key={k} color="error" label={`PII redacted: ${k}`} />
        ))}
      </Stack>
    </Stack>
  );
}