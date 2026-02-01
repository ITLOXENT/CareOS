type PaginationProps = {
  page: number;
  pageSize: number;
  totalCount: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (pageSize: number) => void;
};

const PAGE_SIZES = [10, 25, 50];

export function PaginationControls({
  page,
  pageSize,
  totalCount,
  onPageChange,
  onPageSizeChange
}: PaginationProps) {
  const totalPages = Math.max(Math.ceil(totalCount / pageSize), 1);
  const canPrev = page > 1;
  const canNext = page < totalPages;

  return (
    <div className="row" style={{ marginTop: "12px", alignItems: "center" }}>
      <button
        className="button secondary"
        type="button"
        onClick={() => onPageChange(page - 1)}
        disabled={!canPrev}
        aria-disabled={!canPrev}
      >
        Previous
      </button>
      <span className="status" aria-live="polite">
        Page {page} of {totalPages} · {totalCount} items
      </span>
      <button
        className="button secondary"
        type="button"
        onClick={() => onPageChange(page + 1)}
        disabled={!canNext}
        aria-disabled={!canNext}
      >
        Next
      </button>
      <label className="status" style={{ marginLeft: "auto" }}>
        Page size
        <select
          className="input"
          style={{ marginLeft: "8px" }}
          value={pageSize}
          onChange={(event) => onPageSizeChange(Number(event.target.value))}
        >
          {PAGE_SIZES.map((size) => (
            <option key={size} value={size}>
              {size}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}
