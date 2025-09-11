import os
import json
import asyncio
from typing import Optional, Union, BinaryIO
from pathlib import Path
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from ..schemas import DossierCompetences
from ..utils import logger, LLMExtractionError
from .ingest import read_cv
from .llm_extract import SYSTEM_PROMPT, EXTRACTION_SCHEMA, get_openai_client


async def call_openai_extraction_async(cv_text: str) -> dict:
    """Call OpenAI API asynchronously to extract structured data from CV text."""
    logger.info("Calling OpenAI API asynchronously for CV extraction")
    
    try:
        # Créer un client asynchrone
        client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"""Voici le CV à analyser pour créer un dossier de compétences professionnel :

{cv_text}

CONSIGNES SPÉCIFIQUES :
1. Pour chaque expérience professionnelle, extrait le maximum de détails disponibles
2. Reformule le contexte pour qu'il soit riche et informatif (projet, enjeux, secteur)
3. Détaille les responsabilités avec des verbes d'action forts et des spécificités techniques
4. Liste tous les livrables concrets mentionnés ou implicites
5. Recense exhaustivement l'environnement technique pour chaque expérience
6. Priorise la qualité et la pertinence des informations extraites
7. IMPORTANT : Extrais exactement 5 expériences professionnelles clés récentes, même si certaines sont plus courtes ou moins détaillées que d'autres
8. ENVIRONNEMENT TECHNIQUE : Structure l'environnement technique de chaque expérience selon les 9 catégories (language_framework, ci_cd, state_management, tests, outils, base_de_donnees_big_data, data_analytics_visualisation, collaboration, ux_ui)"""}
            ],
            functions=[{
                "name": "extract_cv_data",
                "description": "Extraire les données structurées du CV",
                "parameters": EXTRACTION_SCHEMA
            }],
            function_call={"name": "extract_cv_data"},
        )
        
        function_call = response.choices[0].message.function_call
        if not function_call or function_call.name != "extract_cv_data":
            raise LLMExtractionError("No function call returned by OpenAI")
            
        extracted_data = json.loads(function_call.arguments)
        logger.info("Successfully extracted structured data from CV asynchronously")
        return extracted_data
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error from OpenAI response: {e}")
        raise LLMExtractionError(f"Invalid JSON response from OpenAI: {e}")
        
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        raise LLMExtractionError(f"OpenAI extraction failed: {e}")


async def extract_structured_async(cv_text: str = None, cv_file: Union[str, Path, BinaryIO] = None) -> DossierCompetences:
    """
    Extract structured data from CV text or file asynchronously.
    
    Args:
        cv_text: Raw text content of CV
        cv_file: CV file (path or file-like object)
        
    Returns:
        DossierCompetences: Structured CV data
        
    Raises:
        LLMExtractionError: If extraction fails
    """
    try:
        # Get CV text
        if cv_text:
            text_content = cv_text
        elif cv_file:
            # Run file reading in executor pour éviter de bloquer
            loop = asyncio.get_event_loop()
            text_content = await loop.run_in_executor(None, read_cv, cv_file)
        else:
            raise ValueError("Either cv_text or cv_file must be provided")
            
        if not text_content or len(text_content.strip()) < 50:
            raise LLMExtractionError("CV text too short or empty")
            
        logger.info(f"Extracting structured data from CV text ({len(text_content)} chars) asynchronously")
        
        # Call OpenAI for extraction asynchronously
        extracted_dict = await call_openai_extraction_async(text_content)
        
        # Validate and create Pydantic model
        try:
            extracted = DossierCompetences(**extracted_dict)
            logger.info("Successfully validated extracted data with Pydantic")
            return extracted
            
        except Exception as e:
            logger.error(f"Pydantic validation failed: {e}")
            logger.debug(f"Raw extracted data: {json.dumps(extracted_dict, indent=2)}")
            raise LLMExtractionError(f"Data validation failed: {e}")
            
    except LLMExtractionError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during extraction: {e}")
        raise LLMExtractionError(f"Extraction failed: {e}")


async def extract_from_text_async(cv_text: str) -> DossierCompetences:
    """Extract structured data from CV text asynchronously."""
    return await extract_structured_async(cv_text=cv_text)


async def extract_from_file_async(file_path: Union[str, Path]) -> DossierCompetences:
    """Extract structured data from CV file asynchronously."""
    return await extract_structured_async(cv_file=file_path)
