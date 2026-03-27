"""
C1 — SDK Client Initialization
Singleton clients for Gemini, Anthropic, and Supabase.
Each client is initialized once and reused across the application.
"""

from google import genai
import anthropic
from supabase import create_client, Client as SupabaseClient

from src.config import (
    GEMINI_API_KEY,
    ANTHROPIC_API_KEY,
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY,
)

_gemini_client: genai.Client | None = None
_anthropic_client: anthropic.Anthropic | None = None
_supabase_client: SupabaseClient | None = None


def get_gemini_client() -> genai.Client:
    """Return the singleton Gemini client."""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    return _gemini_client


def get_anthropic_client() -> anthropic.Anthropic:
    """Return the singleton Anthropic client."""
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _anthropic_client


def get_supabase_client() -> SupabaseClient:
    """Return the singleton Supabase client using the service role key."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    return _supabase_client
