import React, { useEffect, useMemo, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import LessonSidebar from '../components/learning/LessonSidebar';
import { apiService } from '../services/api';
import { Box, Button, Chip, Divider, Paper, Stack, Typography, Tabs, Tab, Grid } from '@mui/material';
import ReactMarkdown from 'react-markdown';
import Quiz from '../components/learning/Quiz';
import Assignment from '../components/learning/Assignment';

interface LessonDetail {
  id: string;
  section_id: string;
  title: string;
  order_index: number;
  type: string;
  duration_sec?: number;
  content_rich?: string;
  video_url?: string;
  embed_url?: string;
  downloads_json?: string; // JSON array of {label,url}
}

export default function LessonView() {
  const { lessonId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [lesson, setLesson] = useState<LessonDetail | null>(null);

  useEffect(() => {
    if (!lessonId) return;
    const load = async () => {
      setLoading(true);
      try {
        const { data } = await apiService.get<LessonDetail>(`/api/learning/lessons/${lessonId}`);
        setLesson(data);
        // Mark as in progress when opened
        await apiService.post(`/api/learning/lessons/${lessonId}/progress`, { status: 'in_progress' });
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [lessonId]);

  const downloads = useMemo(() => {
    if (!lesson?.downloads_json) return [] as Array<{ label: string; url: string }>;
    try { return JSON.parse(lesson.downloads_json || '[]'); } catch { return []; }
  }, [lesson]);

  if (loading) {
    return <Box sx={{ p: 3 }}><Typography>Loading lesson...</Typography></Box>;
  }
  if (!lesson) {
    return <Box sx={{ p: 3 }}><Typography color="error">Lesson not found.</Typography></Box>;
  }

  const [tab, setTab] = useState(0);

  return (
    <Grid container spacing={2} sx={{ p: 2 }}>
      <Grid item xs={12} md={3}>
        <LessonSidebar courseId={localStorage.getItem('edu.activeCourse') || ''} onOpenLesson={(id) => navigate(`/education/lesson/${id}`)} activeLessonId={lesson.id} />
      </Grid>
      <Grid item xs={12} md={9}>
        <Typography variant="h5" sx={{ mb: 1 }}>{lesson.title}</Typography>
        <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
          <Chip label={lesson.type} size="small" />
          {lesson.duration_sec ? <Chip label={`${lesson.duration_sec} sec`} size="small" /> : null}
        </Stack>

        <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }}>
          <Tab label="Content" />
          <Tab label="Quiz" />
          <Tab label="Assignment" />
        </Tabs>

        {tab === 0 && (
          <Paper sx={{ p: 2, mb: 2 }}>
            {lesson.video_url && (
              <Box sx={{ mb: 2 }}>
                <video src={lesson.video_url} controls style={{ width: '100%', borderRadius: 8 }} />
              </Box>
            )}

            {lesson.embed_url && (
              <Box sx={{ mb: 2 }}>
                <iframe title="Lesson Embed" src={lesson.embed_url} style={{ width: '100%', height: 420, border: 0, borderRadius: 8 }} />
              </Box>
            )}

            {lesson.content_rich && (
              <Box sx={{ '& img': { maxWidth: '100%' } }}>
                <ReactMarkdown>{lesson.content_rich}</ReactMarkdown>
              </Box>
            )}

            {downloads.length > 0 && (
              <Box sx={{ mt: 2 }}>
                <Divider sx={{ mb: 1 }}>Downloads</Divider>
                <Stack direction="row" spacing={1}>
                  {downloads.map((d, i) => (
                    <Button key={i} href={d.url} target="_blank" rel="noreferrer" variant="outlined" size="small">
                      {d.label}
                    </Button>
                  ))}
                </Stack>
              </Box>
            )}
          </Paper>
        )}

        {tab === 1 && (
          <Paper sx={{ p: 2, mb: 2 }}>
            <Quiz lessonId={lesson.id} />
          </Paper>
        )}

        {tab === 2 && (
          <Paper sx={{ p: 2, mb: 2 }}>
            <Assignment lessonId={lesson.id} />
          </Paper>
        )}

        <Stack direction="row" spacing={1}>
          <Button variant="outlined" onClick={() => navigate(-1)}>Back</Button>
          <Button variant="contained" color="primary" onClick={async () => {
            await apiService.post(`/api/learning/lessons/${lesson.id}/progress`, { status: 'completed', percent: 100 });
            navigate(-1);
          }}>Mark Complete</Button>
        </Stack>
      </Grid>
    </Grid>
  );
}