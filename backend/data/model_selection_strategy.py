"""
Model Selection Strategy for Resume Generation

Based on November 2025 research on anti-hallucination and factual accuracy.
"""

# Primary model recommendations based on research
PRIMARY_MODELS = {
    "llama-3.3-70b-versatile": {
        "provider": "groq",
        "hallucination_rate": "~16%",  # Estimated based on Llama family performance
        "speed": "276 tokens/sec",
        "cost_per_1m": {"input": 0.59, "output": 0.79},
        "context_window": 131072,
        "max_output": 32768,
        "strengths": [
            "RLHF training for human alignment",
            "Strong instruction following",
            "Excellent speed/cost ratio",
            "Good performance on structured tasks",
            "86% MMLU accuracy",
            "88.4% HumanEval code generation"
        ],
        "anti_hallucination_features": [
            "RLHF training reduces fabrication",
            "Strong instruction following reduces off-topic generation",
            "Built-in refusal when uncertain (can be prompted)"
        ],
        "recommended_for": ["Stage 2: Generation & Validation"],
        "use_case": "Primary high-quality resume generation with strong factual grounding"
    },
    
    "llama-3.1-8b-instant": {
        "provider": "groq", 
        "hallucination_rate": "~18%",  # Estimated higher due to smaller size
        "speed": "840 tokens/sec",
        "cost_per_1m": {"input": 0.05, "output": 0.08},
        "context_window": 131072,
        "max_output": 131072,
        "strengths": [
            "Ultra-fast generation",
            "Very cost-effective",
            "Good for structured tasks",
            "Suitable for real-time applications"
        ],
        "anti_hallucination_features": [
            "Fast iteration allows multiple validation passes",
            "Lower cost enables conservative generation with verification"
        ],
        "recommended_for": ["Stage 1: Analysis & Matching"],
        "use_case": "Fast analysis, keyword extraction, content scoring"
    }
}

# Alternative models for comparison (not currently integrated)
ALTERNATIVE_MODELS = {
    "claude-3.7-sonnet": {
        "provider": "anthropic",
        "hallucination_rate": "~16%",  # Best measured anti-hallucination performance
        "strengths": [
            "Constitutional AI for safety",
            "Exceptional structured reasoning", 
            "Low hallucination rates",
            "Built-in uncertainty acknowledgment",
            "200K+ token context window"
        ],
        "anti_hallucination_features": [
            "Constitutional AI training", 
            "Built-in 'can't answer' circuit",
            "Explicit uncertainty quantification",
            "Formal tone reduces creative fabrication"
        ],
        "recommended_for": ["Premium anti-hallucination option"],
        "note": "Best for mission-critical applications requiring maximum factual accuracy"
    },
    
    "gemini-2.5-pro": {
        "provider": "google",
        "hallucination_rate": "~6.3%",  # Lowest measured in research
        "strengths": [
            "Lowest measured hallucination rate",
            "Strong factual accuracy",
            "Google's safety research integration"
        ],
        "limitations": [
            "Higher cost",
            "Less API availability",
            "Newer model with less proven track record"
        ]
    }
}

# Configuration for JobWise pipeline
JOBWISE_MODEL_CONFIG = {
    "stage1_model": "llama-3.1-8b-instant",  # Fast analysis
    "stage1_params": {
        "temperature": 0.2,  # Low for deterministic analysis
        "max_tokens": 2500,
        "top_p": 0.95,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    },
    
    "stage2_model": "llama-3.3-70b-versatile",  # High-quality generation
    "stage2_params": {
        "temperature": 0.3,  # Low-moderate for factual accuracy
        "max_tokens": 2500,
        "top_p": 0.95,
        "frequency_penalty": 0.1,  # Slight penalty for repetition
        "presence_penalty": 0.1   # Slight penalty for hallucination patterns
    },
    
    # Anti-hallucination strategies
    "anti_hallucination": {
        "use_system_constraints": True,
        "require_source_citations": True,
        "enable_uncertainty_detection": True,
        "validate_against_source": True,
        "use_fact_checking_prompts": True,
        "temperature_override_on_uncertainty": 0.1
    },
    
    # Prompt engineering for factual accuracy
    "prompt_strategies": [
        "Front-load critical constraints at prompt beginning",
        "Use explicit 'DO NOT FABRICATE' instructions",
        "Require source ID citation for every claim",
        "Implement chain-of-thought reasoning",
        "Use structured output with validation metadata",
        "Include self-validation checkpoints in prompts"
    ]
}

# Performance targets based on research
PERFORMANCE_TARGETS = {
    "hallucination_rate": {"target": "<15%", "acceptable": "<20%"},
    "factual_accuracy": {"target": ">85%", "minimum": ">80%"},
    "source_grounding": {"target": "100%", "minimum": "95%"},
    "response_time": {
        "stage1": {"target": "<3s", "maximum": "<5s"},
        "stage2": {"target": "<6s", "maximum": "<10s"}
    },
    "cost_per_generation": {"target": "<$0.02", "maximum": "<$0.05"}
}

# Model evaluation criteria for future upgrades
MODEL_EVALUATION_CRITERIA = {
    "anti_hallucination": {
        "weight": 0.35,
        "metrics": ["hallucination_rate", "uncertainty_detection", "source_grounding"]
    },
    "quality": {
        "weight": 0.25, 
        "metrics": ["coherence", "relevance", "professional_tone"]
    },
    "performance": {
        "weight": 0.20,
        "metrics": ["speed", "reliability", "consistency"]
    },
    "cost": {
        "weight": 0.20,
        "metrics": ["tokens_per_dollar", "total_cost_per_generation"]
    }
}

# Research-based best practices
RESEARCH_INSIGHTS = {
    "key_findings": [
        "Claude models have best built-in anti-hallucination features via Constitutional AI",
        "Gemini 2.5 Pro shows lowest hallucination rates (6.3%) in benchmarks", 
        "Groq's Llama models offer best speed/cost ratio with acceptable accuracy",
        "RLHF training significantly reduces fabrication compared to base models",
        "Lower temperature settings improve factual accuracy but reduce creativity",
        "Chain-of-thought prompting improves transparency and accuracy",
        "Explicit uncertainty acknowledgment reduces confident false statements"
    ],
    
    "anti_hallucination_techniques": [
        "Use structured output with validation metadata",
        "Implement semantic entropy detection for uncertainty",
        "Apply constitutional AI principles in prompting",
        "Use retrieval-augmented generation (RAG) for fact-checking",
        "Implement multiple model validation for critical claims",
        "Use temperature control based on task criticality"
    ],
    
    "model_specific_notes": {
        "llama_family": "RLHF training improves alignment, but still requires careful prompting",
        "claude_family": "Built-in safety circuits reduce hallucination but may be overly conservative", 
        "gpt_family": "Good general performance but requires explicit anti-hallucination prompting",
        "gemini_family": "Shows promise in benchmarks but limited real-world validation"
    }
}

# Implementation recommendations
IMPLEMENTATION_STRATEGY = {
    "immediate": [
        "Continue using Groq llama-3.3-70b-versatile for optimal speed/cost/quality balance",
        "Implement enhanced anti-hallucination prompts based on research",
        "Add structured output validation with source citation requirements",
        "Use lower temperature (0.2-0.3) for factual accuracy"
    ],
    
    "short_term": [
        "Add semantic entropy detection for hallucination flagging",
        "Implement multi-model validation for critical resume claims",
        "Add user feedback loop for hallucination detection training",
        "Create benchmarking suite for ongoing model evaluation"
    ],
    
    "long_term": [
        "Evaluate Claude integration for premium anti-hallucination tier",
        "Consider Gemini integration when API access improves", 
        "Develop custom fine-tuning for resume-specific anti-hallucination",
        "Implement full RAG pipeline for fact-checking against source documents"
    ]
}