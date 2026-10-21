export type ProposalPage<T> = {
  items: T[]
  total: number
  offset: number
  pageSize: number
  pageNumber: number
  pageCount: number
}

export function paginateProposals<T>(items: T[], offset: number, pageSize: number): ProposalPage<T> {
  const safePageSize = Math.max(1, Math.floor(pageSize))
  const total = items.length
  const pageCount = total === 0 ? 0 : Math.ceil(total / safePageSize)
  const safeOffset = total === 0 ? 0 : Math.min(Math.max(0, Math.floor(offset)), (pageCount - 1) * safePageSize)
  return { items: items.slice(safeOffset, safeOffset + safePageSize), total, offset: safeOffset, pageSize: safePageSize, pageNumber: pageCount === 0 ? 0 : Math.floor(safeOffset / safePageSize) + 1, pageCount }
}
