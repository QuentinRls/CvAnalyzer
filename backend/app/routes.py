from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Request, Body
from fastapi.responses import StreamingResponse
from typing import Optional, List
import io
from datetime import datetime

from .schemas import DossierCompetences, CVTextRequest, ErrorResponse
from .extractor import extract_structured
from .extractor.async_extract import extract_structured_async, extract_from_text_async
from .utils import logger, CVExtractionError, LLMExtractionError
from .renderer.pdf_generator import generate_cv_pdf
from .extractor.compare_async import compare_mission_with_cvs_async


# Create router
router = APIRouter(prefix="/api/v1", tags=["cv"])


@router.post("/extract-text", response_model=DossierCompetences, responses={
    400: {"model": ErrorResponse},
    422: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def extract_cv_from_text(cv_text_request: CVTextRequest) -> DossierCompetences:
    """
    Extract structured data from CV text
    
    Args:
        cv_text_request: Raw CV text - JSON payload
        
    Returns:
        Structured extracted data
    """
    try:
        cv_text = cv_text_request.cv_text
        
        # Validate text length
        if not cv_text or len(cv_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="CV text too short (minimum 50 characters required)"
            )
        
        # Extract structured data asynchronously
        try:
            extracted = await extract_from_text_async(cv_text)
            
            logger.info("Successfully extracted CV data from text asynchronously")
            return extracted
            
        except LLMExtractionError as e:
            logger.error(f"LLM extraction failed: {e}")
            raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected extraction error: {e}")
            raise HTTPException(status_code=500, detail="Internal extraction error")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in extract-text endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/extract", response_model=DossierCompetences, responses={
    400: {"model": ErrorResponse},
    422: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def extract_cv_data(
    file: Optional[UploadFile] = File(None),
    cv_text_request: Optional[CVTextRequest] = Body(None)
) -> DossierCompetences:
    """
    Extract structured data from CV
    
    Args:
        file: CV file (PDF/DOCX/TXT) - multipart/form-data
        cv_text_request: Raw CV text - JSON payload
        
    Returns:
        Structured extracted data
        
    Raises:
        400: Invalid input (no file/text or insufficient content)
        422: Validation error
        500: Internal extraction error
    """
    try:
        cv_text = None
        
        # Handle file upload
        if file is not None:
            logger.info(f"Processing uploaded file: {file.filename} ({file.content_type})")
            
            # Validate file type
            if file.content_type not in [
                "application/pdf",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "text/plain",
                "application/octet-stream"  # Allow generic binary for flexibility
            ]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file.content_type}"
                )
            
            # Read file content
            content = await file.read()
            if not content:
                raise HTTPException(status_code=400, detail="Empty file")
            
            # Extract text using file-like object
            import io
            file_obj = io.BytesIO(content)
            
            try:
                from .extractor.ingest import read_cv
                cv_text = read_cv(file_obj)
            except CVExtractionError as e:
                raise HTTPException(status_code=400, detail=str(e))
                
        # Handle JSON text input
        elif cv_text_request is not None:
            cv_text = cv_text_request.cv_text
            
        else:
            raise HTTPException(
                status_code=400, 
                detail="Either 'file' or 'cv_text' must be provided"
            )
        
        # Validate text length
        if not cv_text or len(cv_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="CV text too short (minimum 50 characters required)"
            )
        
        # Extract structured data asynchronously
        try:
            extracted = await extract_from_text_async(cv_text)
            
            logger.info("Successfully extracted CV data asynchronously")
            return extracted
            
        except LLMExtractionError as e:
            logger.error(f"LLM extraction failed: {e}")
            raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected extraction error: {e}")
            raise HTTPException(status_code=500, detail="Internal extraction error")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in extract endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/generate-pdf")
async def generate_pdf(dossier: DossierCompetences):
    """
    Generate a PDF from structured CV data
    
    Args:
        dossier: Structured CV data
        
    Returns:
        PDF file as StreamingResponse
    """
    try:
        # Generate PDF
        pdf_buffer = generate_cv_pdf(dossier)
        
        # Prepare filename
        nom_complet = f"{dossier.entete.prenom}_{dossier.entete.nom}".strip("_")
        if not nom_complet:
            nom_complet = "Dossier_Competences"
        
        filename = f"{nom_complet}_CV.pdf"
        
        logger.info(f"Successfully generated PDF: {filename}")
        
        # Return PDF as streaming response
        return StreamingResponse(
            io.BytesIO(pdf_buffer.getvalue()),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.post("/generate-google-docs")
async def generate_google_docs(dossier: DossierCompetences):
    """
    Generate Google Docs formatted content from structured CV data
    
    Args:
        dossier: Structured CV data
        
    Returns:
        HTML content formatted for Google Docs import
    """
    # Google Docs generation endpoint removed.
    raise HTTPException(status_code=404, detail="Google Docs generation endpoint has been removed")


@router.post("/generate-pptx")
async def generate_pptx(dossier: DossierCompetences):
    """
    Génère une présentation PowerPoint avec le template Devoteam
    """
    try:
        logger.info("Génération PowerPoint demandée")
        
        # Import dynamique pour éviter les erreurs de démarrage
        from .renderer.pptx_generator import generate_devoteam_pptx
        
        # Générer le PowerPoint
        pptx_buffer = generate_devoteam_pptx(dossier)
        
        # Nom de fichier avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nom_complet = f"{dossier.entete.prenom}_{dossier.entete.nom}".replace(" ", "_")
        filename = f"CV_{nom_complet}_{timestamp}.pptx"
        
        logger.info(f"PowerPoint généré: {filename}")
        
        # Return PPTX as streaming response
        return StreamingResponse(
            pptx_buffer,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error generating PowerPoint: {e}")
        raise HTTPException(status_code=500, detail=f"PowerPoint generation failed: {str(e)}")



@router.post("/compare")
async def compare_cvs_with_mission(
    cvs: Optional[List[UploadFile]] = File(None),
    mission: Optional[UploadFile] = File(None)
) -> dict:
    """Compare multiple CV files against a mission file and return ranked results.

    Expects multipart/form-data with fields:
    - cvs: multiple CV files
    - mission: single mission file
    """
    try:
        if not cvs or len(cvs) == 0:
            raise HTTPException(status_code=400, detail="At least one CV file must be provided")
        if mission is None:
            raise HTTPException(status_code=400, detail="A mission file must be provided")

        # Read mission text
        mission_content = await mission.read()
        if not mission_content:
            raise HTTPException(status_code=400, detail="Empty mission file")

        import io
        from .extractor.ingest import read_cv

        try:
            mission_text = read_cv(io.BytesIO(mission_content))
        except CVExtractionError as e:
            logger.error(f"Failed to extract mission text: {e}")
            raise HTTPException(status_code=400, detail=str(e))

        if not mission_text or len(mission_text.strip()) < 50:
            raise HTTPException(status_code=400, detail="Mission text too short (minimum 50 characters required)")

        # For each CV, read and extract text (we'll keep a light summary object for LLM compare)
        cvs_summaries = []
        for f in cvs:
            content = await f.read()
            if not content:
                continue
            try:
                text = read_cv(io.BytesIO(content))
            except CVExtractionError as e:
                logger.warning(f"Could not extract text from CV {f.filename}: {e}")
                # Append a minimal placeholder so the compare step still has an identifier
                cvs_summaries.append({"_filename": f.filename, "entete": {"resume_profil": ""}})
                continue

            # Keep lightweight structured extraction via async extractor
            try:
                extracted = await extract_from_text_async(text)
                # attach filename to help identify results
                d = extracted.dict()
                d["_filename"] = f.filename
                cvs_summaries.append(d)
            except LLMExtractionError:
                # If extraction fails for a CV, include minimal info so compare can still proceed
                cvs_summaries.append({"_filename": f.filename, "entete": {"resume_profil": text[:200]}})

        # Call compare LLM
        try:
            results = await compare_mission_with_cvs_async(mission_text, cvs_summaries)
        except LLMExtractionError as le:
            logger.error(f"LLM extraction/compare failed: {le}")
            raise HTTPException(status_code=500, detail=f"LLM compare failed: {str(le)}")

        return results

    except HTTPException:
        raise
    except Exception as e:
        # Return the exception message in dev to aid debugging
        logger.exception(f"Error in compare endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))