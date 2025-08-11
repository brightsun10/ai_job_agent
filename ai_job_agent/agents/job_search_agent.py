from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from ai_job_agent.models.job_data import JobData

@dataclass
class JobSearchConfig:
    title: Optional[str] = None
    location: Optional[str] = None
    remote_ok: bool = True
    sources: List[str] = field(default_factory=lambda: ["linkedin", "naukri"])
    limit: int = 20

class JobSearchAgent:
    """
    Minimal stub for job search agent.
    Responsible for retrieving job listings from configured sources.
    """

    def __init__(self, config: Optional[JobSearchConfig] = None) -> None:
        self.config = config or JobSearchConfig()

    def search(self, criteria: Optional[Dict[str, Any]] = None) -> List[JobData]:
        """
        Return a list of JobData items based on criteria.
        Currently returns a static placeholder list.
        """
        criteria = criteria or {}
        title = criteria.get("title") or self.config.title or "Software Engineer"
        location = criteria.get("location") or self.config.location or "Bengaluru"
        jobs = [
            JobData(
                job_id="demo-1",
                title=title,
                company="Example Corp",
                location=location,
                description="Build and ship features with Python.",
                requirements=["Python", "Git", "REST"],
                source="linkedin",
            ),
            JobData(
                job_id="demo-2",
                title=title,
                company="Sample Labs",
                location=location,
                description="Data pipelines and ML ops.",
                requirements=["SQL", "Airflow", "PySpark"],
                source="naukri",
            ),
        ]
        return jobs[: self.config.limit]
