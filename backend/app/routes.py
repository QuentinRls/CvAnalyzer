from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Request, Body
from fastapi.responses import StreamingResponse
from typing import Optional
import io
from datetime import datetime

from .schemas import DossierCompetences, CVTextRequest, ErrorResponse
from .extractor import extract_structured
from .utils import logger, CVExtractionError, LLMExtractionError
from .renderer.pdf_generator import generate_cv_pdf


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
        
        # Extract structured data
        try:
            extracted = extract_structured(cv_text=cv_text)
            
            logger.info("Successfully extracted CV data from text")
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
        
        # Extract structured data
        try:
            extracted = extract_structured(cv_text=cv_text)
            
            logger.info("Successfully extracted CV data")
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
    try:
        from .renderer.google_docs_generator import generate_google_docs_html
        
        # Generate HTML content
        html_content = generate_google_docs_html(dossier)
        
        # Prepare filename
        nom_complet = f"{dossier.entete.prenom}_{dossier.entete.nom}".strip("_")
        if not nom_complet:
            nom_complet = "Dossier_Competences"
        
        filename = f"{nom_complet}_CV.html"
        
        logger.info(f"Successfully generated Google Docs HTML: {filename}")
        
        # Return HTML as streaming response
        return StreamingResponse(
            io.BytesIO(html_content.encode('utf-8')),
            media_type="text/html",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error generating Google Docs content: {e}")
        raise HTTPException(status_code=500, detail=f"Google Docs generation failed: {str(e)}")


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