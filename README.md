## Development Setup
1) Install the Python package manager `uv` (see [uv Installation Docs](https://docs.astral.sh/uv/getting-started/installation/))
2) Create a `.env` file with eBay API credentials (see [Obtaining eBay API Credentials](#obtaining-ebay-api-credentials) and [Creating the .env file](#creating-the-env-file))
3) Run `uv sync` to download and install dependent packages
4) Run `uv run app run` to run a local development server
5) Open a browser and go to [http://localhost:8000](http://localhost:8000)

## Production Deployment
### Requirements
- Linux Host with docker and docker-compose installed
- eBay API credentials (see [Obtaining eBay API Credentials](#obtaining-ebay-api-credentials))

### Deployment Steps
1) Clone or upload this repository to a working directory on the server
2) Create the environment file with API credentials (see [Creating the .env file](#creating-the-env-file))
3) Run `docker compose up --build -d` to bring the application and all dependencies online

## Obtaining eBay API Credentials
1) Register with an eBay Developer account at [developer.ebay.com](https://developer.ebay.com/signin?tab=register)
- Note: Developer accounts may be manually reviewed, and it may take some time before the account becomes active.
2) 

## Creating the .env file
At the project root, create a file called `.env` with your eBay API credentials like shown:
```dotenv
EBAY_APP_ID=Jac*****-********-PRD-*********-********
EBAY_DEV_ID=2******8-****-****-****-4**********f
EBAY_SECRET=PRD-************-****-****-****-**8a
EBAY_USERNAME=***********
EBAY_PASSWORD=***********
EBAY_REDIRECT=https://auth.ebay.com/oauth2...
```