from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.services.detection_service import detection_service
from app.utils.image_utils import load_image
from app.db import get_db
from app.models.analysis import Analysis, UploadMethod
from app.models.analysis_result import AnalysisResult
from app.models.user import User
from app.api.auth import get_current_user
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.post("/api/detect")
async def detect(
    file: UploadFile = File(...),
    upload_method: str = Header(default="file"),  # Expected: 'file', 'camera', or 'clipboard'
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        contents = await file.read()
        image = load_image(contents)
        
        # Run detection
        result = await detection_service.detect_image(image)
        
        # Try to save to database (optional - don't fail if this errors)
        try:
            # Map upload method string to enum
            upload_method_enum = UploadMethod.FILE  # Default
            if upload_method.lower() == "camera":
                upload_method_enum = UploadMethod.CAMERA
            elif upload_method.lower() == "clipboard":
                upload_method_enum = UploadMethod.CLIPBOARD
            
            # Save analysis to database
            analysis = Analysis(
                user_id=current_user.id,
                image_data=contents,
                image_filename=file.filename,
                upload_method=upload_method_enum
            )
            db.add(analysis)
            db.flush()  # Get the analysis ID
            
            # Save analysis result
            decision = result.get("final_decision", {})
            analysis_result = AnalysisResult(
                analysis_id=analysis.id,
                verdict=decision.get("label", "unknown"),
                prob_ai=decision.get("prob_ai"),
                prob_real=decision.get("prob_real"),
                confidence=decision.get("prob_ai") if decision.get("label") == "ai_generated" else decision.get("prob_real"),
                source_model=decision.get("source", "unknown"),
                feature_metrics=None,  # Can be populated later if needed
                raw_response=result
            )
            db.add(analysis_result)
            db.commit()
            
            logger.info(f"Analysis {analysis.id} saved for user {current_user.username}")
        except Exception as db_error:
            db.rollback()
            logger.warning(f"Failed to save analysis to database: {db_error}")
            # Continue anyway - detection result is still valid
        
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

