#!/bin/bash

# Resume-Boost AI Deployment Script
# This script automates the deployment of the backend infrastructure

set -e

echo "🚀 Starting Resume-Boost AI Backend Deployment..."

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo "❌ AWS SAM CLI is not installed. Please install it first."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Build the SAM application
echo "🔨 Building SAM application..."
sam build --use-container

if [ $? -eq 0 ]; then
    echo "✅ Build completed successfully"
else
    echo "❌ Build failed"
    exit 1
fi

# Check if this is the first deployment
if [ ! -f "samconfig.toml" ]; then
    echo "🆕 First time deployment detected. Running guided deployment..."
    sam deploy --guided
else
    echo "🔄 Running deployment with existing configuration..."
    sam deploy
fi

if [ $? -eq 0 ]; then
    echo "✅ Deployment completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Copy the API Gateway URL from the deployment output"
    echo "2. Update the API_GATEWAY_URL in src/App.jsx"
    echo "3. Build and deploy the frontend: npm run build"
    echo ""
    echo "🎉 Your Resume-Boost AI backend is now live!"
else
    echo "❌ Deployment failed"
    exit 1
fi 