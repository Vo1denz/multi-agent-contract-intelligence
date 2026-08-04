"""Application settings loaded from environment variables."""
from __future__ import annotations
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    # Mode
    clauseiq_mode: str = "lite"  # "full" or "lite"
    
    # API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    default_reasoning_model: str = "gpt-4o-mini"
    default_critic_model: str = "claude-3-5-sonnet-20240620"
    
    # Database
    database_url: str = ""
    pgvector_table_name: str = "playbook_precedents"
    embedding_dimension: int = 384
    
    # Paths - computed from BASE_DIR
    base_dir: str = str(Path(__file__).resolve().parent.parent)
    upload_dir: str = ""  # set in model_post_init
    models_dir: str = ""
    
    # Model config
    lora_checkpoint_path: str = ""
    vision_model_id: str = "microsoft/dit-base-finetuned-rvlcdip"
    embedding_model_id: str = "BAAI/bge-small-en-v1.5"
    classification_confidence_threshold: float = 0.60
    deviation_threshold: float = 0.30
    max_upload_size_mb: int = 50
    
    # App
    log_level: str = "INFO"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    
    # Langfuse
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    def model_post_init(self, __context):
        if not self.upload_dir:
            self.upload_dir = str(Path(self.base_dir) / "data" / "uploads")
        if not self.models_dir:
            self.models_dir = str(Path(self.base_dir) / "data" / "models")
        if not self.lora_checkpoint_path:
            self.lora_checkpoint_path = str(Path(self.models_dir) / "cuad_lora")
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)

settings = AppSettings()
