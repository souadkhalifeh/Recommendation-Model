# PowerShell deployment script for Google Cloud Run
# Make sure you have gcloud CLI installed and authenticated

# Set your project ID
$PROJECT_ID = "your-gcp-project-id"
$SERVICE_NAME = "recommendation-api"
$REGION = "us-central1"

# Your Qdrant credentials (replace with your actual values)
$QDRANT_URL = "https://416e0f86-bedc-4757-90e9-b3ee36e0775a.europe-west3-0.gcp.cloud.qdrant.io"
$QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.L7CqmGVrzbyLDh27EYddMKJonr3G3HXGGoHEPr2EmUQ"

Write-Host "🚀 Deploying Recommendation API to Cloud Run..." -ForegroundColor Green

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
Write-Host "📋 Enabling required APIs..." -ForegroundColor Yellow
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and deploy using Cloud Build
Write-Host "🔨 Building and deploying..." -ForegroundColor Yellow
gcloud builds submit --config cloudbuild.yaml --substitutions "_QDRANT_URL=$QDRANT_URL,_QDRANT_API_KEY=$QDRANT_API_KEY"

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "🌐 Your API will be available at the URL shown above" -ForegroundColor Cyan
