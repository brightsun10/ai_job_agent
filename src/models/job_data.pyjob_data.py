"""Job Data Model

This module defines the Pydantic model for job postings in the AI Job Agent system.
It includes all necessary fields for storing job information for applications and matching.
"""

from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel, HttpUrl, Field
from enum import Enum


class JobType(str, Enum):
    """Enumeration for different job types."""
    
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"
    TEMPORARY = "temporary"


class ExperienceLevel(str, Enum):
    """Enumeration for experience levels."""
    
    ENTRY_LEVEL = "entry-level"
    ASSOCIATE = "associate"
    MID_LEVEL = "mid-level"
    SENIOR_LEVEL = "senior-level"
    DIRECTOR = "director"
    EXECUTIVE = "executive"


class WorkLocation(str, Enum):
    """Enumeration for work location types."""
    
    REMOTE = "remote"
    ONSITE = "onsite"
    HYBRID = "hybrid"


class CompanyInfo(BaseModel):
    """Model for company information."""
    
    name: str = Field(..., description="Company name")
    size: Optional[str] = Field(None, description="Company size (e.g., '1-10', '50-100', '1000+')")
    industry: Optional[str] = Field(None, description="Industry or sector")
    website: Optional[HttpUrl] = Field(None, description="Company website URL")
    description: Optional[str] = Field(None, description="Brief company description")
    logo_url: Optional[HttpUrl] = Field(None, description="Company logo image URL")


class SalaryInfo(BaseModel):
    """Model for salary information."""
    
    min_salary: Optional[float] = Field(None, description="Minimum salary amount")
    max_salary: Optional[float] = Field(None, description="Maximum salary amount")
    currency: str = Field("USD", description="Currency code (e.g., USD, EUR, INR)")
    period: str = Field("annually", description="Salary period (annually, monthly, hourly)")
    is_negotiable: bool = Field(False, description="Whether salary is negotiable")


class JobData(BaseModel):
    """Main job data model containing all information about a job posting.
    
    This model serves as the central data structure for storing job information
    that will be used across the AI job agent system for applications, matching,
    and tracking.
    """
    
    # Basic Job Information
    title: str = Field(..., description="Job title or position name")
    company: CompanyInfo = Field(..., description="Company information")
    location: str = Field(..., description="Job location (city, state/country)")
    work_location_type: WorkLocation = Field(
        WorkLocation.ONSITE, 
        description="Type of work location (remote, onsite, hybrid)"
    )
    
    # Job Details
    description: str = Field(..., description="Full job description")
    responsibilities: List[str] = Field(
        default=[], 
        description="List of key responsibilities"
    )
    requirements: List[str] = Field(
        default=[], 
        description="Job requirements and qualifications"
    )
    required_skills: List[str] = Field(
        default=[], 
        description="Required technical and soft skills"
    )
    preferred_skills: List[str] = Field(
        default=[], 
        description="Preferred or nice-to-have skills"
    )
    
    # Employment Information
    job_type: JobType = Field(
        JobType.FULL_TIME, 
        description="Type of employment"
    )
    experience_level: ExperienceLevel = Field(
        ExperienceLevel.MID_LEVEL, 
        description="Required experience level"
    )
    experience_years: Optional[str] = Field(
        None, 
        description="Required years of experience (e.g., '2-4 years')"
    )
    
    # Compensation
    salary: Optional[SalaryInfo] = Field(
        None, 
        description="Salary information if available"
    )
    benefits: List[str] = Field(
        default=[], 
        description="List of benefits offered"
    )
    
    # Application Information
    application_url: HttpUrl = Field(..., description="URL to apply for the job")
    application_deadline: Optional[date] = Field(
        None, 
        description="Application deadline date"
    )
    posted_date: datetime = Field(
        default_factory=datetime.now, 
        description="Date when job was posted"
    )
    
    # Platform and Tracking
    source_platform: str = Field(..., description="Platform where job was found (e.g., 'LinkedIn', 'Indeed')")
    job_id: str = Field(..., description="Unique job ID from the source platform")
    external_url: Optional[HttpUrl] = Field(
        None, 
        description="Original job posting URL on the platform"
    )
    
    # Company-specific Questions
    screening_questions: List[str] = Field(
        default=[], 
        description="Company-specific screening questions"
    )
    
    # Additional Information
    education_requirements: Optional[str] = Field(
        None, 
        description="Education requirements (e.g., 'Bachelor's degree')"
    )
    certifications: List[str] = Field(
        default=[], 
        description="Required or preferred certifications"
    )
    languages: List[str] = Field(
        default=[], 
        description="Required or preferred languages"
    )
    
    # Internal Tracking
    is_active: bool = Field(True, description="Whether the job posting is still active")
    match_score: Optional[float] = Field(
        None, 
        description="AI-calculated match score with user profile (0-100)"
    )
    notes: Optional[str] = Field(
        None, 
        description="Internal notes about the job posting"
    )
    
    class Config:
        """Pydantic configuration for the JobData model."""
        
        # Allow validation assignment to support updates
        validate_assignment = True
        
        # Use enum values for serialization
        use_enum_values = True
        
        # Example schema for documentation
        schema_extra = {
            "example": {
                "title": "Senior Software Engineer",
                "company": {
                    "name": "TechCorp Inc.",
                    "size": "100-500",
                    "industry": "Technology",
                    "website": "https://techcorp.com",
                    "description": "Leading technology company specializing in AI solutions"
                },
                "location": "San Francisco, CA, USA",
                "work_location_type": "hybrid",
                "description": "We are looking for a senior software engineer to join our AI team...",
                "responsibilities": [
                    "Design and develop scalable AI systems",
                    "Lead technical discussions and code reviews",
                    "Mentor junior developers"
                ],
                "requirements": [
                    "5+ years of software development experience",
                    "Strong knowledge of Python and machine learning",
                    "Experience with cloud platforms"
                ],
                "required_skills": ["Python", "TensorFlow", "AWS", "Docker"],
                "preferred_skills": ["Kubernetes", "MLOps", "React"],
                "job_type": "full-time",
                "experience_level": "senior-level",
                "experience_years": "5-8 years",
                "salary": {
                    "min_salary": 120000,
                    "max_salary": 180000,
                    "currency": "USD",
                    "period": "annually",
                    "is_negotiable": True
                },
                "benefits": ["Health insurance", "401k", "Flexible PTO"],
                "application_url": "https://techcorp.com/careers/senior-engineer-123",
                "application_deadline": "2025-09-15",
                "source_platform": "LinkedIn",
                "job_id": "tech-corp-senior-eng-001",
                "external_url": "https://linkedin.com/jobs/view/123456789",
                "education_requirements": "Bachelor's degree in Computer Science or related field",
                "match_score": 85.5
            }
        }
