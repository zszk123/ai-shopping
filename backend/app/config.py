import os
import secrets

from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "AI Shopping Compare")
    VERSION: str = "1.0.0"
    ENV: str = os.getenv("ENV", "development").lower()
    IS_PRODUCTION: bool = ENV == "production"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "ai_shopping")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        (
            f"mysql+aiomysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
            f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
        ),
    )

    MILVUS_HOST: str = os.getenv("MILVUS_HOST", "127.0.0.1")
    MILVUS_PORT: int = int(os.getenv("MILVUS_PORT", "19530"))
    MILVUS_COLLECTION: str = os.getenv("MILVUS_COLLECTION", "goods_vectors")

    REDIS_HOST: str = os.getenv("REDIS_HOST", "127.0.0.1")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))

    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = int(os.getenv("JWT_EXPIRE_HOURS", "24"))
    INTERNAL_API_TOKEN: str = os.getenv("INTERNAL_API_TOKEN", "")

    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")
    VISION_MODEL: str = os.getenv("VISION_MODEL", "qwen-vl-plus")
    VISION_FALLBACK_MODELS: list[str] = [
        model.strip()
        for model in os.getenv("VISION_FALLBACK_MODELS", "qwen3-vl-plus,qwen-vl-plus").split(",")
        if model.strip()
    ]
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-v3")
    VISION_EMBEDDING_MODEL: str = os.getenv("VISION_EMBEDDING_MODEL", "tongyi-embedding-vision-flash")
    RERANK_MODEL: str = os.getenv("RERANK_MODEL", "qwen3-rerank")
    MATH_MODEL: str = os.getenv("MATH_MODEL", "qwen-math-turbo")

    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-vl2")

    SPIDER_AUTO_START: bool = os.getenv("SPIDER_AUTO_START", "false").lower() == "true"

    OSS_ACCESS_KEY: str = os.getenv("OSS_ACCESS_KEY", "")
    OSS_SECRET_KEY: str = os.getenv("OSS_SECRET_KEY", "")
    OSS_ENDPOINT: str = os.getenv("OSS_ENDPOINT", "")
    OSS_BUCKET: str = os.getenv("OSS_BUCKET", "")

    VECTOR_CACHE_TTL: int = int(os.getenv("VECTOR_CACHE_TTL", "300"))
    GOODS_INFO_CACHE_TTL: int = int(os.getenv("GOODS_INFO_CACHE_TTL", "600"))
    COMPARE_RESULT_CACHE_TTL: int = int(os.getenv("COMPARE_RESULT_CACHE_TTL", "600"))
    AI_ANALYSIS_CACHE_TTL: int = int(os.getenv("AI_ANALYSIS_CACHE_TTL", "1800"))
    ENABLE_AI_PRICE_ANALYSIS: bool = os.getenv("ENABLE_AI_PRICE_ANALYSIS", "false").lower() == "true"
    AI_PRICE_ANALYSIS_TIMEOUT_SECONDS: float = float(os.getenv("AI_PRICE_ANALYSIS_TIMEOUT_SECONDS", "3"))
    RERANK_TIMEOUT_SECONDS: float = float(os.getenv("RERANK_TIMEOUT_SECONDS", "5"))
    JWT_CACHE_TTL: int = int(os.getenv("JWT_CACHE_TTL", "86400"))
    LOGIN_RATE_LIMIT_COUNT: int = int(os.getenv("LOGIN_RATE_LIMIT_COUNT", "10"))
    LOGIN_RATE_LIMIT_SECONDS: int = int(os.getenv("LOGIN_RATE_LIMIT_SECONDS", "60"))

    CORS_ORIGINS_RAW: str = os.getenv("CORS_ORIGINS", "")
    CORS_ORIGINS: list[str] = []

    def validate(self) -> None:
        if not self.JWT_SECRET:
            self.JWT_SECRET = "dev-only-ai-shopping-jwt-secret-key"
        if self.IS_PRODUCTION and (
            not self.JWT_SECRET or self.JWT_SECRET.startswith("dev-only") or len(self.JWT_SECRET) < 32
        ):
            raise RuntimeError("JWT_SECRET must be a strong secret in production")

        default_origins = "" if self.IS_PRODUCTION else "*"
        origins = self.CORS_ORIGINS_RAW or default_origins
        self.CORS_ORIGINS = [origin.strip() for origin in origins.split(",") if origin.strip()]

        if self.IS_PRODUCTION and (not self.CORS_ORIGINS or "*" in self.CORS_ORIGINS):
            raise RuntimeError("CORS_ORIGINS must be explicit in production")
        if self.IS_PRODUCTION and not self.INTERNAL_API_TOKEN:
            raise RuntimeError("INTERNAL_API_TOKEN must be configured in production")
        if self.INTERNAL_API_TOKEN and len(self.INTERNAL_API_TOKEN) < 24:
            raise RuntimeError("INTERNAL_API_TOKEN must be at least 24 characters")

    @staticmethod
    def generate_secret() -> str:
        return secrets.token_urlsafe(48)


settings = Settings()
settings.validate()
