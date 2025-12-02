#!/bin/bash

# Riva AI Deployment Script
# Usage: ./deploy.sh [PROJECT_ID] [REGION]

set -e

PROJECT_ID=$1
REGION=${2:-us-west2}

if [ -z "$PROJECT_ID" ]; then
    echo "Usage: ./deploy.sh [PROJECT_ID] [REGION]"
    echo "Example: ./deploy.sh riva-ai-dev us-west2"
    exit 1
fi

echo "========================================================"
echo "🚀 Deploying Riva AI to Google Cloud Project: $PROJECT_ID"
echo "🌍 Region: $REGION"
echo "========================================================"

# 1. Set Project
echo "Step 1: Setting active project..."
gcloud config set project $PROJECT_ID

# 2. Enable APIs
echo "Step 2: Enabling required Google Cloud APIs..."
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    firestore.googleapis.com \
    classroom.googleapis.com \
    calendar-json.googleapis.com \
    generativelanguage.googleapis.com

# 3. Create Artifact Registry
REPO_NAME="riva-repo"
echo "Step 3: Checking/Creating Artifact Registry ($REPO_NAME)..."
if ! gcloud artifacts repositories describe $REPO_NAME --location=$REGION &>/dev/null; then
    gcloud artifacts repositories create $REPO_NAME \
        --repository-format=docker \
        --location=$REGION \
        --description="Riva AI Docker Repository"
    echo "Created repository: $REPO_NAME"
else
    echo "Repository $REPO_NAME already exists."
fi

# 4. Configure Docker Auth
echo "Step 4: Configuring Docker authentication..."
# gcloud auth configure-docker $REGION-docker.pkg.dev --quiet
# Using explicit login for better reliability
gcloud auth print-access-token | docker login -u oauth2accesstoken --password-stdin https://$REGION-docker.pkg.dev

# 5. Build and Push Backend
echo "Step 5: Building and Pushing Backend..."
BACKEND_IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/backend:latest"
docker build -f Dockerfile.backend -t $BACKEND_IMAGE .
docker push $BACKEND_IMAGE

# 6. Build and Push Frontend
echo "Step 6: Building and Pushing Frontend..."
FRONTEND_IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/frontend:latest"
# Note: We need to pass build args for Firebase config if not using runtime env vars
# For Cloud Run, runtime env vars are preferred, but Next.js bakes NEXT_PUBLIC_ vars at build time.
# We will assume .env.local or .env exists and is used by docker build context, 
# OR we pass them from current environment.
# For simplicity in this script, we rely on the Dockerfile picking up the .env file if present,
# or the user having set them.
# Source .env file if it exists to get Firebase config
if [ -f .env ]; then
    echo "Loading .env file..."
    # Remove Windows line endings just in case
    sed -i 's/\r$//' .env
    set -a
    source .env
    set +a
fi

echo "Debug: Checking Firebase Config..."
if [ -z "$NEXT_PUBLIC_FIREBASE_API_KEY" ]; then
    echo "❌ Error: NEXT_PUBLIC_FIREBASE_API_KEY is missing!"
    exit 1
else
    echo "✅ NEXT_PUBLIC_FIREBASE_API_KEY is set (starts with ${NEXT_PUBLIC_FIREBASE_API_KEY:0:5}...)"
fi

docker build --no-cache -f riva-ui/Dockerfile \
    --build-arg NEXT_PUBLIC_FIREBASE_API_KEY="$NEXT_PUBLIC_FIREBASE_API_KEY" \
    --build-arg NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN="$NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN" \
    --build-arg NEXT_PUBLIC_FIREBASE_PROJECT_ID="$NEXT_PUBLIC_FIREBASE_PROJECT_ID" \
    --build-arg NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET="$NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET" \
    --build-arg NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID="$NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID" \
    --build-arg NEXT_PUBLIC_FIREBASE_APP_ID="$NEXT_PUBLIC_FIREBASE_APP_ID" \
    -t $FRONTEND_IMAGE ./riva-ui
docker push $FRONTEND_IMAGE

# 7. Deploy Backend
echo "Step 7: Deploying Backend Service..."
gcloud run deploy riva-backend \
    --image $BACKEND_IMAGE \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars GOOGLE_PROJECT_ID=$PROJECT_ID \
    --set-env-vars GOOGLE_API_KEY=$GOOGLE_API_KEY \
    --set-env-vars PYTHONUNBUFFERED=1

# Get Backend URL
BACKEND_URL=$(gcloud run services describe riva-backend --platform managed --region $REGION --format 'value(status.url)')
echo "✅ Backend deployed at: $BACKEND_URL"

# 8. Deploy Frontend
echo "Step 8: Deploying Frontend Service..."
gcloud run deploy riva-frontend \
    --image $FRONTEND_IMAGE \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars NEXT_PUBLIC_API_URL=$BACKEND_URL

# Get Frontend URL
FRONTEND_URL=$(gcloud run services describe riva-frontend --platform managed --region $REGION --format 'value(status.url)')
echo "✅ Frontend deployed at: $FRONTEND_URL"

echo "========================================================"
echo "🎉 Deployment Complete!"
echo "========================================================"
echo "Next Steps:"
echo "1. Go to Google Cloud Console > Cloud Run"
echo "2. Map your domain (myriva.space) to the 'riva-frontend' service."
echo "3. Update your OAuth Credentials in API & Services to allow:"
echo "   - Origin: https://myriva.space"
echo "   - Redirect: https://myriva.space/auth/callback"
echo "========================================================"
