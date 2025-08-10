"""
Импорт всех моделей в правильном порядке для избежания circular imports.
"""

# Сначала базовые модели
from .base import BaseModel
from .user import User
from .token import UserToken

# Затем проектные модели
from .project import Project
from .text import Text
from .character import Character

# Чек-листы временно отключены
# from .checklist import (
#     Checklist, ChecklistSection, ChecklistSubsection,
#     ChecklistQuestionGroup, ChecklistQuestion, ChecklistResponse, 
#     ChecklistResponseHistory, SourceType
# )

__all__ = [
    "BaseModel",
    "User", 
    "UserToken",
    "Project",
    "Text", 
    "Character",
    # "Checklist", "ChecklistSection", "ChecklistSubsection",
    # "ChecklistQuestionGroup", "ChecklistQuestion", "ChecklistResponse", 
    # "ChecklistResponseHistory", "SourceType"
]
