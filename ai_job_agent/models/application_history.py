from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ApplicationHistory(BaseModel):
job_id: str
status: str # submitted, failed, interview, offer, rejected
timestamp: datetime
answers: Optional[Dict[str, Any]] = None
error_reason: Optional[str] = None
