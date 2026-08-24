import { useEffect, useMemo, useState, type FormEvent } from 'react'
import './App.css'

type View = 'personas' | 'horarios' | 'planificar'
type Person = { id_person: number; name: string; email: string; active: boolean }
type Activity = { id_activity: number; person_id: number; name: string; type: string; description?: string }
type Block = { id_block: number; activity_id: number; day_of_week: string; start_time: string; end_time: string }
type ImportRow = { activity: string; day: string; start: string; end: string }
type ProposalPerson = { person_id: number; minutes: number; minutes_per_session: number[]; can_attend: boolean }
type Proposal = { proposal_id: number; name: string; score: number; attendance: number; sessions: { day: string; start: string; end: string }[]; people: ProposalPerson[] }
type DayRange = { enabled: boolean; start: string; end: string }

const days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
const dayNames: Record<string, string> = { MONDAY: 'Lunes', TUESDAY: 'Martes', WEDNESDAY: 'Miércoles', THURSDAY: 'Jueves', FRIDAY: 'Viernes', SATURDAY: 'Sábado', SUNDAY: 'Domingo' }
const apiBase = import.meta.env.VITE_API_URL || '/api'

async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBase}${path}`, {
    ...options,
    headers: options?.body instanceof FormData ? options.headers : { 'Content-Type': 'application/json', ...options?.headers },
  })
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: 'Error de conexión' }))
    throw new Error(typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail))
  }
  return response.status === 204 ? (undefined as T) : response.json()
}

function App() {
  const [view, setView] = useState<View>('personas')
  const [people, setPeople] = useState<Person[]>([])
  const [activities, setActivities] = useState<Activity[]>([])
  const [blocks, setBlocks] = useState<Block[]>([])
  const [selectedPerson, setSelectedPerson] = useState<number | null>(null)
  const [notice, setNotice] = useState<{ text: string; error?: boolean } | null>(null)
  const [loading, setLoading] = useState(true)

  const reload = async () => {
    try {
      const [personsData, activitiesData, blocksData] = await Promise.all([
        api<Person[]>('/people/'), api<Activity[]>('/activities/'), api<Block[]>('/time-blocks/'),
      ])
      setPeople(personsData)
      setActivities(activitiesData)
      setBlocks(blocksData)
      setSelectedPerson(current => current ?? personsData[0]?.id_person ?? null)
    } catch (error) {
      setNotice({ text: error instanceof Error ? error.message : 'No se pudo cargar la aplicación', error: true })
    } finally { setLoading(false) }
  }

  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => { void reload() }, [])
  useEffect(() => {
    if (!notice) return
    const timer = window.setTimeout(() => setNotice(null), 4500)
    return () => window.clearTimeout(timer)
  }, [notice])

  const selected = people.find(person => person.id_person === selectedPerson)
  const personActivities = activities.filter(activity => activity.person_id === selectedPerson)
  const activityIds = new Set(personActivities.map(activity => activity.id_activity))
  const personBlocks = blocks.filter(block => activityIds.has(block.activity_id))

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">OH</span><span><strong>Organizador</strong><small>de horarios</small></span></div>
        <nav>
          <NavButton active={view === 'personas'} icon="♙" label="Personas" onClick={() => setView('personas')} count={people.length} />
          <NavButton active={view === 'horarios'} icon="▦" label="Horarios" onClick={() => setView('horarios')} />
          <NavButton active={view === 'planificar'} icon="✦" label="Planificar actividad" onClick={() => setView('planificar')} />
        </nav>
      </aside>

      <main>
        <header className="topbar"><div><span className="eyebrow">ORGANIZADOR DE HORARIOS</span><h1>{view === 'personas' ? 'Personas' : view === 'horarios' ? 'Horarios individuales' : 'Planificar una actividad'}</h1></div><button className="primary" onClick={() => setView('planificar')}>＋ Nueva actividad</button></header>
        {notice && <div className={`toast ${notice.error ? 'error' : ''}`}>{notice.text}</div>}
        {loading ? <div className="empty-state"><span className="spinner" /> Cargando espacio de trabajo…</div> : (
          <>
            {view === 'personas' && <PeoplePanel people={people} onChanged={reload} notify={setNotice} onOpenSchedule={id => { setSelectedPerson(id); setView('horarios') }} />}
            {view === 'horarios' && <SchedulesPanel people={people} selected={selected} selectedPerson={selectedPerson} setSelectedPerson={setSelectedPerson} activities={personActivities} blocks={personBlocks} onChanged={reload} notify={setNotice} />}
            {view === 'planificar' && <Planner people={people.filter(person => person.active)} notify={setNotice} onAccepted={async () => { await reload(); setView('horarios') }} />}
          </>
        )}
      </main>
    </div>
  )
}

function NavButton({ active, icon, label, count, onClick }: { active: boolean; icon: string; label: string; count?: number; onClick: () => void }) {
  return <button className={active ? 'nav-item active' : 'nav-item'} onClick={onClick}><span>{icon}</span>{label}{count !== undefined && <b>{count}</b>}</button>
}

function PeoplePanel({ people, onChanged, notify, onOpenSchedule }: { people: Person[]; onChanged: () => Promise<void>; notify: (value: { text: string; error?: boolean }) => void; onOpenSchedule: (id: number) => void }) {
  const [editing, setEditing] = useState<Person | null>(null)
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const submit = async (event: FormEvent) => {
    event.preventDefault()
    try {
      await api(editing ? `/people/${editing.id_person}` : '/people/', { method: editing ? 'PUT' : 'POST', body: JSON.stringify({ name, email }) })
      setName(''); setEmail(''); setEditing(null); await onChanged(); notify({ text: editing ? 'Persona actualizada' : 'Persona agregada' })
    } catch (error) { notify({ text: (error as Error).message, error: true }) }
  }
  const startEdit = (person: Person) => { setEditing(person); setName(person.name); setEmail(person.email) }
  const remove = async (person: Person) => {
    if (!window.confirm(`¿Eliminar a ${person.name} y todo su horario?`)) return
    try { await api(`/people/${person.id_person}`, { method: 'DELETE' }); await onChanged(); notify({ text: 'Persona eliminada' }) } catch (error) { notify({ text: (error as Error).message, error: true }) }
  }
  return <section className="content two-column"><div className="panel"><div className="panel-title"><div><span className="eyebrow">EQUIPO</span><h2>{people.length} personas</h2></div></div><div className="people-list">{people.map(person => <article key={person.id_person}><div className="avatar">{person.name.split(' ').map(part => part[0]).slice(0, 2).join('').toUpperCase()}</div><div><strong>{person.name}</strong><span>{person.email}</span></div><span className={person.active ? 'status' : 'status inactive'}>{person.active ? 'Activa' : 'Inactiva'}</span><button title="Ver horario" onClick={() => onOpenSchedule(person.id_person)}>▦</button><button title="Editar" onClick={() => startEdit(person)}>✎</button><button className="danger-icon" title="Eliminar" onClick={() => void remove(person)}>×</button></article>)}{people.length === 0 && <div className="empty-state">Aún no has agregado personas.</div>}</div></div><form className="panel form-card" onSubmit={submit}><span className="eyebrow">{editing ? 'EDITAR' : 'NUEVA PERSONA'}</span><h2>{editing ? 'Actualiza sus datos' : 'Agrega a alguien'}</h2><label>Nombre completo<input value={name} onChange={event => setName(event.target.value)} placeholder="Ej. Ana Martínez" required /></label><label>Correo electrónico<input type="email" value={email} onChange={event => setEmail(event.target.value)} placeholder="ana@ejemplo.com" required /></label><button className="primary" type="submit">{editing ? 'Guardar cambios' : 'Agregar persona'}</button>{editing && <button className="link-button" type="button" onClick={() => { setEditing(null); setName(''); setEmail('') }}>Cancelar edición</button>}</form></section>
}

function SchedulesPanel({ people, selected, selectedPerson, setSelectedPerson, activities, blocks, onChanged, notify }: { people: Person[]; selected?: Person; selectedPerson: number | null; setSelectedPerson: (id: number) => void; activities: Activity[]; blocks: Block[]; onChanged: () => Promise<void>; notify: (value: { text: string; error?: boolean }) => void }) {
  const [activityName, setActivityName] = useState('')
  const [day, setDay] = useState('MONDAY')
  const [start, setStart] = useState('08:00')
  const [end, setEnd] = useState('09:00')
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<ImportRow[]>([])
  const [replace, setReplace] = useState(false)
  const [importing, setImporting] = useState(false)
  const names = new Map(activities.map(activity => [activity.id_activity, activity.name]))

  const addBlock = async (event: FormEvent) => {
    event.preventDefault(); if (!selectedPerson) return
    try {
      const activity = await api<Activity>('/activities/', { method: 'POST', body: JSON.stringify({ person_id: selectedPerson, name: activityName, type: 'MANUAL' }) })
      await api('/time-blocks/', { method: 'POST', body: JSON.stringify({ activity_id: activity.id_activity, day_of_week: day, start_time: start, end_time: end }) })
      setActivityName(''); await onChanged(); notify({ text: 'Bloque agregado al horario' })
    } catch (error) { notify({ text: (error as Error).message, error: true }) }
  }
  const previewFile = async () => {
    if (!file) return; setImporting(true)
    const data = new FormData(); data.append('file', file)
    try {
      const result = await api<{ success: boolean; schedule: ImportRow[]; errors: { message?: string }[] }>('/import/preview', { method: 'POST', body: data })
      setPreview(result.schedule.map(row => ({ ...row, start: row.start.slice(0, 5), end: row.end.slice(0, 5) })))
      if (!result.success) notify({ text: result.errors[0]?.message ?? 'Revisa las filas antes de guardar' })
    } catch (error) { notify({ text: (error as Error).message, error: true }) } finally { setImporting(false) }
  }
  const saveImport = async () => {
    if (!selectedPerson) return
    try { await api('/import/save', { method: 'POST', body: JSON.stringify({ person_id: selectedPerson, schedule: preview, replace_existing: replace }) }); setPreview([]); setFile(null); await onChanged(); notify({ text: 'Horario importado correctamente' }) } catch (error) { notify({ text: (error as Error).message, error: true }) }
  }
  const deleteBlock = async (id: number) => { try { await api(`/time-blocks/${id}`, { method: 'DELETE' }); await onChanged() } catch (error) { notify({ text: (error as Error).message, error: true }) } }
  const editBlock = async (block: Block) => {
    const newStart = window.prompt('Hora de inicio (HH:MM)', block.start_time.slice(0, 5)); if (!newStart) return
    const newEnd = window.prompt('Hora de fin (HH:MM)', block.end_time.slice(0, 5)); if (!newEnd) return
    try { await api(`/time-blocks/${block.id_block}`, { method: 'PUT', body: JSON.stringify({ day_of_week: block.day_of_week, start_time: newStart, end_time: newEnd }) }); await onChanged(); notify({ text: 'Bloque actualizado' }) } catch (error) { notify({ text: (error as Error).message, error: true }) }
  }
  return <section className="content">
    <div className="schedule-toolbar">
      <label>Horario de<select value={selectedPerson ?? ''} onChange={event => setSelectedPerson(Number(event.target.value))}><option value="" disabled>Selecciona una persona</option>{people.map(person => <option value={person.id_person} key={person.id_person}>{person.name}</option>)}</select></label>
      <div>{selected && <><div className="avatar small">{selected.name[0]}</div><span><strong>{selected.name}</strong><small>{blocks.length} bloques ocupados · datos guardados en SQLite</small></span></>}</div>
    </div>
    {!selected ? <div className="empty-state">Agrega una persona para comenzar su horario.</div> : <>
      <ScheduleGrid blocks={blocks} names={names} onEdit={editBlock} onDelete={deleteBlock} />
      <div className="schedule-forms">
        <form className="panel compact-form" onSubmit={addBlock}><span className="eyebrow">AGREGAR MANUALMENTE</span><h3>Nuevo bloque ocupado</h3><label>Actividad<input value={activityName} onChange={event => setActivityName(event.target.value)} placeholder="Clase, trabajo, reunión…" required /></label><div className="field-row"><label>Día<select value={day} onChange={event => setDay(event.target.value)}>{days.map(value => <option value={value} key={value}>{dayNames[value]}</option>)}</select></label><label>Desde<input type="time" value={start} onChange={event => setStart(event.target.value)} required /></label><label>Hasta<input type="time" value={end} onChange={event => setEnd(event.target.value)} required /></label></div><button className="primary">Agregar bloque</button></form>
        <div className="panel import-card"><span className="eyebrow">IMPORTAR DOCUMENTO</span><h3>Sube un horario</h3><p>Excel, CSV, PDF, PNG o JPG. Podrás revisar cada fila antes de guardarla.</p><label className="drop-zone"><span>⇧</span><strong>{file?.name ?? 'Selecciona un archivo'}</strong><small>Formatos admitidos: .xlsx, .csv, .pdf, .png, .jpg</small><input type="file" accept=".xlsx,.csv,.pdf,.png,.jpg,.jpeg" onChange={event => setFile(event.target.files?.[0] ?? null)} /></label><button className="secondary" disabled={!file || importing} onClick={() => void previewFile()}>{importing ? 'Analizando…' : 'Analizar archivo'}</button></div>
      </div>
      {preview.length > 0 && <ImportEditor rows={preview} setRows={setPreview} replace={replace} setReplace={setReplace} onSave={saveImport} />}
    </>}
  </section>
}

function toMinutes(value: string) {
  const [hour, minute] = value.slice(0, 5).split(':').map(Number)
  return hour * 60 + minute
}

function ScheduleGrid({ blocks, names, onEdit, onDelete }: { blocks: Block[]; names: Map<number, string>; onEdit: (block: Block) => Promise<void>; onDelete: (id: number) => Promise<void> }) {
  const [intervalSetting, setIntervalSetting] = useState('auto')
  const [automaticRange, setAutomaticRange] = useState(true)
  const [manualStart, setManualStart] = useState(6)
  const [manualEnd, setManualEnd] = useState(22)
  const boundaries = blocks.flatMap(block => [toMinutes(block.start_time), toMinutes(block.end_time)])
  const durations = blocks.map(block => toMinutes(block.end_time) - toMinutes(block.start_time))
  const automaticInterval = [60, 40, 30, 20, 15, 10].find(value => [...boundaries, ...durations].every(item => item % value === 0)) ?? 20
  const interval = intervalSetting === 'auto' ? automaticInterval : Number(intervalSetting)
  const startMinute = automaticRange && boundaries.length ? Math.max(0, Math.floor((Math.min(...boundaries) - interval) / interval) * interval) : manualStart * 60
  const endMinute = automaticRange && boundaries.length ? Math.min(1440, Math.ceil((Math.max(...boundaries) + interval) / interval) * interval) : manualEnd * 60
  const safeEnd = Math.max(endMinute, startMinute + interval)
  const slotCount = Math.ceil((safeEnd - startMinute) / interval)
  const rowHeight = 34
  const labels = Array.from({ length: slotCount + 1 }, (_, index) => startMinute + index * interval)
  const format = (minutes: number) => `${String(Math.floor(minutes / 60)).padStart(2, '0')}:${String(minutes % 60).padStart(2, '0')}`

  return <div className="calendar-panel panel">
    <div className="calendar-controls"><div><span className="eyebrow">CUADRÍCULA SEMANAL</span><h3>Ocupación y espacios disponibles</h3></div><label>Intervalo<select value={intervalSetting} onChange={event => setIntervalSetting(event.target.value)}><option value="auto">Automático ({automaticInterval} min)</option>{[10, 15, 20, 30, 40, 60].map(value => <option value={value} key={value}>{value} minutos</option>)}</select></label><label className="check"><input type="checkbox" checked={automaticRange} onChange={event => setAutomaticRange(event.target.checked)} /> Rango automático</label>{!automaticRange && <><label>Desde<input type="number" min="0" max="23" value={manualStart} onChange={event => setManualStart(Number(event.target.value))} /></label><label>Hasta<input type="number" min="1" max="24" value={manualEnd} onChange={event => setManualEnd(Number(event.target.value))} /></label></>}</div>
    <div className="calendar-scroll">
      <div className="calendar-grid-head"><span>Hora</span>{days.map(day => <strong key={day}>{dayNames[day]}</strong>)}</div>
      <div className="calendar-grid-body" style={{ height: slotCount * rowHeight }}>
        <div className="time-axis">{labels.slice(0, -1).map((value, index) => <span key={value} style={{ top: index * rowHeight }}>{format(value)}</span>)}</div>
        {days.map(day => <div className="calendar-lane" key={day} style={{ backgroundSize: `100% ${rowHeight}px` }}>{blocks.filter(block => block.day_of_week === day).map(block => {
          const eventStart = Math.max(startMinute, toMinutes(block.start_time))
          const eventEnd = Math.min(safeEnd, toMinutes(block.end_time))
          if (eventEnd <= eventStart) return null
          return <article className="calendar-event" key={block.id_block} style={{ top: ((eventStart - startMinute) / interval) * rowHeight + 2, height: Math.max(26, ((eventEnd - eventStart) / interval) * rowHeight - 4) }}><small>{block.start_time.slice(0, 5)}–{block.end_time.slice(0, 5)}</small><strong>{names.get(block.activity_id) ?? 'Actividad'}</strong><div><button onClick={() => void onEdit(block)}>Editar</button><button onClick={() => void onDelete(block.id_block)}>×</button></div></article>
        })}</div>)}
      </div>
    </div>
    <div className="calendar-legend"><span><i className="busy" /> Ocupado</span><span><i /> Disponible</span></div>
  </div>
}

function ImportEditor({ rows, setRows, replace, setReplace, onSave }: { rows: ImportRow[]; setRows: (rows: ImportRow[]) => void; replace: boolean; setReplace: (value: boolean) => void; onSave: () => Promise<void> }) {
  const update = (index: number, key: keyof ImportRow, value: string) => setRows(rows.map((row, rowIndex) => rowIndex === index ? { ...row, [key]: value } : row))
  return <div className="panel import-editor"><div className="panel-title"><div><span className="eyebrow">VISTA PREVIA EDITABLE</span><h3>{rows.length} bloques detectados</h3></div><label className="check"><input type="checkbox" checked={replace} onChange={event => setReplace(event.target.checked)} /> Reemplazar horario actual</label></div><div className="table-wrap"><table><thead><tr><th>Actividad</th><th>Día</th><th>Inicio</th><th>Fin</th><th /></tr></thead><tbody>{rows.map((row, index) => <tr key={index}><td><input value={row.activity} onChange={event => update(index, 'activity', event.target.value)} /></td><td><select value={row.day} onChange={event => update(index, 'day', event.target.value)}>{days.map(value => <option value={value} key={value}>{dayNames[value]}</option>)}</select></td><td><input type="time" value={row.start.slice(0, 5)} onChange={event => update(index, 'start', event.target.value)} /></td><td><input type="time" value={row.end.slice(0, 5)} onChange={event => update(index, 'end', event.target.value)} /></td><td><button onClick={() => setRows(rows.filter((_, rowIndex) => rowIndex !== index))}>×</button></td></tr>)}</tbody></table></div><button className="primary" onClick={() => void onSave()}>Guardar horario importado</button></div>
}

function Planner({ people, notify, onAccepted }: { people: Person[]; notify: (value: { text: string; error?: boolean }) => void; onAccepted: () => Promise<void> }) {
  const [name, setName] = useState('')
  const [selected, setSelected] = useState<number[]>([])
  const [sessions, setSessions] = useState(2)
  const [duration, setDuration] = useState(80)
  const [minimum, setMinimum] = useState(40)
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [rangeMode, setRangeMode] = useState<'same' | 'daily'>('same')
  const [commonStart, setCommonStart] = useState('08:00')
  const [commonEnd, setCommonEnd] = useState('20:00')
  const [dayRanges, setDayRanges] = useState<Record<string, DayRange>>(() => Object.fromEntries(days.map(day => [day, { enabled: true, start: '08:00', end: '20:00' }])))
  const [proposals, setProposals] = useState<Proposal[]>([])
  const [working, setWorking] = useState(false)
  const peopleById = useMemo(() => new Map(people.map(person => [person.id_person, person])), [people])
  const toggle = (id: number) => setSelected(current => current.includes(id) ? current.filter(value => value !== id) : [...current, id])
  const updateDayRange = (day: string, changes: Partial<DayRange>) => setDayRanges(current => ({ ...current, [day]: { ...current[day], ...changes } }))
  const generate = async (event: FormEvent) => {
    event.preventDefault()
    if (selected.length === 0) { notify({ text: 'Selecciona al menos una persona', error: true }); return }
    const activeRanges = rangeMode === 'same' ? [{ start: commonStart, end: commonEnd }] : Object.values(dayRanges).filter(range => range.enabled)
    if (!activeRanges.length || activeRanges.some(range => range.end <= range.start)) { notify({ text: 'Revisa los rangos de horario permitidos', error: true }); return }
    setWorking(true); setProposals([])
    try {
      const group = await api<{ id_group: number }>('/groups/', { method: 'POST', body: JSON.stringify({ name, sessions_per_week: sessions, duration_minutes: duration, minimum_attendance_minutes: minimum, start_date: startDate || null, end_date: endDate || null }) })
      await Promise.all(selected.map(personId => api('/group-participants/', { method: 'POST', body: JSON.stringify({ group_id: group.id_group, person_id: personId, required: true }) })))
      const restrictions = rangeMode === 'same'
        ? [{ group_id: group.id_group, name: 'Rango diario', type: 'ALLOWED_HOURS', start_time: commonStart, end_time: commonEnd }]
        : days.map(day => dayRanges[day].enabled
          ? { group_id: group.id_group, name: `Rango ${day}`, type: 'ALLOWED_HOURS', day_of_week: day, start_time: dayRanges[day].start, end_time: dayRanges[day].end }
          : { group_id: group.id_group, name: `Día no permitido ${day}`, type: 'FORBIDDEN_DAY', day_of_week: day })
      await Promise.all(restrictions.map(restriction => api('/restrictions/', { method: 'POST', body: JSON.stringify(restriction) })))
      const result = await api<Proposal[]>(`/proposals/generate/${group.id_group}`, { method: 'POST' })
      setProposals(result); notify({ text: `${result.length} opciones encontradas` })
    } catch (error) { notify({ text: (error as Error).message, error: true }) } finally { setWorking(false) }
  }
  const accept = async (proposal: Proposal) => {
    try { await api(`/proposals/${proposal.proposal_id}/accept`, { method: 'PUT' }); notify({ text: 'Actividad añadida a los horarios seleccionados' }); await onAccepted() } catch (error) { notify({ text: (error as Error).message, error: true }) }
  }
  return <section className="content planner-layout">
    <form className="panel planner-form" onSubmit={generate}>
      <span className="eyebrow">REQUISITOS</span><h2>¿Qué quieres coordinar?</h2>
      <label>Nombre de la actividad<input value={name} onChange={event => setName(event.target.value)} placeholder="Ej. Ensayo general" required /></label>
      <fieldset><legend>Personas participantes <span>{selected.length} seleccionadas</span></legend><div className="participant-picker">{people.map(person => <label className={selected.includes(person.id_person) ? 'selected' : ''} key={person.id_person}><input type="checkbox" checked={selected.includes(person.id_person)} onChange={() => toggle(person.id_person)} /><span className="avatar small">{person.name[0]}</span><span><strong>{person.name}</strong><small>{person.email}</small></span><i>✓</i></label>)}</div></fieldset>
      <div className="field-row"><label>Veces por semana<input type="number" min="1" max="7" value={sessions} onChange={event => setSessions(Number(event.target.value))} /></label><label>Duración por sesión<input type="number" min="20" step="20" value={duration} onChange={event => setDuration(Number(event.target.value))} /><small>minutos</small></label><label>Mínimo por persona<input type="number" min="1" max={duration} value={minimum} onChange={event => setMinimum(Number(event.target.value))} /><small>por sesión</small></label></div>
      <div className="field-row"><label>Desde (opcional)<input type="date" value={startDate} onChange={event => setStartDate(event.target.value)} /></label><label>Hasta (opcional)<input type="date" value={endDate} min={startDate} onChange={event => setEndDate(event.target.value)} /></label></div>
      <fieldset className="range-requirements"><legend>Horario permitido para la actividad</legend><p>Las propuestas se generarán únicamente dentro de estos rangos.</p><div className="range-mode"><button type="button" className={rangeMode === 'same' ? 'active' : ''} onClick={() => setRangeMode('same')}>Mismo horario diario</button><button type="button" className={rangeMode === 'daily' ? 'active' : ''} onClick={() => setRangeMode('daily')}>Diferente por día</button></div>
        {rangeMode === 'same' ? <div className="common-range"><label>Desde<input type="time" value={commonStart} onChange={event => setCommonStart(event.target.value)} /></label><span>hasta</span><label>Hasta<input type="time" value={commonEnd} onChange={event => setCommonEnd(event.target.value)} /></label></div> : <div className="day-range-list">{days.map(day => <div className={dayRanges[day].enabled ? 'day-range' : 'day-range disabled'} key={day}><label className="day-toggle"><input type="checkbox" checked={dayRanges[day].enabled} onChange={event => updateDayRange(day, { enabled: event.target.checked })} /><strong>{dayNames[day]}</strong></label>{dayRanges[day].enabled ? <><input aria-label={`Inicio ${dayNames[day]}`} type="time" value={dayRanges[day].start} onChange={event => updateDayRange(day, { start: event.target.value })} /><span>—</span><input aria-label={`Fin ${dayNames[day]}`} type="time" value={dayRanges[day].end} onChange={event => updateDayRange(day, { end: event.target.value })} /></> : <small>No disponible</small>}</div>)}</div>}
      </fieldset>
      <button className="primary generate" disabled={working}>{working ? <><span className="spinner" /> Comparando agendas…</> : <>✦ Encontrar mejores opciones</>}</button>
    </form>
    <div className="results"><div className="results-intro"><span className="eyebrow">PROPUESTAS</span><h2>{proposals.length ? 'Mejores coincidencias' : 'Aquí aparecerán las opciones'}</h2><p>{proposals.length ? 'Ordenadas por asistencia y minutos disponibles.' : 'Completa los requisitos y analizaremos los horarios seleccionados.'}</p></div>{proposals.map((proposal, index) => <article className="proposal" key={proposal.proposal_id}><div className="proposal-rank">#{index + 1}</div><div className="proposal-head"><div><strong>{proposal.name}</strong><span>{Math.round(proposal.attendance * 100)}% puede cumplir el mínimo</span></div><b>{proposal.score.toFixed(1)} pts</b></div><div className="session-list">{proposal.sessions.map(session => <div key={`${session.day}${session.start}`}><span>{dayNames[session.day]}</span><strong>{session.start} — {session.end}</strong><small>{duration} min</small></div>)}</div><div className="attendance-list">{proposal.people.map(item => <span className={item.can_attend ? 'can' : 'cannot'} key={item.person_id} title={`${item.minutes} minutos disponibles`}><i>{item.can_attend ? '✓' : '!'}</i>{peopleById.get(item.person_id)?.name ?? `Persona ${item.person_id}`} · {item.minutes} min</span>)}</div><button className="primary" onClick={() => void accept(proposal)}>Aceptar y añadir a horarios</button></article>)}{proposals.length === 0 && <div className="result-placeholder"><span>✦</span><div className="orbit one" /><div className="orbit two" /></div>}</div>
  </section>
}

export default App
