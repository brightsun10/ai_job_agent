"""User Profile Data Model

This module defines the Pydantic model for user profiles in the AI Job Agent system.
It includes all necessary fields for storing user information relevant to job applications.
"""

from typing import List, Optional
from datetime import date
from pydantic import BaseModel, EmailStr, HttpUrl, Field


class WorkExperience(BaseModel):
    """Model for work experience entries."""
    
    position: str = Field(..., description="Job title or position held")
    company: str = Field(..., description="Company or organization name")
    start_date: date = Field(..., description="Start date of employment")
    end_date: Optional[date] = Field(None, description="End date of employment (None if current job)")
    description: str = Field(..., description="Brief description of role and responsibilities")
    skills_used: List[str] = Field(default=[], description="Skills utilized in this role")


class Education(BaseModel):
    """Model for education entries."""
    
    degree: str = Field(..., description="Degree or certification obtained")
    school: str = Field(..., description="School, university, or institution name")
    field_of_study: str = Field(..., description="Major, field of study, or specialization")
    start_year: int = Field(..., description="Year started")
    end_year: Optional[int] = Field(None, description="Year completed (None if ongoing)")
    gpa: Optional[float] = Field(None, description="GPA or grade (optional)")
    achievements: List[str] = Field(default=[], description="Academic achievements or honors")


class UserProfile(BaseModel):
    """Main user profile model containing all user information for job applications.
    
    This model serves as the central data structure for storing user information
    that will be used across the AI job agent system for applications, resume
    generation, and profile matching.
    """
    
    # Personal Information
    name: str = Field(..., description="Full name of the user")
    email: EmailStr = Field(..., description="Primary email address")
    phone: str = Field(..., description="Primary phone number")
    location: str = Field(..., description="Current location (city, state/country)")
    
    # Professional Summary
    summary: str = Field(..., description="Professional summary or about section")
    skills: List[str] = Field(..., description="List of technical and soft skills")
    
    # Experience and Education
    experience: List[WorkExperience] = Field(..., description="List of work experiences")
    education: List[Education] = Field(..., description="Educational background")
    
    # Professional Profiles
    linkedin_url: Optional[HttpUrl] = Field(None, description="LinkedIn profile URL")
    naukri_url: Optional[HttpUrl] = Field(None, description="Naukri.com profile URL")
    github_url: Optional[HttpUrl] = Field(None, description="GitHub profile URL")
    portfolio_url: Optional[HttpUrl] = Field(None, description="Personal portfolio or website URL")
    
    # Additional Information
    certifications: List[str] = Field(default=[], description="Professional certifications")
    languages: List[str] = Field(default=[], description="Languages spoken")
    preferred_job_titles: List[str] = Field(default=[], description="Preferred job titles for applications")
    preferred_locations: List[str] = Field(default=[], description="Preferred work locations")
    salary_expectation: Optional[str] = Field(None, description="Expected salary range")
    
    class Config:
        """Pydantic configuration for the UserProfile model."""
        
        # Allow validation assignment to support updates
        validate_assignment = True
        
        # Use enum values for serialization
        use_enum_values = True
        
        # Example schema for documentation
        schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@email.com",
                "phone": "+1-555-0123",
                "location": "San Francisco, CA, USA",
                "summary": "Experienced software engineer with 5+ years in Python development",
                "skills": ["Python", "Django", "REST APIs", "PostgreSQL", "Docker"],
                "experience": [
                    {
                        "position": "Senior Software Engineer",
                        "company": "Tech Corp",
                        "start_date": "2020-01-15",
                        "end_date": None,
                        "description": "Lead backend development for web applications",
                        "skills_used": ["Python", "Django", "PostgreSQL"]
                    }
                ],
                "education": [
                    {
                        "degree": "Bachelor of Science",
                        "school": "University of California",
                        "field_of_study": "Computer Science",
                        "start_year": 2015,
                        "end_year": 2019,
                        "gpa": 3.8,
                        "achievements": ["Dean's List", "CS Honor Society"]
                    }
                ],
                "linkedin_url": "https://linkedin.com/in/johndoe",
                "preferred_job_titles": ["Software Engineer", "Backend Developer"],
                "preferred_locations": ["San Francisco", "Remote"]
            }
        }
