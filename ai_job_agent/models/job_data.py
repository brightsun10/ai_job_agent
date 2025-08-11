from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class JobData(BaseModel):
job_id: str
title: str
company: str
location: Optional[str] = None
description: Optional[str] = None
requirements: List[str] = []
apply_url: Optional[HttpUrl] = None
source: Optional[str] = None # linkedin, naukri
