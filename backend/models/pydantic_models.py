import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# --- Enums ---


class EvalStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AttackCategory(str, Enum):
    PROMPT_INJECTION = "prompt_injection"
    JAILBREAK = "jailbreak"
    PII_EXTRACTION = "pii_extraction"
    BIAS_PROBING = "bias_probing"
    HARMFUL_CONTENT = "harmful_content"
    HALLUCINATION = "hallucination"


class EvalDimension(str, Enum):
    FACTUALITY = "factuality"
    RELEVANCE = "relevance"
    COHERENCE = "coherence"
    SAFETY = "safety"
    HELPFULNESS = "helpfulness"


# --- Target Models ---


class TargetCreate(BaseModel):
    name: str = Field(..., description="Display name for the target")
    description: Optional[str] = None
    api_url: str = Field(..., description="Target API endpoint URL")
    api_method: str = Field(default="POST", description="HTTP method")
    headers: Dict[str, str] = Field(default_factory=dict)
    request_template: str = Field(
        default='{"query": "{{input}}"}',
        description="Request body template. Use {{input}} as placeholder.",
    )
    response_path: str = Field(
        default="response",
        description="JSON path to extract response text from API response",
    )


class TargetResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    api_url: str
    api_method: str
    headers: Dict[str, str]
    request_template: str
    response_path: str
    created_at: str
    updated_at: str

    @classmethod
    def from_db(cls, row: dict):
        return cls(
            **{
                **row,
                "headers": json.loads(row.get("headers", "{}")),
            }
        )


class TargetTestRequest(BaseModel):
    input_text: str = Field(default="Hello, how are you?")


class TargetTestResponse(BaseModel):
    success: bool
    status_code: int
    response_text: Optional[str]
    latency_ms: float
    error: Optional[str] = None


# --- Evaluation Models ---


class QueryItem(BaseModel):
    input: str
    expected_output: Optional[str] = None


class EvaluationCreate(BaseModel):
    name: str
    target_id: str
    dimensions: List[EvalDimension] = Field(
        default_factory=lambda: [
            EvalDimension.FACTUALITY,
            EvalDimension.RELEVANCE,
            EvalDimension.COHERENCE,
            EvalDimension.SAFETY,
            EvalDimension.HELPFULNESS,
        ]
    )
    queries: List[QueryItem] = Field(
        ...,
        description="List of {input, expected_output} pairs",
    )


class EvaluationResponse(BaseModel):
    id: str
    name: str
    target_id: str
    dimensions: List[str]
    status: str
    total_queries: int
    completed_queries: int
    avg_score: Optional[float]
    created_at: str
    completed_at: Optional[str]

    @classmethod
    def from_db(cls, row: dict):
        return cls(
            **{
                **row,
                "dimensions": json.loads(row.get("dimensions", "[]")),
            }
        )


class EvalResultResponse(BaseModel):
    id: str
    evaluation_id: str
    input_text: str
    expected_output: Optional[str]
    actual_output: Optional[str]
    scores: Dict[str, float]
    avg_score: Optional[float]
    latency_ms: Optional[float]
    token_usage: Dict[str, Any]
    created_at: str

    @classmethod
    def from_db(cls, row: dict):
        return cls(
            **{
                **row,
                "scores": json.loads(row.get("scores", "{}")),
                "token_usage": json.loads(row.get("token_usage", "{}")),
            }
        )


# --- Red Team Models ---


class RedTeamRunCreate(BaseModel):
    name: str
    target_id: str
    categories: List[AttackCategory] = Field(
        default_factory=lambda: list(AttackCategory)
    )
    max_attacks: Optional[int] = Field(default=50)


class RedTeamRunResponse(BaseModel):
    id: str
    name: str
    target_id: str
    categories: List[str]
    status: str
    total_attacks: int
    completed_attacks: int
    safety_score: Optional[float]
    created_at: str
    completed_at: Optional[str]

    @classmethod
    def from_db(cls, row: dict):
        return cls(
            **{
                **row,
                "categories": json.loads(row.get("categories", "[]")),
            }
        )


class RedTeamResultResponse(BaseModel):
    id: str
    run_id: str
    category: str
    subcategory: Optional[str]
    attack_name: str
    attack_input: str
    target_output: Optional[str]
    is_safe: bool
    safety_score: Optional[float]
    explanation: Optional[str]
    latency_ms: Optional[float]
    created_at: str

    @classmethod
    def from_db(cls, row: dict):
        return cls(**{**row, "is_safe": bool(row.get("is_safe", 1))})


# --- A/B Testing Models ---


class ABTestCreate(BaseModel):
    name: str
    target_a_id: str
    target_b_id: str
    dimensions: List[EvalDimension] = Field(
        default_factory=lambda: [
            EvalDimension.FACTUALITY,
            EvalDimension.RELEVANCE,
            EvalDimension.COHERENCE,
        ]
    )
    queries: List[str] = Field(..., description="List of input queries")


class ABExperimentResponse(BaseModel):
    id: str
    name: str
    target_a_id: str
    target_b_id: str
    dimensions: List[str]
    status: str
    total_queries: int
    completed_queries: int
    winner: Optional[str]
    statistical_significance: Optional[float]
    created_at: str
    completed_at: Optional[str]

    @classmethod
    def from_db(cls, row: dict):
        return cls(
            **{
                **row,
                "dimensions": json.loads(row.get("dimensions", "[]")),
            }
        )


class ABResultResponse(BaseModel):
    id: str
    experiment_id: str
    input_text: str
    output_a: Optional[str]
    output_b: Optional[str]
    scores_a: Dict[str, float]
    scores_b: Dict[str, float]
    avg_score_a: Optional[float]
    avg_score_b: Optional[float]
    latency_a_ms: Optional[float]
    latency_b_ms: Optional[float]
    created_at: str

    @classmethod
    def from_db(cls, row: dict):
        return cls(
            **{
                **row,
                "scores_a": json.loads(row.get("scores_a", "{}")),
                "scores_b": json.loads(row.get("scores_b", "{}")),
            }
        )


class ABTestStats(BaseModel):
    experiment_id: str
    target_a_name: str
    target_b_name: str
    total_queries: int
    scores_a: Dict[str, float]
    scores_b: Dict[str, float]
    avg_a: float
    avg_b: float
    winner: Optional[str]
    p_value: Optional[float]
    confidence_interval: Optional[Dict[str, float]]
    is_significant: bool


# --- Observability Models ---


class MetricSummary(BaseModel):
    total_evaluations: int
    total_red_team_runs: int
    total_ab_tests: int
    total_queries_processed: int
    avg_latency_ms: Optional[float]
    total_tokens: int
    total_cost: float


class TokenUsageTimeSeries(BaseModel):
    date: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost: float


class CostSummary(BaseModel):
    total_cost: float
    total_tokens: int
    total_requests: int
    cost_by_source: Dict[str, float]
    daily_costs: List[Dict[str, Any]]


# --- Common ---


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
