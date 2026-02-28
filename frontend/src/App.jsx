import { BrowserRouter, Routes, Route } from 'react-router-dom'
import MainLayout from './components/layout/MainLayout'
import Dashboard from './pages/Dashboard'
import Evaluations from './pages/Evaluations'
import RedTeam from './pages/RedTeam'
import ABTests from './pages/ABTests'
import Observability from './pages/Observability'
import Targets from './pages/Targets'
import Settings from './pages/Settings'

export default function App() {
  return (
    <BrowserRouter>
      <MainLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/evaluations" element={<Evaluations />} />
          <Route path="/red-team" element={<RedTeam />} />
          <Route path="/ab-tests" element={<ABTests />} />
          <Route path="/observability" element={<Observability />} />
          <Route path="/targets" element={<Targets />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </MainLayout>
    </BrowserRouter>
  )
}
