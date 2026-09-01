from employee_survey_analyzer.aws_config import get_client

def analyze_sentiment(text: str) -> tuple[str, float]:
    """ Comprehend identifies the sentiment and confidence score for that classification """

    response = get_client("comprehend").detect_sentiment(
        Text=text,
        LanguageCode="en"
    )
    
    sentiment = response["Sentiment"]
    scores: dict[str, float] = {category.upper(): round(confidence, 3) 
                                for category, confidence in response["SentimentScore"].items()}

    return sentiment, scores[sentiment]
 
def redact_pii(text: str) -> str:
    """ Comprehend redacts any PII with some level of confidence and returns the redacted text """

    entities = get_client("comprehend").detect_pii_entities(
        Text=text,
        LanguageCode="en"
    )["Entities"]

    redacted_text = text
    for entity in reversed(entities):
        if entity["Score"] < 0.25: # low threshold to minimize false negatives (letting PII through)
            continue

        start_index = entity["BeginOffset"]
        end_index = entity["EndOffset"]
        redacted_text = redacted_text[:start_index] + "[REDACTED]" + redacted_text[end_index:]

    return redacted_text

def summarize_key_phrases(responses: list[str]) -> list[dict[str, str | int]]:
    """ Comprehend identifies key phrases across a list of responses and returns a descending order based on their count """

    key_phrases: dict[str, int] = {}

    for response in responses:
        phrases = get_client("comprehend").detect_key_phrases(
            Text=response,
            LanguageCode="en"
        )["KeyPhrases"]

        phrases_in_response = {
            phrase["Text"].lower()
            for phrase in phrases
            if phrase["Text"] != "[REDACTED]"
        }

        # count key_phrase instances by occurrence per response
        for phrase in phrases_in_response:
            key_phrases[phrase] = key_phrases.get(phrase, 0) + 1

    summary = [
        {
            "phrase": phrase,
            "count": count
        }
        for phrase, count in sorted(
            key_phrases.items(), 
            key=lambda item: item[1], # key is the count
            reverse=True
        )[:15] # grab top 15 descending
    ]

    return summary