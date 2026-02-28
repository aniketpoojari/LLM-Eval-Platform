-- Targets: LLM applications to evaluate
CREATE TABLE IF NOT EXISTS targets (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    api_url TEXT NOT NULL,
    api_method TEXT NOT NULL DEFAULT 'POST',
    headers TEXT DEFAULT '{}',
    request_template TEXT NOT NULL DEFAULT '{"query": "{{input}}"}',
    response_path TEXT DEFAULT 'response',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Evaluations: batch evaluation runs
CREATE TABLE IF NOT EXISTS evaluations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    target_id TEXT NOT NULL,
    dimensions TEXT NOT NULL DEFAULT '["factuality","relevance","coherence","safety","helpfulness"]',
    status TEXT NOT NULL DEFAULT 'pending',
    total_queries INTEGER DEFAULT 0,
    completed_queries INTEGER DEFAULT 0,
    avg_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (target_id) REFERENCES targets(id)
);

-- Evaluation results: individual query results
CREATE TABLE IF NOT EXISTS evaluation_results (
    id TEXT PRIMARY KEY,
    evaluation_id TEXT NOT NULL,
    input_text TEXT NOT NULL,
    expected_output TEXT,
    actual_output TEXT,
    scores TEXT NOT NULL DEFAULT '{}',
    avg_score REAL,
    latency_ms REAL,
    token_usage TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (evaluation_id) REFERENCES evaluations(id)
);

-- Red team runs
CREATE TABLE IF NOT EXISTS red_team_runs (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    target_id TEXT NOT NULL,
    categories TEXT NOT NULL DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'pending',
    total_attacks INTEGER DEFAULT 0,
    completed_attacks INTEGER DEFAULT 0,
    safety_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (target_id) REFERENCES targets(id)
);

-- Red team results: individual attack results
CREATE TABLE IF NOT EXISTS red_team_results (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT,
    attack_name TEXT NOT NULL,
    attack_input TEXT NOT NULL,
    target_output TEXT,
    is_safe INTEGER NOT NULL DEFAULT 1,
    safety_score REAL,
    explanation TEXT,
    latency_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES red_team_runs(id)
);

-- A/B test experiments
CREATE TABLE IF NOT EXISTS ab_experiments (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    target_a_id TEXT NOT NULL,
    target_b_id TEXT NOT NULL,
    dimensions TEXT NOT NULL DEFAULT '["factuality","relevance","coherence"]',
    status TEXT NOT NULL DEFAULT 'pending',
    total_queries INTEGER DEFAULT 0,
    completed_queries INTEGER DEFAULT 0,
    winner TEXT,
    statistical_significance REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (target_a_id) REFERENCES targets(id),
    FOREIGN KEY (target_b_id) REFERENCES targets(id)
);

-- A/B test results: paired comparison results
CREATE TABLE IF NOT EXISTS ab_results (
    id TEXT PRIMARY KEY,
    experiment_id TEXT NOT NULL,
    input_text TEXT NOT NULL,
    output_a TEXT,
    output_b TEXT,
    scores_a TEXT NOT NULL DEFAULT '{}',
    scores_b TEXT NOT NULL DEFAULT '{}',
    avg_score_a REAL,
    avg_score_b REAL,
    latency_a_ms REAL,
    latency_b_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (experiment_id) REFERENCES ab_experiments(id)
);

-- Observability metrics
CREATE TABLE IF NOT EXISTS metrics (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    source_id TEXT,
    metric_type TEXT NOT NULL,
    value REAL NOT NULL,
    metadata TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cost tracking
CREATE TABLE IF NOT EXISTS cost_tracking (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    source_id TEXT,
    provider TEXT NOT NULL DEFAULT 'groq',
    model TEXT NOT NULL,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    estimated_cost REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_evaluations_target ON evaluations(target_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_status ON evaluations(status);
CREATE INDEX IF NOT EXISTS idx_eval_results_eval ON evaluation_results(evaluation_id);
CREATE INDEX IF NOT EXISTS idx_red_team_runs_target ON red_team_runs(target_id);
CREATE INDEX IF NOT EXISTS idx_red_team_results_run ON red_team_results(run_id);
CREATE INDEX IF NOT EXISTS idx_red_team_results_category ON red_team_results(category);
CREATE INDEX IF NOT EXISTS idx_ab_experiments_status ON ab_experiments(status);
CREATE INDEX IF NOT EXISTS idx_ab_results_experiment ON ab_results(experiment_id);
CREATE INDEX IF NOT EXISTS idx_metrics_source ON metrics(source, source_id);
CREATE INDEX IF NOT EXISTS idx_metrics_type ON metrics(metric_type);
CREATE INDEX IF NOT EXISTS idx_metrics_created ON metrics(created_at);
CREATE INDEX IF NOT EXISTS idx_cost_source ON cost_tracking(source, source_id);
CREATE INDEX IF NOT EXISTS idx_cost_created ON cost_tracking(created_at);
