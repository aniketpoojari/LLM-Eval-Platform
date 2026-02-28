import { useState } from 'react'
import Header from '../components/layout/Header'
import { DIMENSIONS } from '../utils/constants'

export default function Settings() {
  const [judgeModel, setJudgeModel] = useState('llama-3.1-8b-instant')
  const [judgeProvider, setJudgeProvider] = useState('groq')
  const [defaultDims, setDefaultDims] = useState(DIMENSIONS.map(d => d.value))
  const [saved, setSaved] = useState(false)

  const handleSave = () => {
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div>
      <Header title="Settings" subtitle="Configure platform defaults and judge LLM" />

      <div className="max-w-2xl space-y-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Judge LLM Configuration</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Provider</label>
              <select className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={judgeProvider} onChange={e => setJudgeProvider(e.target.value)}>
                <option value="groq">Groq</option>
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Model</label>
              <input className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={judgeModel} onChange={e => setJudgeModel(e.target.value)} />
            </div>
            <p className="text-xs text-gray-400">The judge LLM evaluates target responses on each dimension. Configure via GROQ_API_KEY environment variable.</p>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Default Evaluation Dimensions</h3>
          <div className="space-y-2">
            {DIMENSIONS.map(d => (
              <label key={d.value} className="flex items-center gap-3 p-2 hover:bg-gray-50 rounded-lg cursor-pointer">
                <input
                  type="checkbox"
                  checked={defaultDims.includes(d.value)}
                  onChange={e => {
                    const dims = e.target.checked
                      ? [...defaultDims, d.value]
                      : defaultDims.filter(x => x !== d.value)
                    setDefaultDims(dims)
                  }}
                  className="w-4 h-4"
                />
                <div>
                  <p className="text-sm font-medium text-gray-900">{d.label}</p>
                </div>
              </label>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">About</h3>
          <div className="space-y-2 text-sm text-gray-600">
            <p><span className="font-medium">Platform:</span> LLM Eval Platform v1.0.0</p>
            <p><span className="font-medium">Backend:</span> FastAPI + Groq (LLM-as-Judge)</p>
            <p><span className="font-medium">Features:</span> Multi-dimension eval, 200+ adversarial attacks, A/B testing with statistical significance, observability</p>
          </div>
        </div>

        <button onClick={handleSave} className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors">
          {saved ? 'Saved!' : 'Save Settings'}
        </button>
      </div>
    </div>
  )
}
