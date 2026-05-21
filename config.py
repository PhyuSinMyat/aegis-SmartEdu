import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')


def _env(name: str, default: str = '') -> str:
    return os.getenv(name, os.getenv(name.lower(), default))


class Config:
    BASE_DIR = BASE_DIR
    BACKEND_DIR = BASE_DIR / 'backend'
    PROMPTS_DIR = BACKEND_DIR / 'prompts'
    EXTRACTION_PROMPT_PATH = Path(
        os.getenv('EXTRACTION_PROMPT_PATH', str(PROMPTS_DIR / 'extraction_prompt.txt'))
    )

    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-change-me')

# Cross-origin cookie settings — required for the browser extension
    # to send session cookies from chrome-extension:// to the Flask server.
    # On Vercel (HTTPS) these MUST be True/None; on localhost they are relaxed.
    _is_production = os.getenv('FLASK_ENV', 'development') == 'production'
    SESSION_COOKIE_SECURE   = _is_production          # True on Vercel (HTTPS only)
    SESSION_COOKIE_SAMESITE = 'None' if _is_production else 'Lax'
    SESSION_COOKIE_HTTPONLY = True
    
    AWS_ACCESS_KEY_ID = _env('AWS_ACCESS_KEY_ID').strip()
    AWS_SECRET_ACCESS_KEY = _env('AWS_SECRET_ACCESS_KEY').strip()
    AWS_REGION = _env('AWS_REGION', 'ap-southeast-1').strip()
    AWS_BEDROCK_MODEL_ID = _env('AWS_BEDROCK_MODEL_ID').strip()

    BEDROCK_MAX_TOKENS = int(os.getenv('BEDROCK_MAX_TOKENS', '12000'))
    BEDROCK_RETRY_MAX_TOKENS = int(os.getenv('BEDROCK_RETRY_MAX_TOKENS', '18000'))
    BEDROCK_TEXT_TEMPERATURE = float(os.getenv('BEDROCK_TEXT_TEMPERATURE', '0'))
    BEDROCK_CONNECT_TIMEOUT = int(os.getenv('BEDROCK_CONNECT_TIMEOUT', '20'))
    BEDROCK_READ_TIMEOUT = int(os.getenv('BEDROCK_READ_TIMEOUT', '120'))
    BEDROCK_MAX_ATTEMPTS = int(os.getenv('BEDROCK_MAX_ATTEMPTS', '3'))
    BEDROCK_API_RETRIES = int(os.getenv('BEDROCK_API_RETRIES', '2'))

    USE_MOCK_LLM = os.getenv('USE_MOCK_LLM', '0').strip().lower() in {'1', 'true', 'yes'}
    DEBUG_LLM = os.getenv('DEBUG_LLM', '1').strip().lower() in {'1', 'true', 'yes'}

    @classmethod
    def bedrock_session_kwargs(cls) -> dict:
        """Build kwargs for boto3.Session. Validates credentials are present."""
        if not cls.AWS_ACCESS_KEY_ID or not cls.AWS_SECRET_ACCESS_KEY:
            raise ValueError(
                'AWS credentials not configured. Please set AWS_ACCESS_KEY_ID and '
                'AWS_SECRET_ACCESS_KEY in your .env file (use UPPERCASE keys).'
            )

        kwargs = {}
        if cls.AWS_ACCESS_KEY_ID:
            kwargs['aws_access_key_id'] = cls.AWS_ACCESS_KEY_ID
        if cls.AWS_SECRET_ACCESS_KEY:
            kwargs['aws_secret_access_key'] = cls.AWS_SECRET_ACCESS_KEY
        if cls.AWS_REGION:
            kwargs['region_name'] = cls.AWS_REGION
        return kwargs

    @classmethod
    def resolve_bedrock_model_id(cls, model_id: str | None = None) -> str:
        final_model_id = (model_id or cls.AWS_BEDROCK_MODEL_ID).strip()
        if not final_model_id:
            raise ValueError('AWS_BEDROCK_MODEL_ID is missing. Add it to .env or pass model_id.')
        return final_model_id
