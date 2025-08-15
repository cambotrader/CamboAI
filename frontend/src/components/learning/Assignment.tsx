import React, { useEffect, useState } from 'react';
import { Box, Button, Paper, Stack, TextField, Typography, Alert } from '@mui/material';
import { apiService } from '../../services/api';

interface AssignmentData {
  id: string;
  lesson_id: string;
  prompt?: string;
  rubric?: Record<string, any> | null;
  due_at?: string | null;
}

export default function Assignment({ lessonId }: { lessonId: string }) {
  const [loading, setLoading] = useState(true);
  const [assignment, setAssignment] = useState<AssignmentData | null>(null);
  const [text, setText] = useState('');
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const { data } = await apiService.get<AssignmentData>(`/api/learning/lessons/${lessonId}/assignment`);
        setAssignment(data);
      } catch (e) {
        setAssignment(null);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [lessonId]);

  const submit = async () => {
    if (!assignment) return;
    await apiService.post(`/api/learning/assignments/${assignment.id}/submit`, { text });
    setSubmitted(true);
  };

  if (loading) return <Typography>Loading assignment...</Typography>;
  if (!assignment) return <Typography color="text.secondary">No assignment for this lesson.</Typography>;

  return (
    <Box>
      {submitted && <Alert severity="success" sx={{ mb: 2 }}>Submitted. You can update and re-submit any time.</Alert>}
      <Paper sx={{ p: 2 }}>
        <Typography variant="subtitle1" sx={{ mb: 1 }}>Prompt</Typography>
        <Typography sx={{ whiteSpace: 'pre-wrap', mb: 2 }}>{assignment.prompt || 'No prompt provided.'}</Typography>
        {assignment.due_at && (
          <Typography variant="caption" color="text.secondary">Due: {new Date(assignment.due_at).toLocaleString()}</Typography>
        )}
      </Paper>
      <Stack spacing={2} sx={{ mt: 2 }}>
        <TextField
          label="Your response"
          multiline
          minRows={6}
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <Button variant="contained" onClick={submit}>Submit Assignment</Button>
      </Stack>
    </Box>
  );
}