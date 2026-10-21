import test from 'node:test'
import assert from 'node:assert/strict'
import { paginateProposals } from '../src/proposalPagination.ts'

test('recorre todas las páginas sin duplicar ni omitir propuestas', () => {
  const items = Array.from({ length: 25 }, (_, id) => ({ id }))
  const pages = [paginateProposals(items, 0, 10), paginateProposals(items, 10, 10), paginateProposals(items, 20, 10)]
  assert.deepEqual(pages.flatMap(page => page.items).map(item => item.id), items.map(item => item.id))
  assert.equal(pages[0].total, 25)
  assert.equal(pages[2].pageCount, 3)
})

test('una página vacía conserva un total explícito', () => {
  const page = paginateProposals([], 10, 10)
  assert.deepEqual(page.items, [])
  assert.equal(page.total, 0)
  assert.equal(page.pageCount, 0)
  assert.equal(page.pageNumber, 0)
})

test('el desplazamiento fuera de rango se ajusta a la última página', () => {
  const page = paginateProposals([1, 2, 3], 100, 2)
  assert.deepEqual(page.items, [3])
  assert.equal(page.offset, 2)
})
