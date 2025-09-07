from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Request, Body
from typing import Optional

from .schemas import DossierCompetences, CVTextRequest, ErrorResponse
from .extractor import extract_structured
from .utils import logger, CVExtractionError, LLMExtractionError


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
