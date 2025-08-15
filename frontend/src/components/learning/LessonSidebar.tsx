import React, { useEffect, useState } from 'react';
import { Box, List, ListItemButton, ListItemText, Paper, Typography } from '@mui/material';
import { apiService } from '../../services/api';

interface Module { id: string; course_id: string; title: string; order_index: number; }
interface Section { id: string; module_id: string; title: string; order_index: number; }
interface Lesson { id: string; section_id: string; title: string; order_index: number; type: string; duration_sec?: number; }

export default function LessonSidebar({ courseId, onOpenLesson, activeLessonId }: { courseId: string; onOpenLesson: (id: string) => void; activeLessonId?: string; }) {
  const [modules, setModules] = useState<Module[]>([]);
  const [sections, setSections] = useState<Record<string, Section[]>>({});
  const [lessons, setLessons] = useState<Record<string, Lesson[]>>({});

  useEffect(() => {
    const load = async () => {
      const { data: mods } = await apiService.get<Module[]>(`/api/learning/courses/${courseId}/modules`);
      setModules(mods);
      const secMap: Record<string, Section[]> = {};
      const lesMap: Record<string, Lesson[]> = {};
      for (const m of mods) {
        const { data: secs } = await apiService.get<Section[]>(`/api/learning/modules/${m.id}/sections`);
        secMap[m.id] = secs;
        for (const s of secs) {
          const { data: less } = await apiService.get<Lesson[]>(`/api/learning/sections/${s.id}/lessons`);
          lesMap[s.id] = less;
        }
      }
      setSections(secMap);
      setLessons(lesMap);
    };
    if (courseId) load();
  }, [courseId]);

  return (
    <Paper sx={{ p: 2, height: '100%', overflowY: 'auto' }}>
      <Typography variant="subtitle1" sx={{ mb: 1 }}>Curriculum</Typography>
      <List>
        {modules.map(m => (
          <Box key={m.id} sx={{ mb: 1 }}>
            <Typography variant="subtitle2" sx={{ px: 1, py: 0.5 }}>{m.title}</Typography>
            {sections[m.id]?.map(s => (
              <Box key={s.id} sx={{ pl: 2 }}>
                <Typography variant="body2" color="text.secondary" sx={{ px: 1, py: 0.5 }}>{s.title}</Typography>
                {lessons[s.id]?.map(l => (
                  <ListItemButton key={l.id} selected={l.id === activeLessonId} onClick={() => onOpenLesson(l.id)} sx={{ pl: 3 }}>
                    <ListItemText primaryTypographyProps={{ fontSize: 14 }} primary={l.title} />
                  </ListItemButton>
                ))}
              </Box>
            ))}
          </Box>
        ))}
      </List>
    </Paper>
  );
}