import hashlib
from typing import List
from openai import AsyncOpenAI
from loguru import logger
from app.config import settings

client = None
if settings.OPENAI_API_KEY:
    try:
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")

def generate_mock_embedding(text: str) -> List[float]:
    """Generates a deterministic 1536-dim normalized float vector based on text hashing."""
    # Seed values based on MD5 hashes of different parts of the string
    hash_obj = hashlib.sha256(text.encode("utf-8"))
    digest = hash_obj.digest()
    
    vector = []
    for i in range(1536):
        # Deterministic generation using byte segments
        byte_index = i % len(digest)
        val = (digest[byte_index] + (i * 17)) % 256
        # Map to -1 to +1 float range
        norm_val = (val / 127.5) - 1.0
        vector.append(norm_val)
        
    # Simple normalization to unit vector
    sq_sum = sum(x*x for x in vector)
    magnitude = sq_sum ** 0.5
    if magnitude > 0:
        vector = [x / magnitude for x in vector]
        
    return vector

async def generate_embedding(text: str) -> List[float]:
    """Generates 1536-dim vector embedding using OpenAI or fallback mock."""
    if not client:
        # Fallback to local mock embedding
        return generate_mock_embedding(text)
        
    try:
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=text[:8000]
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"OpenAI embedding generation failed: {e}. Falling back to mock generator.")
        return generate_mock_embedding(text)

def build_embedding_text(opportunity: dict) -> str:
    """Combine key fields into a single block of text for vector generation."""
    parts = [
        opportunity.get("name", ""),
        opportunity.get("organization", ""),
        opportunity.get("description", ""),
        opportunity.get("eligibility", ""),
        " ".join(opportunity.get("tags", []) or []),
        " ".join(opportunity.get("country", []) or []),
        opportunity.get("category", "")
    ]
    return " ".join(filter(None, parts))
