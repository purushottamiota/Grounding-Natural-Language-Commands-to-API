from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "NL to Calendar API Service"
    PROJECT_DESCRIPTION: str = "Transforms natural language commands into structured JSON Calendar API payloads."
    API_V1_STR: str = "/api/v1"
    
    BASE_MODEL_NAME: str = "t5-small"
    ADAPTER_PATH: str = "./model_artifacts/lora-adapter"
    MAX_INPUT_LEN: int = 256
    MAX_NEW_TOKENS: int = 256
    PREFIX: str = "translate English to Calendar API: "
    NUM_BEAMS: int = 4
    EARLY_STOPPING: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
