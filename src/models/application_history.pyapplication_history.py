"""Application History Data Model

This module defines the Pydantic model for tracking job applications in the AI Job Agent system.
It includes all necessary fields for recording applications and learning from outcomes.
"""

from typing import List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class ApplicationStatus(str, Enum):
    """Enumeration for application status states."""
    
    DRAFT = "draft"
    APPLIED = "applied"
    UNDER_REVIEW = "under_review"
    SCREENING = "screening"
    PHONE_INTERVIEW = "phone_interview"
    TECHNICAL_INTERVIEW = "technical_interview"
    ONSITE_INTERVIEW = "onsite_interview"
    FINAL_INTERVIEW = "final_interview"
    OFFER_RECEIVED = "offer_received"
    OFFER_ACCEPTED = "offer_accepted"
    OFFER_REJECTED = "offer_rejected"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    GHOSTED = "ghosted"


class InterviewType(str, Enum):
    """Enumeration for different types of interviews."""
    
    PHONE = "phone"
    VIDEO = "video"
    ONSITE = "onsite"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    PANEL = "panel"
    FINAL = "final"
    HR = "hr"


class InterviewRecord(BaseModel):
    """Model for recording interview details."""
    
    interview_type: InterviewType = Field(..., description="Type of interview conducted")
    scheduled_date: datetime = Field(..., description="Date and time the interview was scheduled")
    completed_date: Optional[datetime] = Field(None, description="Actual date and time interview was completed")
    interviewer_name: Optional[str] = Field(None, description="Name of the interviewer(s)")
    interviewer_title: Optional[str] = Field(None, description="Title/position of the interviewer")
    duration_minutes: Optional[int] = Field(None, description="Duration of interview in minutes")
    location: Optional[str] = Field(None, description="Interview location (office address, video link, etc.)")
    notes: Optional[str] = Field(None, description="Notes about the interview experience")
    questions_asked: List[str] = Field(default=[], description="Questions that were asked during the interview")
    feedback_received: Optional[str] = Field(None, description="Any feedback received after the interview")
    outcome: Optional[str] = Field(None, description="Interview outcome (passed, failed, pending)")


class ApplicationDocument(BaseModel):
    """Model for tracking documents submitted with application."""
    
    document_type: str = Field(..., description="Type of document (resume, cover_letter, portfolio, etc.)")
    file_name: str = Field(..., description="Name of the file submitted")
    submitted_date: datetime = Field(..., description="Date when document was submitted")
    version: Optional[str] = Field(None, description="Version or revision of the document")
    customized: bool = Field(False, description="Whether document was customized for this specific job")
    notes: Optional[str] = Field(None, description="Notes about document customization or content")


class ApplicationHistory(BaseModel):
    """Main application history model for tracking job applications.
    
    This model serves as the central data structure for recording and tracking
    job applications, learning from outcomes, and improving future applications.
    """
    
    # Application Identification
    application_id: str = Field(..., description="Unique identifier for this application")
    user_profile_id: str = Field(..., description="Reference to the user profile who applied")
    job_id: str = Field(..., description="Reference to the job posting (from JobData model)")
    
    # Basic Application Information
    applied_date: datetime = Field(
        default_factory=datetime.now,
        description="Date and time when application was submitted"
    )
    source_platform: str = Field(..., description="Platform where application was submitted")
    application_method: str = Field(
        ..., 
        description="How application was submitted (online_form, email, referral, etc.)"
    )
    
    # Current Status
    status: ApplicationStatus = Field(
        ApplicationStatus.APPLIED,
        description="Current status of the application"
    )
    last_updated: datetime = Field(
        default_factory=datetime.now,
        description="Last time the application status was updated"
    )
    
    # Application Details
    documents_submitted: List[ApplicationDocument] = Field(
        default=[],
        description="List of documents submitted with the application"
    )
    cover_letter_used: bool = Field(False, description="Whether a cover letter was included")
    referral_source: Optional[str] = Field(
        None,
        description="Source of referral if application came through referral"
    )
    
    # Communication and Updates
    communications: List[str] = Field(
        default=[],
        description="Log of communications related to this application"
    )
    status_updates: List[dict] = Field(
        default=[],
        description="History of status changes with timestamps"
    )
    
    # Interview Process
    interviews: List[InterviewRecord] = Field(
        default=[],
        description="Records of all interviews for this application"
    )
    
    # Outcome and Learning
    final_outcome: Optional[str] = Field(
        None,
        description="Final outcome of the application (hired, rejected, withdrawn)"
    )
    rejection_reason: Optional[str] = Field(
        None,
        description="Reason for rejection if provided"
    )
    feedback_received: Optional[str] = Field(
        None,
        description="Any feedback received about the application or interviews"
    )
    
    # Learning and Improvement
    lessons_learned: List[str] = Field(
        default=[],
        description="Key lessons learned from this application experience"
    )
    areas_for_improvement: List[str] = Field(
        default=[],
        description="Areas identified for improvement based on this application"
    )
    success_factors: List[str] = Field(
        default=[],
        description="Factors that contributed to success (if applicable)"
    )
    
    # Analytics and Tracking
    response_time_days: Optional[int] = Field(
        None,
        description="Days between application and first response"
    )
    total_process_days: Optional[int] = Field(
        None,
        description="Total days from application to final outcome"
    )
    interview_count: int = Field(
        0,
        description="Total number of interviews for this application"
    )
    
    # Internal Notes
    notes: Optional[str] = Field(
        None,
        description="Internal notes about this application"
    )
    follow_up_required: bool = Field(
        False,
        description="Whether follow-up action is required"
    )
    follow_up_date: Optional[datetime] = Field(
        None,
        description="Date when follow-up should be done"
    )
    
    @validator('status_updates', pre=True, always=True)
    def initialize_status_updates(cls, v, values):
        """Initialize status updates with the initial application status."""
        if not v and 'status' in values:
            return [{
                'status': values['status'],
                'date': datetime.now(),
                'notes': 'Application submitted'
            }]
        return v
    
    @validator('interview_count', pre=True, always=True)
    def calculate_interview_count(cls, v, values):
        """Calculate interview count based on interviews list."""
        if 'interviews' in values and values['interviews']:
            return len(values['interviews'])
        return v or 0
    
    def update_status(self, new_status: ApplicationStatus, notes: Optional[str] = None):
        """Update application status and add to status history.
        
        Args:
            new_status: The new status to set
            notes: Optional notes about the status change
        """
        self.status = new_status
        self.last_updated = datetime.now()
        
        status_update = {
            'status': new_status,
            'date': self.last_updated,
            'notes': notes or f'Status updated to {new_status}'
        }
        self.status_updates.append(status_update)
    
    def add_interview(self, interview: InterviewRecord):
        """Add an interview record and update interview count.
        
        Args:
            interview: The interview record to add
        """
        self.interviews.append(interview)
        self.interview_count = len(self.interviews)
    
    def calculate_metrics(self):
        """Calculate response time and process duration metrics."""
        if self.status_updates and len(self.status_updates) > 1:
            first_response = next(
                (update for update in self.status_updates 
                 if update['status'] != ApplicationStatus.APPLIED), 
                None
            )
            
            if first_response:
                response_delta = first_response['date'] - self.applied_date
                self.response_time_days = response_delta.days
        
        if self.final_outcome:
            process_delta = self.last_updated - self.applied_date
            self.total_process_days = process_delta.days
    
    class Config:
        """Pydantic configuration for the ApplicationHistory model."""
        
        # Allow validation assignment to support updates
        validate_assignment = True
        
        # Use enum values for serialization
        use_enum_values = True
        
        # Example schema for documentation
        schema_extra = {
            "example": {
                "application_id": "app-001-techcorp-senior-eng",
                "user_profile_id": "user-john-doe",
                "job_id": "tech-corp-senior-eng-001",
                "applied_date": "2025-08-11T10:30:00",
                "source_platform": "LinkedIn",
                "application_method": "online_form",
                "status": "under_review",
                "documents_submitted": [
                    {
                        "document_type": "resume",
                        "file_name": "john_doe_resume_techcorp.pdf",
                        "submitted_date": "2025-08-11T10:30:00",
                        "customized": True,
                        "notes": "Highlighted AI and machine learning experience"
                    },
                    {
                        "document_type": "cover_letter",
                        "file_name": "cover_letter_techcorp.pdf",
                        "submitted_date": "2025-08-11T10:30:00",
                        "customized": True
                    }
                ],
                "cover_letter_used": True,
                "status_updates": [
                    {
                        "status": "applied",
                        "date": "2025-08-11T10:30:00",
                        "notes": "Application submitted"
                    },
                    {
                        "status": "under_review",
                        "date": "2025-08-13T14:20:00",
                        "notes": "Application moved to review stage"
                    }
                ],
                "interviews": [],
                "response_time_days": 2,
                "interview_count": 0,
                "notes": "Strong match for required skills, emphasized AI experience",
                "follow_up_required": True,
                "follow_up_date": "2025-08-20T09:00:00"
            }
        }
