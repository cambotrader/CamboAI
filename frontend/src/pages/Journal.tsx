import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Typography, Box, Paper, TextField, Button, Chip, Stack, IconButton, ToggleButton, ToggleButtonGroup, Tooltip } from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import SaveIcon from '@mui/icons-material/Save';
import CancelIcon from '@mui/icons-material/Cancel';

interface Note { id: number; title: string; body: string; tags: string[]; date: string; }

const Journal: React.FC = () => {
  const [notes, setNotes] = useState<Note[]>([]);
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [tagInput, setTagInput] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [search, setSearch] = useState(() => localStorage.getItem('journal.search') || '');
  const [filterTagInput, setFilterTagInput] = useState('');
  const [filterTags, setFilterTags] = useState<string[]>(() => {
    try { const raw = localStorage.getItem('journal.filterTags'); return raw ? JSON.parse(raw) : []; } catch { return []; }
  });
  const [dateFrom, setDateFrom] = useState<string>(() => localStorage.getItem('journal.dateFrom') || '');
  const [dateTo, setDateTo] = useState<string>(() => localStorage.getItem('journal.dateTo') || '');
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editBody, setEditBody] = useState('');
  const [editTagInput, setEditTagInput] = useState('');
  const [editTags, setEditTags] = useState<string[]>([]);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [storageMode, setStorageMode] = useState<'local' | 'api'>(() => (localStorage.getItem('journalStorageMode') as 'local' | 'api') || 'local');
  const [loading, setLoading] = useState(false);
  const [quickTags, setQuickTags] = useState<string[]>([]);

  useEffect(() => {
    if (storageMode === 'local') {
      try {
        const raw = localStorage.getItem('journalNotes');
        if (raw) {
          const parsed = JSON.parse(raw);
          if (Array.isArray(parsed)) {
            setNotes(parsed);
            const allTags = Array.from(new Set(parsed.flatMap((n: Note) => n.tags)));
            setQuickTags(allTags.slice(0, 10));
          }
        } else {
          setNotes([]);
        }
      } catch {
        setNotes([]);
      }
    } else {
      // API mode: fetch from backend
      const fetchApi = async () => {
        setLoading(true);
        try {
          const { apiService } = await import('../services/api');
          const data = await apiService.getJournal({});
          setNotes(data);
          const allTags = Array.from(new Set(data.flatMap((n: Note) => n.tags)));
          setQuickTags(allTags.slice(0, 10));
        } catch (e) {
          console.error('Failed to load journal from API', e);
        } finally {
          setLoading(false);
        }
      };
      fetchApi();
    }
  }, [storageMode]);

  useEffect(() => {
    if (storageMode === 'local') {
      try {
        localStorage.setItem('journalNotes', JSON.stringify(notes));
      } catch {
        // storage may be unavailable
      }
    }
  }, [notes, storageMode]);

  useEffect(() => {
    localStorage.setItem('journalStorageMode', storageMode);
  }, [storageMode]);

  // Persist filters
  useEffect(() => { localStorage.setItem('journal.search', search); }, [search]);
  useEffect(() => { try { localStorage.setItem('journal.filterTags', JSON.stringify(filterTags)); } catch {} }, [filterTags]);
  useEffect(() => { localStorage.setItem('journal.dateFrom', dateFrom); }, [dateFrom]);
  useEffect(() => { localStorage.setItem('journal.dateTo', dateTo); }, [dateTo]);

  const addTag = () => {
    const t = tagInput.trim();
    if (t && !tags.includes(t)) {
      setTags([...tags, t]);
    }
    setTagInput('');
  };

  const addNote = () => {
    if (!title.trim() && !body.trim()) {
      return;
    }
    const createLocal = () => {
      const n: Note = { id: Date.now(), title: title.trim(), body: body.trim(), tags, date: new Date().toISOString() };
      setNotes([n, ...notes]);
    };
    const createApi = async () => {
      try {
        setLoading(true);
        const { apiService } = await import('../services/api');
        const created = await apiService.createJournal({ title, body, tags });
        setNotes([created as Note, ...notes]);
      } catch (e) {
        console.error('Create note failed', e);
      } finally {
        setLoading(false);
      }
    };
    if (storageMode === 'local') {
      createLocal();
    } else {
      void createApi();
    }
    setTitle(''); setBody(''); setTags([]); setTagInput('');
  };

  const removeNote = (id: number) => {
    if (storageMode === 'local') {
      setNotes(notes.filter(n => n.id !== id));
    } else {
      (async () => {
        try {
          setLoading(true);
          const { apiService } = await import('../services/api');
          await apiService.deleteJournal(id);
          setNotes(notes.filter(n => n.id !== id));
        } catch (e) {
          console.error('Delete note failed', e);
        } finally {
          setLoading(false);
        }
      })();
    }
  };
  const removeTag = (t: string) => setTags(tags.filter(x => x !== t));

  const addFilterTag = () => {
    const t = filterTagInput.trim();
    if (t && !filterTags.includes(t)) {
      setFilterTags([...filterTags, t]);
    }
    setFilterTagInput('');
  };
  const removeFilterTag = (t: string) => setFilterTags(filterTags.filter(x => x !== t));

  const toDateOnly = (iso: string) => {
    try {
      const d = new Date(iso);
      return new Date(d.getFullYear(), d.getMonth(), d.getDate());
    } catch {
      return null;
    }
  };

  const filteredNotes = useMemo(() => {
    const searchLower = search.trim().toLowerCase();
    const from = dateFrom ? new Date(dateFrom) : null;
    const to = dateTo ? new Date(dateTo) : null;
    return notes.filter(n => {
      const titleBody = `${n.title} ${n.body}`.toLowerCase();
      if (searchLower && !titleBody.includes(searchLower)) {
        return false;
      }
      if (filterTags.length > 0) {
        const hasAny = n.tags.some(t => filterTags.includes(t));
        if (!hasAny) {
          return false;
        }
      }
      if (from || to) {
        const nd = toDateOnly(n.date);
        if (!nd) {
          return false;
        }
        if (from && nd < from) {
          return false;
        }
        if (to) {
          // include the entire end day
          const end = new Date(to.getFullYear(), to.getMonth(), to.getDate(), 23, 59, 59, 999);
          if (nd > end) {
            return false;
          }
        }
      }
      return true;
    });
  }, [notes, search, filterTags, dateFrom, dateTo]);

  const startEdit = (n: Note) => {
    setEditingId(n.id);
    setEditTitle(n.title);
    setEditBody(n.body);
    setEditTags(n.tags);
    setEditTagInput('');
  };
  const cancelEdit = () => {
    setEditingId(null);
    setEditTitle('');
    setEditBody('');
    setEditTags([]);
    setEditTagInput('');
  };
  const addEditTag = () => {
    const t = editTagInput.trim();
    if (t && !editTags.includes(t)) {
      setEditTags([...editTags, t]);
    }
    setEditTagInput('');
  };
  const removeEditTag = (t: string) => setEditTags(editTags.filter(x => x !== t));
  const saveEdit = () => {
    if (editingId == null) {
      return;
    }
    const applyLocal = () => setNotes(prev => prev.map(n => n.id === editingId ? { ...n, title: editTitle.trim(), body: editBody.trim(), tags: editTags } : n));
    const applyApi = async () => {
      try {
        setLoading(true);
        const { apiService } = await import('../services/api');
        const updated = await apiService.updateJournal(editingId, { title: editTitle, body: editBody, tags: editTags });
        setNotes(prev => prev.map(n => n.id === editingId ? updated as Note : n));
      } catch (e) {
        console.error('Update note failed', e);
      } finally {
        setLoading(false);
      }
    };
    if (storageMode === 'local') {
      applyLocal();
    } else {
      void applyApi();
    }
    cancelEdit();
  };

  const exportJson = () => {
    try {
      const data = JSON.stringify(notes, null, 2);
      const blob = new Blob([data], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `journal-notes-${new Date().toISOString().slice(0,10)}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      window.alert('Export failed');
    }
  };
  const importJson = async (file: File) => {
    try {
      const text = await file.text();
      const parsed = JSON.parse(text);
      if (!Array.isArray(parsed)) {
        window.alert('Invalid JSON format');
        return;
      }
      // basic shape guard
      const valid = parsed.filter((n: any) => n && typeof n.id === 'number' && typeof n.date === 'string');
      if (storageMode === 'local') {
        setNotes(valid);
      } else {
        // Bulk import into API: naive approach create each
        try {
          setLoading(true);
          const { apiService } = await import('../services/api');
          for (const n of valid) {
            await apiService.createJournal({ title: n.title, body: n.body, tags: n.tags });
          }
          const fresh = await apiService.getJournal({});
          setNotes(fresh);
        } catch (e) {
          console.error('Import to API failed', e);
        } finally {
          setLoading(false);
        }
      }
    } catch (e) {
      window.alert('Import failed');
    }
  };

  const exportCsv = () => {
    const header = ['id','date','title','body','tags'];
    const rows = filteredNotes.map(n => [
      n.id,
      n.date,
      '"' + (n.title || '').replaceAll('"','""') + '"',
      '"' + (n.body || '').replaceAll('"','""') + '"',
      '"' + (n.tags || []).join('|').replaceAll('"','""') + '"',
    ].join(','));
    const csv = [header.join(','), ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `journal-${new Date().toISOString().slice(0,10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const importCsv = async (file: File) => {
    try {
      const text = await file.text();
      const lines = text.split(/\r?\n/).filter(l => l.trim().length > 0);
      if (lines.length < 2) { window.alert('CSV has no rows'); return; }
  const header = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''));
      const idx = {
        id: header.indexOf('id'),
        date: header.indexOf('date'),
        title: header.indexOf('title'),
        body: header.indexOf('body'),
        tags: header.indexOf('tags'),
      };
      const parsed: Note[] = [];
      for (let i = 1; i < lines.length; i++) {
        const raw = lines[i];
        // naive CSV parse for our schema: split commas not inside quotes
        const parts: string[] = [];
        let cur = '';
        let inQ = false;
        for (let c = 0; c < raw.length; c++) {
          const ch = raw[c];
          if (ch === '"') {
            if (inQ && raw[c+1] === '"') { cur += '"'; c++; } else { inQ = !inQ; }
          } else if (ch === ',' && !inQ) { parts.push(cur); cur = ''; }
          else { cur += ch; }
        }
        parts.push(cur);
  const get = (j: number) => (j >= 0 && j < parts.length ? parts[j].replace(/^"|"$/g, '') : '');
        const id = Number(get(idx.id));
        const note: Note = {
          id: Number.isFinite(id) ? id : Date.now() + i,
          date: get(idx.date) || new Date().toISOString(),
          title: get(idx.title),
          body: get(idx.body),
          tags: (get(idx.tags) || '').split('|').map(t => t.trim()).filter(Boolean),
        };
        parsed.push(note);
      }
      if (storageMode === 'local') {
        setNotes(parsed);
      } else {
        try {
          setLoading(true);
          const { apiService } = await import('../services/api');
          for (const n of parsed) {
            await apiService.createJournal({ title: n.title, body: n.body, tags: n.tags });
          }
          const fresh = await apiService.getJournal({});
          setNotes(fresh);
        } catch (e) {
          console.error('CSV import to API failed', e);
        } finally {
          setLoading(false);
        }
      }
    } catch (e) {
      window.alert('CSV import failed');
    }
  };

  const bulkDeleteFiltered = async () => {
    if (!window.confirm(`Delete ${filteredNotes.length} filtered note(s)?`)) {
      return;
    }
    if (storageMode === 'local') {
      setNotes(notes.filter(n => !filteredNotes.some(f => f.id === n.id)));
    } else {
      try {
        setLoading(true);
        const { apiService } = await import('../services/api');
        for (const n of filteredNotes) {
          await apiService.deleteJournal(n.id);
        }
        const fresh = await apiService.getJournal({});
        setNotes(fresh);
      } catch (e) {
        console.error('Bulk delete failed', e);
      } finally {
        setLoading(false);
      }
    }
  };

  const bulkDeleteAll = async () => {
    if (!window.confirm('Delete ALL notes?')) {
      return;
    }
    if (storageMode === 'local') {
      setNotes([]);
    } else {
      try {
        setLoading(true);
        const { apiService } = await import('../services/api');
        for (const n of notes) {
          await apiService.deleteJournal(n.id);
        }
        setNotes([]);
      } catch (e) {
        console.error('Delete all failed', e);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <Box p={2}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
        <Typography variant="h5">Journal</Typography>
        <Stack direction="row" spacing={1}>
          <ToggleButtonGroup size="small" exclusive value={storageMode} onChange={(_, v) => v && setStorageMode(v)} disabled={loading}>
            <ToggleButton value="local">Local</ToggleButton>
            <ToggleButton value="api">API</ToggleButton>
          </ToggleButtonGroup>
          <Tooltip title="Export as CSV">
            <Button variant="outlined" onClick={exportCsv} disabled={loading}>Export CSV</Button>
          </Tooltip>
          <Button variant="outlined" onClick={exportJson} disabled={loading}>Export JSON</Button>
          <input type="file" ref={fileInputRef} accept="application/json,.csv,text/csv" hidden onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) {
              if (f.name.toLowerCase().endsWith('.csv')) { void importCsv(f); }
              else { void importJson(f); }
              e.currentTarget.value = '';
            }
          }} />
          <Button variant="outlined" onClick={() => fileInputRef.current?.click()} disabled={loading}>Import JSON/CSV</Button>
          <Button color="warning" variant="outlined" onClick={bulkDeleteFiltered} disabled={loading || filteredNotes.length === 0}>Delete Filtered</Button>
          <Button color="error" variant="outlined" onClick={bulkDeleteAll} disabled={loading || notes.length === 0}>Delete All</Button>
        </Stack>
      </Stack>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="subtitle1" sx={{ mb: 1 }}>Search & Filter</Typography>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems={{ xs: 'stretch', sm: 'center' }}>
          <TextField label="Search" value={search} onChange={(e) => setSearch(e.target.value)} fullWidth />
          <TextField label="From" type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} InputLabelProps={{ shrink: true }} />
          <TextField label="To" type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)} InputLabelProps={{ shrink: true }} />
        </Stack>
        <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 1 }}>
          <TextField label="Filter tag" size="small" value={filterTagInput} onChange={(e) => setFilterTagInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && addFilterTag()} disabled={loading} />
          <Button variant="outlined" onClick={addFilterTag} disabled={loading}>Add</Button>
          <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap' }}>
            {filterTags.map(t => <Chip key={t} label={t} onDelete={() => removeFilterTag(t)} />)}
          </Stack>
          <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap' }}>
            {quickTags.map(t => (
              <Chip key={`quick-${t}`} label={t} variant="outlined" onClick={() => {
                if (!filterTags.includes(t)) setFilterTags([...filterTags, t]);
              }} />
            ))}
          </Stack>
        </Stack>
      </Paper>
      <Paper sx={{ p: 2, mb: 2, display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 2 }}>
            <TextField label="Title" value={title} onChange={(e) => setTitle(e.target.value)} disabled={loading} />
        <Box>
          <Stack direction="row" spacing={1} alignItems="center">
            <TextField label="Add tag" size="small" value={tagInput} onChange={(e) => setTagInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && addTag()} disabled={loading} />
            <Button variant="outlined" onClick={addTag} disabled={loading}>Add</Button>
          </Stack>
          <Stack direction="row" spacing={1} sx={{ mt: 1, flexWrap: 'wrap' }}>
            {tags.map(t => <Chip key={t} label={t} onDelete={() => removeTag(t)} disabled={loading} />)}
          </Stack>
        </Box>
            <TextField label="Body" value={body} onChange={(e) => setBody(e.target.value)} multiline minRows={4} sx={{ gridColumn: '1 / -1' }} disabled={loading} />
        <Box sx={{ gridColumn: '1 / -1', textAlign: 'right' }}>
            <Button variant="contained" onClick={addNote} disabled={loading}>Save Note</Button>
        </Box>
      </Paper>
  <Stack spacing={2}>
        {filteredNotes.map(n => (
          <Paper key={n.id} sx={{ p: 2 }}>
            {editingId === n.id ? (
              <>
                <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                  <Typography variant="subtitle2" color="text.secondary">Editing • {new Date(n.date).toLocaleString()}</Typography>
                  <Stack direction="row" spacing={1}>
                    <IconButton color="primary" onClick={saveEdit} aria-label="save" disabled={loading}><SaveIcon /></IconButton>
                    <IconButton color="inherit" onClick={cancelEdit} aria-label="cancel" disabled={loading}><CancelIcon /></IconButton>
                  </Stack>
                </Stack>
                <TextField label="Title" value={editTitle} onChange={(e) => setEditTitle(e.target.value)} fullWidth sx={{ mb: 1 }} disabled={loading} />
                <TextField label="Body" value={editBody} onChange={(e) => setEditBody(e.target.value)} multiline minRows={4} fullWidth disabled={loading} />
                <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 1 }}>
                  <TextField label="Add tag" size="small" value={editTagInput} onChange={(e) => setEditTagInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && addEditTag()} disabled={loading} />
                  <Button variant="outlined" onClick={addEditTag} disabled={loading}>Add</Button>
                  <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap' }}>
                    {editTags.map(t => <Chip key={t} label={t} onDelete={() => removeEditTag(t)} disabled={loading} />)}
                  </Stack>
                </Stack>
              </>
            ) : (
              <>
                <Stack direction="row" justifyContent="space-between" alignItems="center">
                  <Typography variant="h6">{n.title || 'Untitled'}</Typography>
                  <Stack direction="row" spacing={1}>
                    <IconButton color="primary" onClick={() => startEdit(n)} aria-label="edit" disabled={loading}><EditIcon /></IconButton>
                    <Button size="small" color="error" onClick={() => removeNote(n.id)} disabled={loading}>Delete</Button>
                  </Stack>
                </Stack>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>{new Date(n.date).toLocaleString()}</Typography>
                <Typography sx={{ whiteSpace: 'pre-wrap' }}>{n.body}</Typography>
                <Stack direction="row" spacing={1} sx={{ mt: 1, flexWrap: 'wrap' }}>
                  {n.tags.map(t => <Chip key={t} label={t} />)}
                </Stack>
              </>
            )}
          </Paper>
        ))}
      </Stack>
    </Box>
  );
};

export default Journal;
