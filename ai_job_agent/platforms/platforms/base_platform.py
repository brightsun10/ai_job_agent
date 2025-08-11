from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BasePlatform(ABC):
    """
    Abstract base class for job platform scrapers/bots.
    Defines the common interface that all platform-specific implementations must follow.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the platform with configuration.
        
        Args:
            config: Platform-specific configuration dictionary
        """
        self.config = config
        self.is_authenticated = False
        self.session = None
    
    @abstractmethod
    def authenticate(self, credentials: Dict[str, str]) -> bool:
        """
        Authenticate with the platform.
        
        Args:
            credentials: Dictionary containing login credentials
            
        Returns:
            bool: True if authentication successful, False otherwise
        """
        pass
    
    @abstractmethod
    def search_jobs(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for jobs on the platform.
        
        Args:
            query: Search query string
            filters: Optional filters for the search (location, experience, etc.)
            
        Returns:
            List of job dictionaries with standardized structure
        """
        pass
    
    @abstractmethod
    def get_job_details(self, job_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific job.
        
        Args:
            job_id: Unique identifier for the job
            
        Returns:
            Dictionary containing detailed job information
        """
        pass
    
    @abstractmethod
    def apply_to_job(self, job_id: str, application_data: Dict[str, Any]) -> bool:
        """
        Apply to a specific job.
        
        Args:
            job_id: Unique identifier for the job
            application_data: Application details (resume, cover letter, etc.)
            
        Returns:
            bool: True if application successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_application_status(self, application_id: str) -> str:
        """
        Get the status of a job application.
        
        Args:
            application_id: Unique identifier for the application
            
        Returns:
            str: Current status of the application
        """
        pass
    
    def logout(self) -> bool:
        """
        Logout from the platform.
        
        Returns:
            bool: True if logout successful, False otherwise
        """
        self.is_authenticated = False
        if self.session:
            self.session.close()
            self.session = None
        return True
    
    def get_platform_name(self) -> str:
        """
        Get the name of the platform.
        
        Returns:
            str: Platform name
        """
        return self.__class__.__name__.replace('Bot', '').replace('Platform', '')
