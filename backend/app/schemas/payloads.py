from pydantic import BaseModel, Field

class NLRequest(BaseModel):
    command: str = Field(..., example="Schedule a meeting with Alice next Wednesday at 3pm")

class APIResponse(BaseModel):
    raw_output: str
    parsed_json: dict | None
    status: str
