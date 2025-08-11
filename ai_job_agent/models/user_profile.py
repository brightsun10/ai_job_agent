from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class Experience(BaseModel):
company: str
title: str
start_date: Optional[str] = None
end_date: Optional[str] = None
summary: Optional[str] = None
technologies: List[str] = []

class Education(BaseModel):
institution: str
degree: Optional[str] = None
start_year: Optional[int] = None
end_year: Optional[int] = None

class UserProfile(BaseModel):
full_name: str
email: EmailStr
phone: Optional[str] = None
location: Optional[str] = None
skills: List[str] = []
experience: List[Experience] = []
education: List[Education] = []
linkedin_url: Optional[str] = None
naukri_url: Optional[str] = None
