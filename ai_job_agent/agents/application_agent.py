from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from ai_job_agent.models.application_history import ApplicationHistory
from datetime import datetime

@dataclass
class ApplicationConfig:
    dry_run: bool = True  # when True, do not actually submit applications

class ApplicationAgent:
    """
    Minimal stub for application agent.
    Responsible for generating answers and submitting applications.
    """

    def __init__(self, config: Optional[ApplicationConfig] = None) -> None:
        self.config = config or ApplicationConfig()

    def prepare_answers(self, job: Dict[str, Any], resume: Optional[str] = None) -> Dict[str, Any]:
        """
        Produce simple placeholder Q&A for application forms.
        """
        return {
            "why_hire": "I match the role requirements and can deliver impact quickly.",
            "relevant_experience": "3+ projects using similar stack and workflows.",
            "notice_period": "Immediate",
        }

    def apply(self, job_id: str, answers: Dict[str, Any]) -> Tuple[bool, ApplicationHistory]:
        """
        Submit or simulate an application.
        Returns (success, ApplicationHistory).
        """
        success = True
        reason = None
        if self.config.dry_run:
            # Simulate submission without side effects
            success = True
            reason = None

        history = ApplicationHistory(
            job_id=job_id,
            status="submitted" if success else "failed",
            timestamp=datetime.utcnow(),
            answers=answers,
            error_reason=reason,
        )
        return success, history
