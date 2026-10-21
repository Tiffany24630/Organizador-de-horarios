export type ScheduleBlock = {
  id_block: number
  activity_id: number
  day_of_week: string
  start_time: string
  end_time: string
  room?: string | null
}

export type VisualScheduleBlock = ScheduleBlock & { sourceBlocks: ScheduleBlock[] }

export function timeToMinutes(value: string): number {
  const [hour, minute] = value.slice(0, 5).split(':').map(Number)
  return hour * 60 + minute
}

/** Display-only transformation; source records are preserved for safe edits/deletes. */
export function groupScheduleBlocks(blocks: ScheduleBlock[]): VisualScheduleBlock[] {
  const groups = new Map<string, ScheduleBlock[]>()
  for (const block of blocks) {
    const room = block.room?.trim().toLocaleLowerCase() ?? ''
    const key = `${block.activity_id}|${block.day_of_week}|${room}`
    groups.set(key, [...(groups.get(key) ?? []), block])
  }

  const result: VisualScheduleBlock[] = []
  for (const group of groups.values()) {
    const ordered = [...group].sort((a, b) => timeToMinutes(a.start_time) - timeToMinutes(b.start_time))
    let current: VisualScheduleBlock | undefined
    for (const source of ordered) {
      if (!current) {
        current = { ...source, sourceBlocks: [source] }
        continue
      }
      const gap = timeToMinutes(source.start_time) - timeToMinutes(current.end_time)
      if (gap <= 5) {
        current = {
          ...current,
          end_time: timeToMinutes(source.end_time) > timeToMinutes(current.end_time) ? source.end_time : current.end_time,
          sourceBlocks: [...current.sourceBlocks, source],
        }
      } else {
        result.push(current)
        current = { ...source, sourceBlocks: [source] }
      }
    }
    if (current) result.push(current)
  }
  return result.sort((a, b) => a.day_of_week.localeCompare(b.day_of_week) || timeToMinutes(a.start_time) - timeToMinutes(b.start_time))
}
