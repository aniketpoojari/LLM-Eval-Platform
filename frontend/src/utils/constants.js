export const DIMENSIONS = [
  { value: 'factuality', label: 'Factuality' },
  { value: 'relevance', label: 'Relevance' },
  { value: 'coherence', label: 'Coherence' },
  { value: 'safety', label: 'Safety' },
  { value: 'helpfulness', label: 'Helpfulness' },
]

export const ATTACK_CATEGORIES = [
  { value: 'prompt_injection', label: 'Prompt Injection', color: '#ef4444' },
  { value: 'jailbreak', label: 'Jailbreak', color: '#f97316' },
  { value: 'pii_extraction', label: 'PII Extraction', color: '#eab308' },
  { value: 'bias_probing', label: 'Bias Probing', color: '#22c55e' },
  { value: 'harmful_content', label: 'Harmful Content', color: '#3b82f6' },
  { value: 'hallucination', label: 'Hallucination', color: '#8b5cf6' },
]

export const CHART_COLORS = [
  '#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#3b82f6',
  '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#06b6d4',
]
