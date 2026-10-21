import { useState, type FormEvent } from 'react'

type Person = { id_person: number; name: string; email: string }
type Notice = { text: string; error?: boolean }
type Conflict = { activity: string; day: string; start: string; end: string }
type Attendance = { person_id: number; name?: string; minutes: number; can_attend: boolean; reason?: string | null; conflicts?: { session: { day: string; start: string; end: string }; blocks: Conflict[] }[] }
type Proposal = { proposal_id: number; name: string; attendance: number; attending_count: number; total_people: number; explanation: string; sessions: { day: string; start: string; end: string }[]; people: Attendance[] }
type Api = <T>(path: string, options?: RequestInit) => Promise<T>

const days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
const dayNames: Record<string, string> = { MONDAY: 'Lunes', TUESDAY: 'Martes', WEDNESDAY: 'Miércoles', THURSDAY: 'Jueves', FRIDAY: 'Viernes', SATURDAY: 'Sábado', SUNDAY: 'Domingo' }

export default function ProposalPlanner({ people, notify, onAccepted, api }: { people: Person[]; notify: (value: Notice) => void; onAccepted: () => Promise<void>; api: Api }) {
  const [name, setName] = useState('')
  const [selected, setSelected] = useState<number[]>([])
  const [sessions, setSessions] = useState(1)
  const [duration, setDuration] = useState(60)
  const [minimum, setMinimum] = useState(60)
  const [slotMinutes, setSlotMinutes] = useState(5)
  const [start, setStart] = useState('08:00')
  const [end, setEnd] = useState('20:00')
  const [enabledDays, setEnabledDays] = useState(days)
  const [proposals, setProposals] = useState<Proposal[]>([])
  const [allProposals, setAllProposals] = useState<Proposal[]>([])
  const [pageOffset, setPageOffset] = useState(0)
  const pageSize = 10
  const [working, setWorking] = useState(false)

  const togglePerson = (id: number) => setSelected(current => current.includes(id) ? current.filter(value => value !== id) : [...current, id])
  const toggleDay = (day: string) => setEnabledDays(current => current.includes(day) ? current.filter(value => value !== day) : [...current, day])
  const maximumAttendance = allProposals.length ? Math.max(...allProposals.map(proposal => proposal.attending_count)) : 0
  const pageCount = allProposals.length ? Math.ceil(allProposals.length / pageSize) : 0
  const showPage = (offset: number) => {
    const safeOffset = Math.min(Math.max(0, offset), Math.max(0, (pageCount - 1) * pageSize))
    setPageOffset(safeOffset)
    setProposals(allProposals.slice(safeOffset, safeOffset + pageSize))
  }

  const generate = async (event: FormEvent) => {
    event.preventDefault()
    if (!selected.length) { notify({ text: 'Selecciona al menos una persona', error: true }); return }
    if (sessions < 1 || sessions > enabledDays.length || duration < 1 || minimum < 1 || minimum > duration || end <= start) { notify({ text: 'Revisa sesiones, duración, mínimo y rango horario', error: true }); return }
    setWorking(true); setProposals([]); setAllProposals([]); setPageOffset(0)
    try {
      const group = await api<{ id_group: number }>('/groups/', { method: 'POST', body: JSON.stringify({ name, sessions_per_week: sessions, duration_minutes: duration, minimum_attendance_minutes: minimum }) })
      await Promise.all(selected.map(person_id => api('/group-participants/', { method: 'POST', body: JSON.stringify({ group_id: group.id_group, person_id, required: true }) })))
      await Promise.all(enabledDays.map(day => api('/restrictions/', { method: 'POST', body: JSON.stringify({ group_id: group.id_group, name: `Horario permitido ${day}`, type: 'ALLOWED_HOURS', day_of_week: day, start_time: start, end_time: end }) })))
      const result = await api<Proposal[]>(`/proposals/generate/${group.id_group}?slot_minutes=${slotMinutes}`, { method: 'POST' })
      setAllProposals(result); setProposals(result.slice(0, pageSize)); setPageOffset(0)
      notify({ text: result.length ? `${result.length} alternativas válidas encontradas` : 'No existe una alternativa válida', error: !result.length })
    } catch (error) { notify({ text: error instanceof Error ? error.message : 'No se pudo generar la propuesta', error: true }) } finally { setWorking(false) }
  }

  const accept = async (proposal: Proposal) => {
    try { await api(`/proposals/${proposal.proposal_id}/accept`, { method: 'PUT' }); notify({ text: 'Propuesta aceptada y añadida a los horarios' }); await onAccepted() } catch (error) { notify({ text: error instanceof Error ? error.message : 'No se pudo aceptar la propuesta', error: true }) }
  }

  return <section className="content planner-layout">
    <form className="panel planner-form" onSubmit={generate}>
      <span className="eyebrow">REQUISITOS</span><h2>Encontrar un horario común</h2>
      <label>Nombre de la actividad<input value={name} onChange={event => setName(event.target.value)} required /></label>
      <fieldset><legend>Personas participantes <span>{selected.length} seleccionadas</span></legend><div className="participant-picker">{people.map(person => <label className={selected.includes(person.id_person) ? 'selected' : ''} key={person.id_person}><input type="checkbox" checked={selected.includes(person.id_person)} onChange={() => togglePerson(person.id_person)} /><span className="avatar small">{person.name[0]}</span><span><strong>{person.name}</strong><small>{person.email}</small></span></label>)}</div></fieldset>
      <div className="field-row"><label>Sesiones por semana<input type="number" min="1" max="7" value={sessions} onChange={event => setSessions(Number(event.target.value))} /><small>1 = sesión única</small></label><label>Duración<input type="number" min="1" step="5" value={duration} onChange={event => { const value = Number(event.target.value); setDuration(value); if (minimum > value) setMinimum(value) }} /><small>minutos</small></label><label>Mínimo de asistencia<input type="number" min="1" max={duration} value={minimum} onChange={event => setMinimum(Number(event.target.value))} /><small>por sesión</small></label></div>
      <label>Precisión de búsqueda<select value={slotMinutes} onChange={event => setSlotMinutes(Number(event.target.value))}><option value="5">5 minutos</option><option value="10">10 minutos</option><option value="15">15 minutos</option><option value="20">20 minutos</option></select><small>La búsqueda cubre de 06:00 a 21:00.</small></label>
      <fieldset><legend>Días e intervalo permitidos</legend><div className="attendance-list">{days.map(day => <label className="check" key={day}><input type="checkbox" checked={enabledDays.includes(day)} onChange={() => toggleDay(day)} /> {dayNames[day]}</label>)}</div><div className="common-range"><label>Desde<input type="time" value={start} onChange={event => setStart(event.target.value)} /></label><label>Hasta<input type="time" value={end} onChange={event => setEnd(event.target.value)} /></label></div></fieldset>
      <button className="primary generate" disabled={working}>{working ? 'Analizando agendas…' : 'Encontrar todas las alternativas'}</button>
    </form>
    <div className="results"><div className="results-intro"><span className="eyebrow">PROPUESTAS</span><h2>{proposals.length ? 'Alternativas ordenadas por asistencia' : 'Aquí aparecerán las opciones'}</h2><p>Primero se muestran todas las propuestas con asistencia completa; si no existen, se muestran las que alcanzan el máximo posible.</p></div>{proposals.map((proposal, index) => <article className="proposal" key={proposal.proposal_id}><div className="proposal-rank">#{index + 1}</div><div className="proposal-head"><div><strong>{proposal.name}</strong><span>{proposal.attending_count}/{proposal.total_people} personas pueden asistir ({Math.round(proposal.attendance * 100)}%)</span></div></div><p>{proposal.explanation}</p><div className="session-list">{proposal.sessions.map(session => <div key={`${session.day}-${session.start}`}><span>{dayNames[session.day]}</span><strong>{session.start} — {session.end}</strong><small>{duration} minutos</small></div>)}</div><div className="attendance-list">{proposal.people.map(person => <span className={person.can_attend ? 'can' : 'cannot'} key={person.person_id}><i>{person.can_attend ? '✓' : '!'}</i>{person.name ?? `Persona ${person.person_id}`} · {person.minutes} min</span>)}</div>{proposal.people.filter(person => !person.can_attend).map(person => <details key={`details-${person.person_id}`}><summary>{person.name ?? `Persona ${person.person_id}`}: {person.reason}</summary>{(person.conflicts ?? []).flatMap(conflict => conflict.blocks).map((block, conflictIndex) => <div key={conflictIndex}>{block.activity} · {block.day} · {block.start}–{block.end}</div>)}</details>)}<button className="primary" onClick={() => void accept(proposal)}>Aceptar y añadir a horarios</button></article>)}{!proposals.length && <div className="empty-state">Genera una búsqueda para ver alternativas.</div>}</div>
    {allProposals.length > 0 && <div className="proposal-summary"><span>{allProposals.length} propuestas válidas</span><span>Máximo de asistentes: {maximumAttendance}/{allProposals[0].total_people}</span><span>Página {Math.floor(pageOffset / pageSize) + 1} de {pageCount}</span>{pageCount > 1 && <nav className="proposal-pagination" aria-label="Paginación de propuestas"><button type="button" className="secondary" disabled={pageOffset === 0} onClick={() => showPage(pageOffset - pageSize)}>Anterior</button><span>{pageOffset + 1}–{Math.min(pageOffset + pageSize, allProposals.length)} de {allProposals.length}</span><button type="button" className="secondary" disabled={pageOffset + pageSize >= allProposals.length} onClick={() => showPage(pageOffset + pageSize)}>Siguiente</button></nav>}</div>}
  </section>
}
