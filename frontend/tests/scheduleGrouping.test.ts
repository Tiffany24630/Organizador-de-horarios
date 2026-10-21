import test from 'node:test'
import assert from 'node:assert/strict'
import { groupScheduleBlocks } from '../src/scheduleGrouping.ts'

const block = (id_block: number, activity_id: number, start_time: string, end_time: string, room?: string) => ({
  id_block, activity_id, day_of_week: 'MONDAY', start_time, end_time, room,
})

test('groups consecutive periods and keeps source records', () => {
  const source = [block(1, 10, '08:00', '08:45', 'A'), block(2, 10, '08:45', '09:30', 'A')]
  const result = groupScheduleBlocks(source)
  assert.deepEqual([result.length, result[0].start_time, result[0].end_time, result[0].sourceBlocks.map(item => item.id_block)], [1, '08:00', '09:30', [1, 2]])
  assert.equal(source[0].end_time, '08:45')
})

test('groups a break of exactly five minutes, but not six', () => {
  const result = groupScheduleBlocks([block(1, 10, '08:00', '08:45'), block(2, 10, '08:50', '09:30'), block(3, 10, '09:36', '10:00')])
  assert.deepEqual(result.map(item => [item.start_time, item.end_time]), [['08:00', '09:30'], ['09:36', '10:00']])
})

test('groups overlapping periods of the same class and room', () => {
  const source = [block(1, 10, '08:00', '09:00', 'A'), block(2, 10, '08:30', '09:30', 'A')]
  const result = groupScheduleBlocks(source)
  assert.deepEqual([result.length, result[0].start_time, result[0].end_time, result[0].sourceBlocks.map(item => item.id_block)], [1, '08:00', '09:30', [1, 2]])
})

test('does not group different classes, rooms, days, or overlapping unrelated blocks', () => {
  const result = groupScheduleBlocks([
    block(1, 10, '08:00', '09:00', 'A'), block(2, 11, '08:00', '09:00', 'A'),
    block(3, 10, '09:00', '10:00', 'B'), block(4, 10, '09:00', '10:00', 'A'),
  ])
  assert.equal(result.length, 3)
  assert.deepEqual(result.find(item => item.id_block === 1)?.sourceBlocks.map(item => item.id_block), [1, 4])
  assert.equal(result.find(item => item.id_block === 1)?.end_time, '10:00')
})
