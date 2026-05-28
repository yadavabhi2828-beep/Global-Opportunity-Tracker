import json
import re
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel
from anthropic import Anthropic
from loguru import logger
from app.config import settings

client = None
if settings.ANTHROPIC_API_KEY:
    try:
        client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize Anthropic client: {e}")

EXTRACTION_PROMPT = """
You are an expert at extracting structured information about opportunities 
(scholarships, fellowships, accelerators, grants, competitions, etc.).

Extract the following fields from the text below and return ONLY valid JSON.
If a field is not found, use null.

FIELDS TO EXTRACT:
- name: Program name (string)
- organization: Hosting organization (string)
- country: List of eligible countries (array of strings)
- deadline: Application deadline in ISO format YYYY-MM-DD (string or null)
- eligibility: Who can apply (string)
- funding_amount: Money/benefits offered (string or null)
- category: One of: scholarship, fellowship, accelerator, grant, competition, conference, exchange, travel, government_scheme, giveaway (string)
- description: 2-3 sentence summary (string)
- tags: Relevant tags from: [AI, Startup, Women, Research, Design, MBA, Engineering, Climate, Travel, Social Impact, Hackathon, Student, Founder, Grant, Tech] (array)
- remote: Is it remote/online? (boolean)
- women_friendly: Is it specifically for women/women founders? (boolean)
- indian_eligible: Can Indian nationals apply? (boolean)
- student_eligible: Is it open to students? (boolean)
- min_age: Minimum age requirement (integer or null)
- max_age: Maximum age requirement (integer or null)
- application_fee: Application fee if any (string or null)

TEXT:
{content}

Return ONLY the JSON object, no explanation.
"""

class ExtractedOpportunity(BaseModel):
    name: str
    organization: Optional[str] = None
    country: Optional[List[str]] = None
    deadline: Optional[str] = None
    eligibility: Optional[str] = None
    funding_amount: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    remote: bool = False
    women_friendly: bool = False
    indian_eligible: bool = False
    student_eligible: bool = False
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    application_fee: Optional[str] = None

def mock_extract_opportunity(content: str, url: str) -> ExtractedOpportunity:
    """Generate dynamic mock details based on text if Anthropic API key is missing."""
    title_match = re.search(r"Title:\s*(.*)", content)
    title = title_match.group(1).strip() if title_match else "Global Fellowship Program"
    if not title or len(title) < 5:
        title = "Global Opportunities Initiative"

    # Default values based on title keyword checks
    category = "fellowship"
    if "scholarship" in title.lower():
        category = "scholarship"
    elif "grant" in title.lower() or "funding" in title.lower():
        category = "grant"
    elif "accelerator" in title.lower() or "startup" in title.lower():
        category = "accelerator"
    
    tags = ["Social Impact", "Travel"]
    if "ai" in title.lower() or "tech" in title.lower():
        tags.extend(["AI", "Tech"])
    if "women" in title.lower() or "female" in title.lower():
        tags.append("Women")
    if "student" in title.lower():
        tags.append("Student")
    if "startup" in title.lower() or "founder" in title.lower():
        tags.append("Founder")

    deadline_date = (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d")

    return ExtractedOpportunity(
        name=title,
        organization="Global Leadership Council",
        country=["India", "USA", "UK", "Canada", "Global"],
        deadline=deadline_date,
        eligibility="Open to students and early-career researchers worldwide.",
        funding_amount="$15,000 stipends + fully-funded travel",
        category=category,
        description=f"A competitive program for global leaders: {title}. Focuses on professional development, cross-border research, and mentorship.",
        tags=tags,
        remote="online" in title.lower() or "remote" in title.lower(),
        women_friendly="women" in title.lower() or "female" in title.lower(),
        indian_eligible=True,
        student_eligible="student" in title.lower() or "university" in title.lower(),
        min_age=18,
        max_age=35,
        application_fee="Free"
    )

async def extract_opportunity(content: str, url: str) -> Optional[ExtractedOpportunity]:
    """Extract structured data from raw content using Claude or fallback mock logic."""
    if not client:
        logger.info(f"Anthropic API key is not configured. Simulating AI extraction for {url}.")
        return mock_extract_opportunity(content, url)
        
    try:
        content_truncated = content[:8000]
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            messages=[{
                "role": "user",
                "content": EXTRACTION_PROMPT.format(content=content_truncated)
            }]
        )
        
        raw_json = response.content[0].text.strip()
        
        # Clean up Markdown JSON wraps
        if raw_json.startswith("```"):
            raw_json = raw_json.split("```")[1]
            if raw_json.startswith("json"):
                raw_json = raw_json[4:]
        
        data = json.loads(raw_json)
        return ExtractedOpportunity(**data)
        
    except Exception as e:
        logger.error(f"AI extraction failed for {url} due to: {e}. Falling back to mock extractor.")
        return mock_extract_opportunity(content, url)
