from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.database import get_db, engine
from app.ai.embeddings import generate_embedding
from app.models.opportunity import Opportunity
from app.schemas.opportunity import OpportunityResponse
from typing import List, Optional, Dict, Any

router = APIRouter()

def python_cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculates cosine similarity between two vectors in Python."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_a = sum(a * a for a in v1) ** 0.5
    norm_b = sum(b * b for b in v2) ** 0.5
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot_product / (norm_a * norm_b)

@router.get("")
async def semantic_search(
    q: str = Query(..., description="Natural language query"),
    category: Optional[str] = None,
    country: Optional[str] = None,
    women_only: bool = False,
    student_only: bool = False,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Semantic vector search endpoint.
    Example: q="fully funded fellowship in Europe for women founders"
    """
    # 1. Generate query vector embedding
    query_vector = await generate_embedding(q)
    
    # 2. Check DB dialect
    dialect_name = db.bind.dialect.name
    
    results = []
    
    if dialect_name == "postgresql":
        # Native pgvector cosine similarity search
        filters = ["is_active = true"]
        params = {"embedding": query_vector, "limit": limit}
        
        if category:
            filters.append("category = :category")
            params["category"] = category
        if country:
            filters.append(":country = ANY(country)")
            params["country"] = country
        if women_only:
            filters.append("women_friendly = true")
        if student_only:
            filters.append("student_eligible = true")
            
        where_clause = " AND ".join(filters)
        
        sql = f"""
            SELECT 
                id, name, organization, description, category, tags, country,
                remote, in_person, eligibility_text, women_friendly, indian_eligible,
                student_eligible, funding_amount, deadline, url, source, created_at,
                1 - (embedding <=> :embedding::vector) AS similarity
            FROM opportunities
            WHERE {where_clause}
            ORDER BY embedding <=> :embedding::vector
            LIMIT :limit
        """
        try:
            res = await db.execute(text(sql), params)
            rows = res.fetchall()
            for row in rows:
                mapping = dict(row._mapping)
                results.append(mapping)
        except Exception as e:
            # Fallback to local python search if vector execution fails or extension is missing
            dialect_name = "sqlite_fallback"
            
    if dialect_name != "postgresql":
        # Fallback processing for SQLite / local testing
        stmt = select(Opportunity).where(Opportunity.is_active == True)
        if category:
            stmt = stmt.where(Opportunity.category == category)
        if women_only:
            stmt = stmt.where(Opportunity.women_friendly == True)
        if student_only:
            stmt = stmt.where(Opportunity.student_eligible == True)
            
        res = await db.execute(stmt)
        all_opps = res.scalars().all()
        
        scored_opps = []
        for opp in all_opps:
            # Apply country filter if specified
            if country and opp.country:
                if not any(c.lower() == country.lower() for c in opp.country):
                    continue
            
            similarity = 0.0
            if opp.embedding:
                similarity = python_cosine_similarity(query_vector, opp.embedding)
            
            # Map object
            scored_opps.append({
                "id": opp.id,
                "name": opp.name,
                "organization": opp.organization,
                "description": opp.description,
                "category": opp.category,
                "tags": opp.tags,
                "country": opp.country,
                "remote": opp.remote,
                "in_person": opp.in_person,
                "eligibility_text": opp.eligibility_text,
                "women_friendly": opp.women_friendly,
                "indian_eligible": opp.indian_eligible,
                "student_eligible": opp.student_eligible,
                "funding_amount": opp.funding_amount,
                "deadline": opp.deadline.isoformat() if opp.deadline else None,
                "url": opp.url,
                "source": opp.source,
                "created_at": opp.created_at.isoformat() if opp.created_at else None,
                "similarity": similarity
            })
            
        # Sort by similarity score descending
        scored_opps.sort(key=lambda x: x["similarity"], reverse=True)
        results = scored_opps[:limit]
        
    return {
        "query": q,
        "results": results,
        "count": len(results)
    }

@router.get("/recommendations/{user_id}")
async def get_recommendations(
    user_id: str,
    limit: int = 5,
    db: AsyncSession = Depends(get_db)
):
    """
    AI Recommendation Engine (Bonus).
    Takes a user's saved opportunities, aggregates their vector embeddings
    to build an interest profile, and returns the top matching unsaved opportunities.
    """
    # 1. Fetch saved application opportunities
    from app.models.application import Application
    
    stmt = select(Application).where(Application.user_id == user_id)
    res = await db.execute(stmt)
    apps = res.scalars().all()
    
    if not apps:
        # If no saved opportunities, return latest active opportunities as default recommendations
        default_stmt = select(Opportunity).where(Opportunity.is_active == True).order_by(Opportunity.created_at.desc()).limit(limit)
        default_res = await db.execute(default_stmt)
        opps = default_res.scalars().all()
        return {
            "user_id": user_id,
            "basis": "latest",
            "recommendations": [
                {
                    "id": o.id, "name": o.name, "organization": o.organization,
                    "category": o.category, "description": o.description, "url": o.url
                } for o in opps
            ]
        }
        
    # 2. Collect saved opportunity embeddings
    saved_ids = []
    vectors = []
    
    for app in apps:
        saved_ids.append(app.opportunity_id)
        opp_stmt = select(Opportunity).where(Opportunity.id == app.opportunity_id)
        opp_res = await db.execute(opp_stmt)
        opp = opp_res.scalars().first()
        if opp and opp.embedding:
            # SafeVector processed value is a list of floats
            vectors.append(opp.embedding)
            
    if not vectors:
        # Fallback if no embeddings
        fallback_stmt = select(Opportunity).where(
            Opportunity.is_active == True,
            ~Opportunity.id.in_(saved_ids)
        ).limit(limit)
        fallback_res = await db.execute(fallback_stmt)
        opps = fallback_res.scalars().all()
        return {
            "user_id": user_id,
            "basis": "popular",
            "recommendations": [
                {
                    "id": o.id, "name": o.name, "organization": o.organization,
                    "category": o.category, "description": o.description, "url": o.url
                } for o in opps
            ]
        }
        
    # 3. Calculate average profile vector
    vector_len = len(vectors[0])
    avg_vector = [0.0] * vector_len
    for vec in vectors:
        for i in range(vector_len):
            avg_vector[i] += vec[i]
    avg_vector = [x / len(vectors) for x in avg_vector]
    
    # 4. Find similar unsaved active opportunities
    # Dialect check
    dialect_name = db.bind.dialect.name
    results = []
    
    if dialect_name == "postgresql":
        # Native pgvector similarity queryexcluding saved opportunity IDs
        exclude_clause = ""
        params = {"embedding": avg_vector, "limit": limit}
        if saved_ids:
            exclude_clause = " AND id NOT IN :saved_ids"
            params["saved_ids"] = tuple(saved_ids)
            
        sql = f"""
            SELECT 
                id, name, organization, description, category, tags, country,
                1 - (embedding <=> :embedding::vector) AS similarity
            FROM opportunities
            WHERE is_active = true {exclude_clause}
            ORDER BY embedding <=> :embedding::vector
            LIMIT :limit
        """
        try:
            res = await db.execute(text(sql), params)
            rows = res.fetchall()
            results = [dict(r._mapping) for r in rows]
        except Exception:
            dialect_name = "sqlite_fallback"
            
    if dialect_name != "postgresql":
        # Local fallback math
        stmt = select(Opportunity).where(
            Opportunity.is_active == True,
            ~Opportunity.id.in_(saved_ids)
        )
        res = await db.execute(stmt)
        all_opps = res.scalars().all()
        
        scored = []
        for opp in all_opps:
            sim = 0.0
            if opp.embedding:
                sim = python_cosine_similarity(avg_vector, opp.embedding)
            scored.append({
                "id": opp.id,
                "name": opp.name,
                "organization": opp.organization,
                "category": opp.category,
                "description": opp.description,
                "similarity": sim
            })
        scored.sort(key=lambda x: x["similarity"], reverse=True)
        results = scored[:limit]
        
    return {
        "user_id": user_id,
        "basis": "vector_profile_similarity",
        "recommendations": results
    }

