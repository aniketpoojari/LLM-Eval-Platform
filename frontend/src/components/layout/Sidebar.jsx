import { Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  ClipboardCheck,
  Shield,
  GitCompare,
  Activity,
  Target,
  Settings,
} from 'lucide-react'

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/evaluations', label: 'Evaluations', icon: ClipboardCheck },
  { path: '/red-team', label: 'Red Team', icon: Shield },
  { path: '/ab-tests', label: 'A/B Tests', icon: GitCompare },
  { path: '/observability', label: 'Observability', icon: Activity },
  { path: '/targets', label: 'Targets', icon: Target },
  { path: '/settings', label: 'Settings', icon: Settings },
]

export default function Sidebar() {
  const location = useLocation()

  return (
    <aside className="w-64 bg-gray-900 text-white min-h-screen flex flex-col">
      <div className="p-6 border-b border-gray-700">
        <h1 className="text-xl font-bold">LLM Eval Platform</h1>
        <p className="text-gray-400 text-sm mt-1">Evaluate & Red-Team</p>
      </div>
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map(({ path, label, icon: Icon }) => {
          const isActive = location.pathname === path
          return (
            <Link
              key={path}
              to={path}
              className={`flex items-center gap-3 px-4 py-2.5 rounded-lg transition-colors ${
                isActive
                  ? 'bg-indigo-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`}
            >
              <Icon size={20} />
              <span className="text-sm font-medium">{label}</span>
            </Link>
          )
        })}
      </nav>
      <div className="p-4 border-t border-gray-700 text-gray-500 text-xs">
        v1.0.0
      </div>
    </aside>
  )
}
