# Data Model

## Entity-Relationship Diagram

```mermaid
erDiagram
    SURVEY {
        int id PK
        string title
        text prompt
        string department
        date open_date
        date close_date
    }

    SURVEY_RESPONSE {
        int id PK
        text body
        datetime created_at
        int survey_id FK
        string sentiment
        float confidence_score
    }

    AUDIT_LOG {
        int id PK
        datetime timestamp
        string method
        string action
        string actor
        string event
        string correlation_id
    }

    SURVEY ||--o{ SURVEY_RESPONSE : "contains"
