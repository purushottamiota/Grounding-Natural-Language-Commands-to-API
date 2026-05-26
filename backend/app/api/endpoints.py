import json
from fastapi import APIRouter, HTTPException
from app.schemas.payloads import NLRequest, APIResponse
from app.models.nlp_model import nlp_pipeline
from app.services.parser import postprocess

router = APIRouter()

@router.post("/parse", response_model=APIResponse)
async def parse_command(request: NLRequest):
    try:
        raw_output = nlp_pipeline.generate(request.command)
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Model is currently loading or unavailable.")
    
    parsed = None
    status = "success"

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError:
        start = raw_output.find("{")
        end   = raw_output.rfind("}") + 1
        if start != -1 and end > start:
            try:
                parsed = json.loads(raw_output[start:end])
            except json.JSONDecodeError:
                status = "failed_parsing"
        else:
            status = "failed_parsing"

    if not parsed:
        raise HTTPException(
            status_code=422,
            detail={"message": "Could not generate valid JSON.", "raw_output": raw_output},
        )

    parsed = postprocess(parsed, request.command)

    return APIResponse(raw_output=raw_output, parsed_json=parsed, status=status)
