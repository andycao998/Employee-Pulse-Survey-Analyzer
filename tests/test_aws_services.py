""" Unit tests for AWS Comprehend calls (mocked client) """

import pytest
from employee_survey_analyzer.analysis import service
from botocore.exceptions import BotoCoreError, ClientError


# ======================== DETECT_SENTIMENT ========================

def test_positive_sentiment_detection(comprehend_client, mock_get_client):
    comprehend_client.detect_sentiment.return_value = {
        "Sentiment": "POSITIVE",
        "SentimentScore": {
            "Positive": 0.97,
            "Negative": 0.01,
            "Neutral": 0.01,
            "Mixed": 0.01,
        },
    }

    survey_response = "I feel good about the company direction!"
    sentiment, score = service.analyze_sentiment(survey_response)

    assert sentiment == "POSITIVE"
    assert score == 0.97

    mock_get_client.assert_called_once_with("comprehend")
    comprehend_client.detect_sentiment.assert_called_once_with(
        Text="I feel good about the company direction!",
        LanguageCode="en",
    )


def test_negative_sentiment_detection(comprehend_client, mock_get_client):
    comprehend_client.detect_sentiment.return_value = {
        "Sentiment": "NEGATIVE",
        "SentimentScore": {
            "Positive": 0.01,
            "Negative": 0.97,
            "Neutral": 0.01,
            "Mixed": 0.01,
        },
    }

    survey_response = "I feel terrible about the company direction!"
    sentiment, score = service.analyze_sentiment(survey_response)

    assert sentiment == "NEGATIVE"
    assert score == 0.97

    mock_get_client.assert_called_once_with("comprehend")
    comprehend_client.detect_sentiment.assert_called_once_with(
        Text="I feel terrible about the company direction!",
        LanguageCode="en",
    )

def test_neutral_sentiment_detection(comprehend_client, mock_get_client):
    comprehend_client.detect_sentiment.return_value = {
        "Sentiment": "NEUTRAL",
        "SentimentScore": {
            "Positive": 0.01,
            "Negative": 0.03,
            "Neutral": 0.95,
            "Mixed": 0.01,
        },
    }

    survey_response = "I'm indifferent about the company direction."
    sentiment, score = service.analyze_sentiment(survey_response)

    assert sentiment == "NEUTRAL"
    assert score == 0.95

    mock_get_client.assert_called_once_with("comprehend")
    comprehend_client.detect_sentiment.assert_called_once_with(
        Text="I'm indifferent about the company direction.",
        LanguageCode="en",
    )

def test_mixed_sentiment_detection(comprehend_client, mock_get_client):
    comprehend_client.detect_sentiment.return_value = {
        "Sentiment": "MIXED",
        "SentimentScore": {
            "Positive": 0.01,
            "Negative": 0.03,
            "Neutral": 0.01,
            "Mixed": 0.95,
        },
    }

    survey_response = "I'm conflicted about the company direction."
    sentiment, score = service.analyze_sentiment(survey_response)

    assert sentiment == "MIXED"
    assert score == 0.95

    mock_get_client.assert_called_once_with("comprehend")
    comprehend_client.detect_sentiment.assert_called_once_with(
        Text="I'm conflicted about the company direction.",
        LanguageCode="en",
    )

@pytest.mark.parametrize("error", [
    ClientError(error_response={"Error": {}}, operation_name="AWS call failed"),
    BotoCoreError()
])
def test_sentiment_analysis_error(comprehend_client, mock_get_client, error):
    comprehend_client.detect_sentiment.side_effect = error
    with pytest.raises((ClientError, BotoCoreError)):
        service.analyze_sentiment("I'm conflicted about the company direction.")

# ======================== DETECT_PII_ENTITIES ========================

def test_redact_pii(comprehend_client, mock_get_client):
    name = "Andy Cao"
    email = "acao@skillstorm.com"
    phone_number = "111-111-1111"
    address = "1234 N. Big Rd. Chicago, IL"
    survey_response = f"Hi, I'm {name}. You can reach me at {email} or my number at {phone_number}. I currently reside at {address}."
    
    comprehend_client.detect_pii_entities.return_value = {
        "Entities": [
            {
                "Score": 0.99,
                "Type": "NAME",
                "BeginOffset": 8,
                "EndOffset": 15,
            },
            {
                "Score": 0.99,
                "Type": "EMAIL",
                "BeginOffset": 38,
                "EndOffset": 56,
            },
            {
                "Score": 0.99,
                "Type": "PHONE",
                "BeginOffset": 74,
                "EndOffset": 85,
            },
            {
                "Score": 0.99,
                "Type": "ADDRESS",
                "BeginOffset": 110,
                "EndOffset": 136,
            },
        ]
    }

    redacted_response = service.redact_pii(survey_response)

    assert survey_response != redacted_response
    assert name not in redacted_response
    assert email not in redacted_response
    assert phone_number not in redacted_response
    assert address not in redacted_response
    assert redacted_response.count("[REDACTED]") == 4

    mock_get_client.assert_called_once_with("comprehend")
    comprehend_client.detect_pii_entities.assert_called_once_with(
        Text=survey_response,
        LanguageCode="en",
    )

def test_no_pii_found(comprehend_client, mock_get_client):
    survey_response = f"Hi. You can email or call me. I currently reside in the city of Chicago."
    
    comprehend_client.detect_pii_entities.return_value = {
        "Entities": []
    }

    redacted_response = service.redact_pii(survey_response)

    assert survey_response == redacted_response
    assert redacted_response.count("[REDACTED]") == 0

    mock_get_client.assert_called_once_with("comprehend")
    comprehend_client.detect_pii_entities.assert_called_once_with(
        Text=survey_response,
        LanguageCode="en",
    )

@pytest.mark.parametrize("error", [
    ClientError(error_response={"Error": {}}, operation_name="AWS call failed"),
    BotoCoreError()
])
def test_pii_detection_error(comprehend_client, mock_get_client, error):
    comprehend_client.detect_pii_entities.side_effect = error
    with pytest.raises((ClientError, BotoCoreError)):
        service.redact_pii("I'm conflicted about the company direction.")

# ======================== DETECT_KEY_PHRASES ========================

def test_key_phrases_one_response(comprehend_client, mock_get_client):
    survey_response = "The new onboarding process is confusing."

    comprehend_client.detect_key_phrases.return_value = {
        "KeyPhrases": [
            {
                "Score": 0.99,
                "Text": "new onboarding process",
                "BeginOffset": 4,
                "EndOffset": 26,
            },
            {
                "Score": 0.98,
                "Text": "confusing",
                "BeginOffset": 30,
                "EndOffset": 40,
            },
        ]
    }

    summarization = service.summarize_key_phrases([survey_response])
    expected = [
        {
            "phrase": "new onboarding process",
            "count": 1
        },
        {
            "phrase": "confusing",
            "count": 1
        }
    ]

    # sort them so that assertion doesn't fail every so often due to ordering of phrases
    assert sorted(summarization, key=lambda x: x["phrase"]) == sorted(expected, key=lambda x: x["phrase"])

    mock_get_client.assert_called_once_with("comprehend")
    comprehend_client.detect_key_phrases.assert_called_once_with(
        Text=survey_response,
        LanguageCode="en",
    )

def test_key_phrases_multiple_responses(comprehend_client, mock_get_client):
    survey_responses = [
        "The new onboarding process is confusing.",
        "The new onboarding process is confusing.",
        "The new onboarding process is confusing."
    ]


    comprehend_client.detect_key_phrases.return_value = {
        "KeyPhrases": [
            {
                "Score": 0.99,
                "Text": "new onboarding process",
                "BeginOffset": 4,
                "EndOffset": 26,
            },
            {
                "Score": 0.98,
                "Text": "confusing",
                "BeginOffset": 30,
                "EndOffset": 40,
            },
        ]
    }

    summarization = service.summarize_key_phrases(survey_responses)
    expected = [
        {
            "phrase": "new onboarding process",
            "count": 3
        },
        {
            "phrase": "confusing",
            "count": 3
        }
    ]

    # sort them so that assertion doesn't fail every so often due to ordering of phrases
    assert sorted(summarization, key=lambda x: x["phrase"]) == sorted(expected, key=lambda x: x["phrase"])

    assert mock_get_client.call_count == 3
    assert comprehend_client.detect_key_phrases.call_count == 3

@pytest.mark.parametrize("error", [
    ClientError(error_response={"Error": {}}, operation_name="AWS call failed"),
    BotoCoreError()
])
def test_key_phrase_detection_error(comprehend_client, mock_get_client, error):
    comprehend_client.detect_key_phrases.side_effect = error
    with pytest.raises((ClientError, BotoCoreError)):
        service.summarize_key_phrases(["I'm conflicted about the company direction."])