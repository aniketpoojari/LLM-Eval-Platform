ATTACK_CATEGORIES = {
    "prompt_injection": {
        "name": "Prompt Injection",
        "description": "Attempts to override system instructions or inject new instructions",
        "subcategories": [
            "direct_override",
            "role_play",
            "context_switching",
            "payload_splitting",
            "encoding_bypass",
            "instruction_injection",
            "delimiter_abuse",
            "few_shot_manipulation",
        ],
        "severity": "critical",
    },
    "jailbreak": {
        "name": "Jailbreak",
        "description": "Attempts to bypass safety filters and content policies",
        "subcategories": [
            "dan_variants",
            "hypothetical_scenarios",
            "academic_framing",
            "creative_writing",
            "translation_bypass",
            "role_assignment",
            "logical_manipulation",
            "emotional_appeal",
        ],
        "severity": "critical",
    },
    "pii_extraction": {
        "name": "PII Extraction",
        "description": "Attempts to extract personal or sensitive information",
        "subcategories": [
            "direct_request",
            "inference_probing",
            "system_prompt_leak",
            "data_exfiltration",
            "memory_extraction",
            "context_reconstruction",
        ],
        "severity": "high",
    },
    "bias_probing": {
        "name": "Bias Probing",
        "description": "Tests for biased, discriminatory, or unfair responses",
        "subcategories": [
            "gender_bias",
            "racial_bias",
            "age_bias",
            "socioeconomic_bias",
            "religious_bias",
            "disability_bias",
            "nationality_bias",
            "political_bias",
        ],
        "severity": "high",
    },
    "harmful_content": {
        "name": "Harmful Content",
        "description": "Attempts to generate harmful, dangerous, or illegal content",
        "subcategories": [
            "violence_incitement",
            "illegal_activity",
            "self_harm",
            "misinformation",
            "hate_speech",
            "harassment",
            "deception",
            "manipulation",
        ],
        "severity": "critical",
    },
    "hallucination": {
        "name": "Hallucination Induction",
        "description": "Attempts to induce factual hallucinations or false confidence",
        "subcategories": [
            "fake_facts",
            "numerical_hallucination",
            "authority_appeal",
            "temporal_confusion",
            "source_fabrication",
            "confidence_manipulation",
        ],
        "severity": "medium",
    },
}


def get_category_info(category):
    return ATTACK_CATEGORIES.get(category)


def get_all_categories():
    return [
        {
            "id": k,
            "name": v["name"],
            "description": v["description"],
            "subcategories": v["subcategories"],
            "severity": v["severity"],
            "attack_count": 0,
        }
        for k, v in ATTACK_CATEGORIES.items()
    ]
