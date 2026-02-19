# fgtc-calc
An application to dynamically price used PC builds using live market conditions at [Free Geek Twin Cities](https://www.freegeektwincities.org/).

Python backend built using [Litestar](https://litestar.dev/), [SQLAlchemy](https://www.sqlalchemy.org/), [Alembic](https://alembic.sqlalchemy.org/en/latest/)

Web frontend built using [Vite](https://vite.dev/), [TailwindCSS](https://tailwindcss.com/), [DaisyUI](https://daisyui.com/)

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

The application can be updated by updating the repository on the server (by updating through git or by uploading a new version)
and re-running `docker compose up --build -d`

## Obtaining eBay API Credentials
1) Register with an eBay Developer account at [developer.ebay.com](https://developer.ebay.com/signin?tab=register)
2) Under your user account in the upper right, go to **Application Keysets**
3) Enter a name for the application
4) Under **Production**, Click **Create a keyset**, and fill out the contact info if prompted
5) Click the link to apply for a compliance exemption
6) Check **Exempted from Marketplace Account Deletion** and select **I do not persist eBay data**, then **Submit**
7) Go back to **Application Keysets** and copy the **App ID**, **Dev ID**, and **Cert ID** from that page. Use these for `EBAY_APP_ID`, `EBAY_DEV_ID`, and `EBAY_SECRET` respectively
8) Under **App ID**, click **User Tokens**
9) Under **Get a Token from eBay via Your Application**, click **Add eBay Redirect URL** and confirm address and contact info
10) Next to **Your branded eBay Production Sign In (OAuth)**, click **See all**, and copy everything ***__EXCLUDING the `See less` at the end__***. Use this for `EBAY_REDIRECT`

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