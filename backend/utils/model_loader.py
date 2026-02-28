from langchain_groq import ChatGroq

from backend.config.config_loader import get_config
from backend.logger.logging import get_logger

logger = get_logger(__name__)

_model_cache = {}


class ModelLoader:
    def __init__(self):
        self.config = get_config()

    def get_model(self, temperature=None, max_tokens=None):
        provider = self.config.get_env("model_provider", "groq")
        model_name = self.config.get_env(
            "model_name", self.config.get("judge.model", "llama-3.1-8b-instant")
        )
        temp = (
            temperature
            if temperature is not None
            else self.config.get("judge.temperature", 0.0)
        )
        tokens = (
            max_tokens
            if max_tokens is not None
            else self.config.get("judge.max_tokens", 1024)
        )

        cache_key = f"{provider}_{model_name}_{temp}_{tokens}"
        if cache_key in _model_cache:
            return _model_cache[cache_key]

        try:
            api_key = self.config.get_env("groq_api_key")
            if not api_key:
                raise ValueError("GROQ_API_KEY not set")

            model = ChatGroq(
                model=model_name,
                temperature=temp,
                max_tokens=tokens,
                api_key=api_key,
            )
            _model_cache[cache_key] = model
            logger.info(f"Loaded model: {model_name} (provider: {provider})")
            return model
        except Exception as e:
            logger.error(f"Error in get_model -> {str(e)}")
            raise

    def get_model_info(self):
        return {
            "provider": self.config.get_env("model_provider", "groq"),
            "model": self.config.get_env(
                "model_name", self.config.get("judge.model", "llama-3.1-8b-instant")
            ),
        }
