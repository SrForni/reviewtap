# NFC Google Reviews

NFC card system that allows customers to easily leave a Google review while tracking and analyzing interactions with each NFC card.

## 🏗️ Architecture

```text
                    ┌───────────────┐
                    │   NFC Card    │
                    └───────┬───────┘
                            │
                         NFC Tap
                            │
                            ▼
                    ┌───────────────┐
                    │ API Gateway   │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    Lambda     │
                    │    Python     │
                    └───────┬───────┘
                            │
                   ┌────────┴────────┐
                   ▼                 ▼
             ┌───────────┐    ┌─────────────┐
             │ DynamoDB  │    │   Google    │
             │           │    │   Reviews   │
             └───────────┘    └─────────────┘


              Dashboard / Frontend
                       │
                       ▼
                  ┌─────────┐
                  │   S3    │
                  └────┬────┘
                       │
                       ▼
                  CloudFront
```

### Flow

1. A customer taps the NFC card with their phone.
2. The phone accesses the endpoint associated with the card.
3. API Gateway receives the request.
4. Lambda records the tap in DynamoDB.
5. Lambda redirects the customer to the Google Reviews page.
6. The dashboard displays activity and statistics.

## 📁 Project Structure

```text
nfc-google-reviews/
│
├── backend/
│   └── ...
│
├── frontend/
│   └── ...
│
├── terraform/
│   ├── main.tf
│   ├── lambda.tf
│   ├── api_gateway.tf
│   ├── dynamodb.tf
│   ├── s3.tf
│   ├── cloudfront.tf
│   └── iam.tf
│
└── README.md
```

> 🚧 Project under development.
