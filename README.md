# Employee Pulse Survey Analyzer
An anonymous employee pulse-survey backend for open-ended prompts and feedback from staff. Exposes a REST API to create surveys and view anonymous responses. Survey responses are automatically summarized for sentiment and screened for personal identifiable information (PII) by Amazon Comprehend before data is stored.

## Setup
### Usage:
1. Install: `docker compose up -d --build`
1. Run app: `flask --app employee_survey_analyzer.app run`

<br><br>
### Testing:
1. Install optional dependencies (for tests): `pip install -e ".[test]"`
1. Run tests: `python -m pytest`

## Edge Case Handling
### Editing Surveys:
A survey that has any responses associated with it can no longer have its prompt updated because that risks invalidating the response. Versioned surveys are not supported and updated prompts should be treated as new surveys.

### Response Immutability:
A submitted response can no longer be edited to prevent the employee or an administrator from quietly altering the answer either accidentally or intentionally afterwards. Responses changing afterwards would also mess with analysis endpoints, such as summary generation and sentiment analysis.

### Comprehend is Unavailable:
If either sentiment analysis or PII detection fails due to an AWS `ClientError` or `BotoError`, then that response submission is rejected due to that exception being caught by the global errorhandlers defined in `app.py`. The calls to AWS Comprehend happen before anything in the database to ensure that a response missing a sentiment or PII check doesn't get stored because I think submission should be rejected outright (and cause a slight inconvenience) rather than risk some PII making it through.

### PII Detected in a Response:
A PII span is redacted (e.g. `"[REDACTED]"`) in place before storage. This is opposed to being rejected outright as inconveniences in response submission could serve to discourage employees from responding or providing feedback entirely. PII detection is kept broad to catch more spans, preferring redaction of a non-PII span rather than allowing one to be stored.

### Submission to a Closed or Not-Yet-Open Survey
Clear error messages distinguishing between surveys that are not-yet-open (drafts) and surveys that have already been closed.

### Empty or Trivially Short Response
A minimum response length of 15 characters, which is pretty standard for text inputs and restricts 1-3 word (e.g. "ok") responses that are generally not as helpful for open-ended prompts (and also filters out short, accidental entries). A higher limit would likely serve to discourage employees who wouldn't want to write a long response.

### Concurrent Mutations:
1. <b>Survey closed while response is mid-submission</b>:
Survey availability is validated (`surveys.services.validate_response()`) before a response is created, so if the survey's `close_date` is changed after the response passes validation but before the response is created in the database, then there is no subsequent check in the database layer and the response will go through.

1. <b>Response deleted while survey summary endpoint is being computed</b>:
Similarly, the survey summary endpoint only makes one check at the beginning to grab all of the responses. If a response is deleted after that list of responses is generated, then that response will still go through and be used for sentiment analysis and keyword detection in AWS Comprehend.

## Resources
1. [Entity-relationship diagram](doc/data_model.md)
1. [IAM role policy for Comprehend](infra/policy/comprehend_policy.json)
1. [Kanban board](https://app.asana.com/1/1134946782879758/project/1217954995482365/board/1217954814716903)