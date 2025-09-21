import os
import json
import asyncio
from typing import List, Optional
from openai import AsyncOpenAI
from pydantic import BaseModel, Field, ValidationError

from ..utils import logger, LLMExtractionError


def get_async_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable must be set")
    return AsyncOpenAI(api_key=api_key)


async def compare_mission_with_cvs_async(mission_text: str, cvs_summaries: List[dict]) -> dict:
    """Call OpenAI to compare multiple CV summaries against a mission description.

    Returns a JSON-serializable dict with ranked CVs and highlighted strengths.
    """
    logger.info("Calling OpenAI to compare mission with CVs")
    try:
        client = get_async_openai_client()

        # Build a compact payload describing each CV
        cvs_payload = []
        for c in cvs_summaries:
            cvs_payload.append({
                "filename": c.get("_filename") or c.get("filename") or "unknown",
                "profil": c.get("entete", {}).get("resume_profil", "") if isinstance(c.get("entete"), dict) else "",
                "experiences_cles_recentes": c.get("experiences_cles_recentes", [])
            })

        # System & user instructions: request a strict JSON schema with detailed fields.
        system = (
            "Tu es un expert RH. Pour chaque CV fourni, évalue la pertinence par rapport à la mission donnée. "
            "Tu dois renvoyer STRICTEMENT un JSON valide correspondant au schéma demandé (voir consignes)."
        )

        instructions = (
            "Renvoie UN OBJECT JSON unique avec la forme:\n"
            '{"results":[{"filename":"<string>","score":<number 0-100>,"strengths":["<string>"],'
            '"weaknesses":["<string>"],"summary":"<string>","matched_skills":["<string>"],"reasoning":"<string>"}]}'
            "\n- 'results' doit être une liste triée du plus pertinent au moins pertinent.\n"
            "- Pour chaque CV, fournis entre 1 et 5 points dans 'strengths' et 0-5 points dans 'weaknesses'.\n"
            "- 'summary' doit être une courte phrase résumant l'adéquation.\n"
            "- 'matched_skills' doit lister les compétences clés mises en correspondance entre le CV et la mission.\n"
            "Réponds uniquement par le JSON demandé, sans texte additionnel."
        )

        prompt = (
            f"Mission:\n{mission_text}\n\nCVs:\n{json.dumps(cvs_payload, ensure_ascii=False, indent=2)}\n\n{instructions}"
        )

        response = await client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ]
        )

        # Try parse response text as JSON
        # Log raw content for debugging if needed
        text = response.choices[0].message.content
        logger.debug(f"OpenAI compare raw response content: {text}")

        # Try parse response text as JSON
        try:
            parsed = json.loads(text)
        except Exception:
            # If model returned text plus JSON, try to extract JSON substring
            try:
                start = text.index('{')
                json_text = text[start:]
                parsed = json.loads(json_text)
            except Exception as e:
                logger.error(f"Failed to parse OpenAI compare response: {e}")
                logger.debug(f"Raw response: {text}")
                raise LLMExtractionError("Invalid JSON response from OpenAI for compare")

        # Pydantic models to validate and normalize the response
        class CompareResultItem(BaseModel):
            filename: str
            score: int = Field(..., ge=0, le=100)
            strengths: List[str] = Field(default_factory=list)
            weaknesses: List[str] = Field(default_factory=list)
            summary: Optional[str] = None
            matched_skills: List[str] = Field(default_factory=list)
            reasoning: Optional[str] = None

        class CompareResults(BaseModel):
            results: List[CompareResultItem]

        # Validate parsed JSON matches expected schema
        try:
            validated = CompareResults.parse_obj(parsed)
        except ValidationError as ve:
            logger.error(f"Validation error for compare response: {ve}")
            logger.debug(f"Parsed content: {json.dumps(parsed)[:1000]}")
            raise LLMExtractionError(f"Compare response did not match expected schema: {ve}")

        # Return normalized python dict
        return validated.dict()

    except Exception as e:
        logger.error(f"OpenAI compare failed: {e}")
        raise LLMExtractionError(f"Compare LLM failed: {e}")
