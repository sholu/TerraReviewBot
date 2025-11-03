#!/bin/bash

# TerraReviewBot EKS Deployment Script - Budget Version
set -e

# Configuration
CLUSTER_NAME="TerraReviewBot"
REGION="us-east-1"
ECR_REPO="444824169367.dkr.ecr.us-east-1.amazonaws.com/devpost/terrareviewbot"

echo "🚀 Starting TerraReviewBot EKS Deployment..."

# Step 1: Configure kubectl for your cluster
echo "⚙️ Configuring kubectl..."
aws eks update-kubeconfig --region $REGION --name $CLUSTER_NAME

# Step 2: Build and push Docker image
echo "📦 Building Docker image..."
docker build -t terrareviewbot .

# Tag for ECR
docker tag terrareviewbot:latest $ECR_REPO:latest

# Login to ECR
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_REPO

# Push to ECR
echo "📤 Pushing image to ECR..."
docker push $ECR_REPO:latest

# Step 3: Apply Kubernetes manifests
echo "☸️ Deploying to EKS..."
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Step 4: Wait for deployment
echo "⏳ Waiting for deployment to be ready..."
kubectl rollout status deployment/terrareviewbot --timeout=300s

# Step 5: Wait for LoadBalancer to get external IP
echo "⏳ Waiting for LoadBalancer to be ready..."
echo "This might take 2-3 minutes..."

# Check LoadBalancer status
for i in {1..20}; do
    EXTERNAL_IP=$(kubectl get svc terrareviewbot-service -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
    if [[ -n "$EXTERNAL_IP" ]]; then
        break
    fi
    echo "Waiting for LoadBalancer... ($i/20)"
    sleep 15
done

# Step 6: Display results
echo ""
echo "✅ TerraReviewBot deployment complete!"
echo ""
echo "📊 Deployment Status:"
kubectl get pods -l app=terrareviewbot
echo ""
kubectl get svc terrareviewbot-service
echo ""

if [[ -n "$EXTERNAL_IP" ]]; then
    echo "🌐 Your app is accessible at: http://$EXTERNAL_IP"
    echo "🔗 Direct link: http://$EXTERNAL_IP"
else
    # Check if service is NodePort
    SERVICE_TYPE=$(kubectl get svc terrareviewbot-service -o jsonpath='{.spec.type}')
    if [[ "$SERVICE_TYPE" == "NodePort" ]]; then
        echo "🌐 NodePort service is ready!"
        echo "📱 Access via port-forward (recommended): kubectl port-forward svc/terrareviewbot-service 8080:80"
        echo "🌍 Then open: http://localhost:8080"
        echo ""
        echo "🔗 Node IPs (if security groups allow):"
        kubectl get nodes -o jsonpath='{range .items[*]}{.status.addresses[?(@.type=="ExternalIP")].address}{":31229"}{"\n"}{end}' | sed 's/^/   http:\/\//'
    else
        echo "⏳ LoadBalancer is still provisioning. Check status with:"
        echo "kubectl get svc terrareviewbot-service"
    fi
fi

echo ""
echo "💡 Quick access: kubectl port-forward svc/terrareviewbot-service 8080:80"
echo "💡 To check logs: kubectl logs -f deployment/terrareviewbot"
echo "💡 To delete deployment: kubectl delete -f k8s/"
