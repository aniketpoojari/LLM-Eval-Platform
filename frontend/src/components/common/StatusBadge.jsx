export default function StatusBadge({ status }) {
  const styles = {
    pending: 'bg-gray-100 text-gray-700',
    running: 'bg-blue-100 text-blue-700',
    completed: 'bg-green-100 text-green-700',
    failed: 'bg-red-100 text-red-700',
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${styles[status] || styles.pending}`}>
      {status === 'running' && (
        <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mr-1.5 animate-pulse" />
      )}
      {status}
    </span>
  )
}
