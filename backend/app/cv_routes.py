from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Request, Body, Depends
from fastapi.responses import StreamingResponse
from typing import Optional, List
import io
import time
import json
from datetime import datetime

from .schemas import DossierCompetences, CVTextRequest, ErrorResponse, User
from .extractor import extract_structured
from .extractor.async_extract import extract_structured_async, extract_from_text_async
from .utils import logger, CVExtractionError, LLMExtractionError
from .renderer.pdf_generator import generate_cv_pdf
from .extractor.compare_async import compare_mission_with_cvs_async
from .models import CVAnalysis
from .database import get_db, AsyncSessionLocal
from .routes.auth import get_current_user_dependency
from sqlalchemy import select


# Create router
router = APIRouter(prefix="/api/v1", tags=["cv"])


@router.post("/extract-text", response_model=DossierCompetences, responses={
    400: {"model": ErrorResponse},
    422: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def extract_cv_from_text(
    cv_text_request: CVTextRequest,
    current_user: User = Depends(get_current_user_dependency)
) -> DossierCompetences:
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
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_dependency)
) -> DossierCompetences:
    """
    Extract structured data from CV file
    
    Args:
        file: CV file (PDF/DOCX/TXT) - multipart/form-data
        current_user: Authenticated user
        
    Returns:
        Structured extracted data
        
    Raises:
        400: Invalid input (no file or unsupported format)
        422: Validation error
        500: Internal extraction error
    """
    start_time = time.time()
    cv_analysis_id = None
    
    try:
        logger.info(f"User {current_user.email} processing uploaded file: {file.filename} ({file.content_type})")
        
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
        
        # Create CV analysis record
        async with AsyncSessionLocal() as session:
            cv_analysis = CVAnalysis(
                user_id=current_user.id,
                original_filename=file.filename or "unknown.txt",
                file_type=file.content_type,
                file_size=len(content),
                extraction_status="pending"
            )
            session.add(cv_analysis)
            await session.commit()
            await session.refresh(cv_analysis)
            cv_analysis_id = cv_analysis.id
            logger.info(f"Created CV analysis record: {cv_analysis_id}")
        
        # Extract text using file-like object
        import io
        file_obj = io.BytesIO(content)
        
        try:
            from .extractor.ingest import read_cv
            cv_text = read_cv(file_obj)
        except CVExtractionError as e:
            # Update analysis status to failed
            if cv_analysis_id:
                async with AsyncSessionLocal() as session:
                    result = await session.execute(select(CVAnalysis).filter(CVAnalysis.id == cv_analysis_id))
                    analysis = result.scalar_one_or_none()
                    if analysis:
                        analysis.extraction_status = "failed"
                        analysis.extraction_error = str(e)
                        await session.commit()
            raise HTTPException(status_code=400, detail=str(e))
        
        # Validate text length
        if not cv_text or len(cv_text.strip()) < 50:
            # Update analysis status to failed
            if cv_analysis_id:
                async with AsyncSessionLocal() as session:
                    result = await session.execute(select(CVAnalysis).filter(CVAnalysis.id == cv_analysis_id))
                    analysis = result.scalar_one_or_none()
                    if analysis:
                        analysis.extraction_status = "failed"
                        analysis.extraction_error = "CV text too short"
                        await session.commit()
            raise HTTPException(
                status_code=400,
                detail="CV text too short (minimum 50 characters required)"
            )
        
        # Extract structured data asynchronously
        try:
            extracted = await extract_from_text_async(cv_text)
            
            # Calculate processing time
            processing_time = int((time.time() - start_time) * 1000)
            
            # Update analysis record with success
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(CVAnalysis).filter(CVAnalysis.id == cv_analysis_id))
                analysis = result.scalar_one_or_none()
                if analysis:
                    analysis.extraction_status = "completed"
                    analysis.raw_text = cv_text
                    analysis.structured_data = extracted.model_dump()  # Convert Pydantic model to dict
                    analysis.processing_time = processing_time
                    await session.commit()
            
            logger.info(f"Successfully extracted and saved CV data for user {current_user.email} in {processing_time}ms")
            return extracted
            
        except LLMExtractionError as e:
            # Update analysis status to failed
            if cv_analysis_id:
                async with AsyncSessionLocal() as session:
                    result = await session.execute(select(CVAnalysis).filter(CVAnalysis.id == cv_analysis_id))
                    analysis = result.scalar_one_or_none()
                    if analysis:
                        analysis.extraction_status = "failed"
                        analysis.extraction_error = str(e)
                        analysis.processing_time = int((time.time() - start_time) * 1000)
                        await session.commit()
            logger.error(f"LLM extraction failed: {e}")
            raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")
        except Exception as e:
            # Update analysis status to failed
            if cv_analysis_id:
                async with AsyncSessionLocal() as session:
                    result = await session.execute(select(CVAnalysis).filter(CVAnalysis.id == cv_analysis_id))
                    analysis = result.scalar_one_or_none()
                    if analysis:
                        analysis.extraction_status = "failed"
                        analysis.extraction_error = str(e)
                        analysis.processing_time = int((time.time() - start_time) * 1000)
                        await session.commit()
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


@router.get("/history")
async def get_cv_analysis_history(
    current_user: User = Depends(get_current_user_dependency)
):
    """
    Get CV analysis history for the current user
    
    Returns:
        List of user's CV analyses with metadata
    """
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(CVAnalysis)
                .filter(CVAnalysis.user_id == current_user.id)
                .order_by(CVAnalysis.created_at.desc())
            )
            analyses = result.scalars().all()
            
            # Convert to response format
            history = []
            for analysis in analyses:
                history.append({
                    "id": analysis.id,
                    "original_filename": analysis.original_filename,
                    "file_type": analysis.file_type,
                    "file_size": analysis.file_size,
                    "extraction_status": analysis.extraction_status,
                    "processing_time": analysis.processing_time,
                    "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
                    "has_structured_data": analysis.structured_data is not None
                })
            
            return {
                "history": history,
                "total": len(history)
            }
            
    except Exception as e:
        logger.error(f"Error fetching CV history: {e}")
        raise HTTPException(status_code=500, detail="Error fetching CV history")


@router.get("/analysis/{analysis_id}")
async def get_cv_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user_dependency)
):
    """
    Get specific CV analysis data
    
    Args:
        analysis_id: CV analysis ID
        
    Returns:
        Complete CV analysis data including structured data
    """
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(CVAnalysis)
                .filter(CVAnalysis.id == analysis_id)
                .filter(CVAnalysis.user_id == current_user.id)
            )
            analysis = result.scalar_one_or_none()
            
            if not analysis:
                raise HTTPException(status_code=404, detail="CV analysis not found")
            
            return {
                "id": analysis.id,
                "original_filename": analysis.original_filename,
                "file_type": analysis.file_type,
                "file_size": analysis.file_size,
                "extraction_status": analysis.extraction_status,
                "extraction_error": analysis.extraction_error,
                "processing_time": analysis.processing_time,
                "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
                "updated_at": analysis.updated_at.isoformat() if analysis.updated_at else None,
                "raw_text": analysis.raw_text,
                "structured_data": analysis.structured_data
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching CV analysis {analysis_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching CV analysis")


@router.get("/stats")
async def get_user_cv_stats(
    current_user: User = Depends(get_current_user_dependency)
):
    """
    Get CV analysis statistics for the current user
    
    Returns:
        Statistics about user's CV analyses
    """
    try:
        async with AsyncSessionLocal() as session:
            # Total analyses
            total_result = await session.execute(
                select(CVAnalysis)
                .filter(CVAnalysis.user_id == current_user.id)
            )
            total_analyses = len(total_result.scalars().all())
            
            # Successful analyses
            success_result = await session.execute(
                select(CVAnalysis)
                .filter(CVAnalysis.user_id == current_user.id)
                .filter(CVAnalysis.extraction_status == "completed")
            )
            successful_analyses = len(success_result.scalars().all())
            
            # Failed analyses
            failed_result = await session.execute(
                select(CVAnalysis)
                .filter(CVAnalysis.user_id == current_user.id)
                .filter(CVAnalysis.extraction_status == "failed")
            )
            failed_analyses = len(failed_result.scalars().all())
            
            return {
                "total_analyses": total_analyses,
                "successful_analyses": successful_analyses,
                "failed_analyses": failed_analyses,
                "pending_analyses": total_analyses - successful_analyses - failed_analyses
            }
            
    except Exception as e:
        logger.error(f"Error fetching CV stats: {e}")
        raise HTTPException(status_code=500, detail="Error fetching CV statistics")


@router.post("/analysis/{analysis_id}/generate-pdf")
async def regenerate_pdf_from_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user_dependency)
):
    """
    Regenerate PDF from saved CV analysis
    
    Args:
        analysis_id: CV analysis ID
        
    Returns:
        PDF file stream
    """
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(CVAnalysis)
                .filter(CVAnalysis.id == analysis_id)
                .filter(CVAnalysis.user_id == current_user.id)
                .filter(CVAnalysis.extraction_status == "completed")
            )
            analysis = result.scalar_one_or_none()
            
            if not analysis:
                raise HTTPException(status_code=404, detail="CV analysis not found or not completed")
            
            if not analysis.structured_data:
                raise HTTPException(status_code=400, detail="No structured data available for this analysis")
            
            # Convert structured_data back to DossierCompetences
            try:
                dossier_data = DossierCompetences.model_validate(analysis.structured_data)
            except Exception as e:
                logger.error(f"Error validating structured data: {e}")
                raise HTTPException(status_code=500, detail="Invalid structured data format")
            
            # Generate PDF
            pdf_buffer = generate_cv_pdf(dossier_data)
            
            filename = f"{analysis.original_filename.rsplit('.', 1)[0]}_cv_analysis.pdf"
            
            return StreamingResponse(
                io.BytesIO(pdf_buffer),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PDF from analysis {analysis_id}: {e}")
        raise HTTPException(status_code=500, detail="Error generating PDF")


@router.post("/analysis/{analysis_id}/generate-pptx")
async def regenerate_pptx_from_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user_dependency)
):
    """
    Regenerate PPTX from saved CV analysis
    
    Args:
        analysis_id: CV analysis ID
        
    Returns:
        PPTX file stream
    """
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(CVAnalysis)
                .filter(CVAnalysis.id == analysis_id)
                .filter(CVAnalysis.user_id == current_user.id)
                .filter(CVAnalysis.extraction_status == "completed")
            )
            analysis = result.scalar_one_or_none()
            
            if not analysis:
                raise HTTPException(status_code=404, detail="CV analysis not found or not completed")
            
            if not analysis.structured_data:
                raise HTTPException(status_code=400, detail="No structured data available for this analysis")
            
            # Convert structured_data back to DossierCompetences
            try:
                dossier_data = DossierCompetences.model_validate(analysis.structured_data)
            except Exception as e:
                logger.error(f"Error validating structured data: {e}")
                raise HTTPException(status_code=500, detail="Invalid structured data format")
            
            # Generate PPTX
            from .renderer.pptx_generator import generate_devoteam_pptx
            pptx_buffer = generate_devoteam_pptx(dossier_data)
            
            filename = f"{analysis.original_filename.rsplit('.', 1)[0]}_cv_analysis.pptx"
            
            return StreamingResponse(
                pptx_buffer,
                media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PPTX from analysis {analysis_id}: {e}")
        raise HTTPException(status_code=500, detail="Error generating PPTX")