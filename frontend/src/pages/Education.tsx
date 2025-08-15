import React, { useEffect, useState } from 'react';
import { Box, CircularProgress, Divider, Grid, List, ListItemButton, ListItemText, Paper, Stack, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';

interface Course { id: string; title: string; slug: string; description?: string; }
interface Module { id: string; course_id: string; title: string; order_index: number; }
interface Section { id: string; module_id: string; title: string; order_index: number; }
interface Lesson { id: string; section_id: string; title: string; order_index: number; type: string; duration_sec?: number; }

export default function Education() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [courses, setCourses] = useState<Course[]>([]);
  const [modules, setModules] = useState<Module[]>([]);
  const [sections, setSections] = useState<Section[]>([]);
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [activeCourse, setActiveCourse] = useState<string | null>(null);
  const [activeModule, setActiveModule] = useState<string | null>(null);
  const [activeSection, setActiveSection] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const { data } = await apiService.get<Course[]>('/api/learning/courses');
        setCourses(data);
        if (data.length) {
          const saved = localStorage.getItem('edu.activeCourse');
          const id = saved && data.find(c => c.id === saved) ? saved : data[0].id;
          setActiveCourse(id);
          localStorage.setItem('edu.activeCourse', id);
        }
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  useEffect(() => {
    if (!activeCourse) return;
    const loadModules = async () => {
      const { data } = await apiService.get<Module[]>(`/api/learning/courses/${activeCourse}/modules`);
      setModules(data);
      setActiveModule(data[0]?.id || null);
      setSections([]);
      setLessons([]);
    };
    loadModules();
  }, [activeCourse]);

  useEffect(() => {
    if (!activeModule) return;
    const loadSections = async () => {
      const { data } = await apiService.get<Section[]>(`/api/learning/modules/${activeModule}/sections`);
      setSections(data);
      setActiveSection(data[0]?.id || null);
      setLessons([]);
    };
    loadSections();
  }, [activeModule]);

  useEffect(() => {
    if (!activeSection) return;
    const loadLessons = async () => {
      const { data } = await apiService.get<Lesson[]>(`/api/learning/sections/${activeSection}/lessons`);
      setLessons(data);
    };
    loadLessons();
  }, [activeSection]);

  return (
    <Grid container spacing={2} sx={{ p: 2 }}>
      <Grid item xs={12} md={3}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6">Courses</Typography>
          <Divider sx={{ my: 1 }} />
          {loading && <CircularProgress size={18} />}
          <List>
            {courses.map(c => (
              <ListItemButton key={c.id} selected={c.id === activeCourse} onClick={() => { setActiveCourse(c.id); localStorage.setItem('edu.activeCourse', c.id); }}>
                <ListItemText primary={c.title} secondary={c.description} />
              </ListItemButton>
            ))}
          </List>
        </Paper>
      </Grid>
      <Grid item xs={12} md={3}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6">Modules</Typography>
          <Divider sx={{ my: 1 }} />
          <List>
            {modules.map(m => (
              <ListItemButton key={m.id} selected={m.id === activeModule} onClick={() => setActiveModule(m.id)}>
                <ListItemText primary={m.title} />
              </ListItemButton>
            ))}
          </List>
        </Paper>
      </Grid>
      <Grid item xs={12} md={3}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6">Sections</Typography>
          <Divider sx={{ my: 1 }} />
          <List>
            {sections.map(s => (
              <ListItemButton key={s.id} selected={s.id === activeSection} onClick={() => setActiveSection(s.id)}>
                <ListItemText primary={s.title} />
              </ListItemButton>
            ))}
          </List>
        </Paper>
      </Grid>
      <Grid item xs={12} md={3}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6">Lessons</Typography>
          <Divider sx={{ my: 1 }} />
          <Stack spacing={1}>
            {lessons.map(l => (
              <Box key={l.id} sx={{ p: 1, borderRadius: 1, border: '1px solid', borderColor: 'divider' }}>
                <Typography variant="subtitle2">{l.title}</Typography>
                <Typography variant="caption" color="text.secondary">{l.type}{l.duration_sec ? ` • ${l.duration_sec} sec` : ''}</Typography>
                <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                  <Button size="small" variant="outlined" onClick={async () => {
                    await apiService.post(`/api/learning/lessons/${l.id}/progress`, { status: 'in_progress' });
                  }}>Start</Button>
                  <Button size="small" variant="contained" onClick={async () => {
                    await apiService.post(`/api/learning/lessons/${l.id}/progress`, { status: 'completed', percent: 100 });
                  }}>Mark Complete</Button>
                  <Button size="small" onClick={() => navigate(`/education/lesson/${l.id}`)}>Open</Button>
                </Stack>
              </Box>
            ))}
          </Stack>
        </Paper>
      </Grid>
    </Grid>
  );
}