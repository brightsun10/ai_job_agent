"""Platforms package for AI Job Agent.

This package contains platform-specific implementations for various job platforms:
- LinkedIn Bot (linkedin_bot.py)
- Naukri Bot (naukri_bot.py)
- Base Platform (base_platform.py)
"""

# Import all platform modules to make them available when importing the package
from .base_platform import *
from .linkedin_bot import *
from .naukri_bot import *
