""" Configuration file to share fixtures across test files """

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from employee_survey_analyzer.surveys.models import Response

@pytest.fixture
def comprehend_client() -> MagicMock:
    return MagicMock()

@pytest.fixture
def mock_get_client(comprehend_client):
    with patch("employee_survey_analyzer.analysis.service.get_client",
               return_value=comprehend_client) as mock_client:
        yield mock_client

@pytest.fixture
def sample_survey() -> dict[str, str]:
    return {
        "title": "Mid-Year Check-in",
        "prompt": "How supported do you feel by your manager these past 6 months?",
        "department": "Marketing",
        "open_date": "2026-06-20", 
        "close_date": "2026-10-20"
    }

@pytest.fixture
def sample_responses() -> list[Response]:
    response1 = Response.model_validate({
        "id": 1,
        "body": "My manager, John Smith, has been super supportive in onboarding me! He listens to my concerns and is flexible when I feel like I need more time to gradually ramp up to the tasks we perform here.",
        "survey_id": 1,
        "created_at": datetime(2026, 9, 1, 0, 0, 0),
        "sentiment": "POSITIVE",
        "confidence_score": 0.99
    })

    response2 = Response.model_validate({
        "id": 2,
        "body": "I feel as though my manager could listen more closely to my concerns. I recently had to take a leave of absence during a project and felt as though I was treated differently by my manager after returning.",
        "survey_id": 1,
        "created_at": datetime(2026, 9, 1, 0, 0, 0),
        "sentiment": "NEGATIVE",
        "confidence_score": 0.97
    })

    return [response1, response2]
