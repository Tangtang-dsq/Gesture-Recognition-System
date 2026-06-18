export function StatusPill({ status }) {
  return <span className={`status status-${status}`}>{status}</span>;
}
