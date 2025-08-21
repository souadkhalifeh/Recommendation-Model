# Deployment Guide for Google Cloud Run

This guide will help you deploy your Recommendation API to Google Cloud Run.

## Prerequisites

1. **Google Cloud Account**: Make sure you have a Google Cloud account with billing enabled
2. **gcloud CLI**: Install the Google Cloud CLI from https://cloud.google.com/sdk/docs/install
3. **Docker**: Install Docker Desktop (optional, for local testing)

## Setup Steps

### 1. Authenticate with Google Cloud

```bash
gcloud auth login
gcloud auth configure-docker
```

### 2. Create or Select a Project

```bash
# Create a new project (optional)
gcloud projects create your-project-id --name="Recommendation API"

# Set your project
gcloud config set project your-project-id
```

### 3. Update Configuration

Edit the following files with your actual values:

**deploy.sh** or **deploy.ps1**:
- Replace `your-gcp-project-id` with your actual Google Cloud project ID
- Update `QDRANT_URL` and `QDRANT_API_KEY` if needed (they're already set to your current values)

**cloudbuild.yaml**:
- Update the substitution variables with your Qdrant credentials

### 4. Deploy to Cloud Run

#### Option A: Using the deployment script (Recommended)

**On Windows (PowerShell):**
```powershell
.\deploy.ps1
```

**On Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

#### Option B: Manual deployment

```bash
# Set your project
gcloud config set project your-project-id

# Enable APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com

# Deploy using Cloud Build
gcloud builds submit --config cloudbuild.yaml \
  --substitutions _QDRANT_URL="your-qdrant-url",_QDRANT_API_KEY="your-api-key"
```

#### Option C: Direct Docker deployment

```bash
# Build the image
docker build -t gcr.io/your-project-id/recommendation-api .

# Push to Container Registry
docker push gcr.io/your-project-id/recommendation-api

# Deploy to Cloud Run
gcloud run deploy recommendation-api \
  --image gcr.io/your-project-id/recommendation-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars QDRANT_URL="your-qdrant-url",QDRANT_API_KEY="your-api-key"
```

## After Deployment

1. **Get your service URL**: Cloud Run will provide a URL like `https://recommendation-api-xxxxx-uc.a.run.app`

2. **Test your API**:
   ```bash
   curl https://your-service-url/products/
   ```

3. **View API documentation**: Visit `https://your-service-url/docs`

## Environment Variables

The following environment variables are automatically set during deployment:

- `QDRANT_URL`: Your Qdrant cloud URL
- `QDRANT_API_KEY`: Your Qdrant API key
- `COLLECTION_NAME`: Collection name (defaults to "products")
- `PORT`: Port number (automatically set by Cloud Run)

## Security Notes

- The API is deployed with `--allow-unauthenticated` for easy testing
- For production, consider adding authentication
- Environment variables are securely managed by Cloud Run
- Your Qdrant credentials are not exposed in the container image

## Troubleshooting

### Common Issues:

1. **Build fails**: Check that all files are present and Dockerfile syntax is correct
2. **Service won't start**: Check logs with `gcloud run logs read --service recommendation-api`
3. **Qdrant connection fails**: Verify your credentials and network connectivity

### Viewing Logs:

```bash
gcloud run logs read --service recommendation-api --region us-central1
```

### Updating the Service:

To update your service, simply run the deployment script again or use:

```bash
gcloud run deploy recommendation-api \
  --image gcr.io/your-project-id/recommendation-api:latest \
  --region us-central1
```

## Cost Optimization

- Cloud Run charges only for actual usage
- The service will scale to zero when not in use
- Consider setting CPU and memory limits for cost control

## Next Steps

- Set up CI/CD with GitHub Actions or Cloud Build triggers
- Add authentication and authorization
- Monitor performance and set up alerting
- Consider using Cloud Run's traffic splitting for blue-green deployments
