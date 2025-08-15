import React, { useEffect, useState } from 'react';
import { Box, Button, Paper, RadioGroup, FormControlLabel, Radio, Checkbox, Stack, Typography, Alert } from '@mui/material';
import { apiService } from '../../services/api';

interface QuizQuestion {
  id: string;
  type: 'mcq' | 'multi' | 'short';
  prompt: string;
  choices?: string[];
  correct?: any; // not used on client grading
  points?: number;
}

interface QuizData {
  id: string;
  lesson_id: string;
  settings: { pass_score?: number };
  questions: QuizQuestion[];
}

export default function Quiz({ lessonId }: { lessonId: string }) {
  const [loading, setLoading] = useState(true);
  const [quiz, setQuiz] = useState<QuizData | null>(null);
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const { data } = await apiService.get<QuizData>(`/api/learning/lessons/${lessonId}/quiz`);
        setQuiz(data);
      } catch (e) {
        setQuiz(null);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [lessonId]);

  const submit = async () => {
    if (!quiz) return;
    const { data } = await apiService.post(`/api/learning/quizzes/${quiz.id}/attempt`, { answers });
    setResult(data);
  };

  if (loading) return <Typography>Loading quiz...</Typography>;
  if (!quiz) return <Typography color="text.secondary">No quiz for this lesson.</Typography>;

  return (
    <Box>
      {result && (
        <Alert severity={result.passed ? 'success' : 'warning'} sx={{ mb: 2 }}>
          Score: {result.score}/{result.max_score} • {result.passed ? 'Passed' : 'Not passed'}
        </Alert>
      )}
      <Stack spacing={2}>
        {quiz.questions.map((q) => (
          <Paper key={q.id} sx={{ p: 2 }}>
            <Typography variant="subtitle1" sx={{ mb: 1 }}>{q.prompt}</Typography>
            {q.type === 'mcq' && (
              <RadioGroup
                value={answers[q.id] ?? ''}
                onChange={(e) => setAnswers({ ...answers, [q.id]: e.target.value })}
              >
                {q.choices?.map((c) => (
                  <FormControlLabel key={c} value={c} control={<Radio />} label={c} />
                ))}
              </RadioGroup>
            )}
            {q.type === 'multi' && (
              <Stack>
                {q.choices?.map((c) => (
                  <FormControlLabel
                    key={c}
                    control={<Checkbox checked={(answers[q.id] || []).includes(c)} onChange={(e) => {
                      const prev = new Set(answers[q.id] || []);
                      if (e.target.checked) prev.add(c); else prev.delete(c);
                      setAnswers({ ...answers, [q.id]: Array.from(prev) });
                    }} />}
                    label={c}
                  />
                ))}
              </Stack>
            )}
            {q.type === 'short' && (
              <input
                type="text"
                value={answers[q.id] ?? ''}
                onChange={(e) => setAnswers({ ...answers, [q.id]: e.target.value })}
                style={{ padding: 8, width: '100%', borderRadius: 4, border: '1px solid #ccc' }}
              />
            )}
          </Paper>
        ))}
        <Box>
          <Button variant="contained" onClick={submit}>Submit Quiz</Button>
        </Box>
      </Stack>
    </Box>
  );
}