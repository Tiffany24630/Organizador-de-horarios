import test from 'node:test'
import assert from 'node:assert/strict'
import { findBlockConflicts, validateEditForm } from '../src/timeBlockEditing.ts'

const block = (id_block: number, start_time: string, end_time: string, day_of_week = 'MONDAY') => ({ id_block, activity_id: 1, day_of_week, start_time, end_time })

test('valida que la hora final sea posterior', () => {
  assert.equal(validateEditForm({ activityName: 'Clase', day: 'MONDAY', start: '10:00', end: '10:00' }), 'La hora final debe ser posterior a la hora inicial.')
})

test('detecta solapamientos y no considera el propio registro', () => {
  const current = block(1, '10:00', '11:00')
  assert.deepEqual(findBlockConflicts(current, [current, block(2, '10:30', '11:30'), block(3, '11:00', '12:00')]).map(item => item.id_block), [2])
})

test('cancelar no transforma el registro original', () => {
  const current = block(1, '10:00', '11:00')
  const draft = { ...current, start_time: '12:00' }
  assert.equal(current.start_time, '10:00')
  assert.equal(draft.start_time, '12:00')
})
