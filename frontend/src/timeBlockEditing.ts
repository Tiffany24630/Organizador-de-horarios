export type EditableBlock = {
  id_block: number
  day_of_week: string
  start_time: string
  end_time: string
}

export type EditForm = { activityName: string; day: string; start: string; end: string }

const minutes = (value: string) => {
  const [hour, minute] = value.slice(0, 5).split(':').map(Number)
  return hour * 60 + minute
}

export function validateEditForm(form: EditForm): string | null {
  if (!form.activityName.trim()) return 'El nombre de la actividad es obligatorio.'
  if (!form.day) return 'Selecciona un día de la semana.'
  if (!/^\d{2}:\d{2}$/.test(form.start) || !/^\d{2}:\d{2}$/.test(form.end)) return 'Usa horas válidas en formato HH:MM.'
  if (minutes(form.end) <= minutes(form.start)) return 'La hora final debe ser posterior a la hora inicial.'
  return null
}

export function findBlockConflicts<T extends EditableBlock>(edit: T, blocks: T[]): T[] {
  const start = minutes(edit.start_time)
  const end = minutes(edit.end_time)
  return blocks.filter(block => block.id_block !== edit.id_block && block.day_of_week === edit.day_of_week && minutes(block.start_time) < end && minutes(block.end_time) > start)
}
