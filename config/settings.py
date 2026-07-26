from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys & Models
    openai_api_key: str = "test-key"
    anthropic_api_key: str = "test-key"
    default_reasoning_model: str = "gpt-4o-mini"
    default_critic_model: str = "claude-3-5-sonnet-20240620"

    # Database & Vector Store
    database_url: str = "postgresql://clauseiq:clauseiq_password@localhost:5432/clauseiq_db"
    pgvector_table_name: str = "playbook_precedents"

    # Paths
    base_dir: Path = Path(__file__).resolve().parent.parent
    data_dir: Path = base_dir / "data"
    models_dir: Path = data_dir / "models"
    lora_checkpoint_path: Path = models_dir / "cuad_lora_modernbert"
    vision_model_id: str = "microsoft/layoutlmv3-base"

    # App Config
    log_level: str = "INFO"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = AppSettings()
