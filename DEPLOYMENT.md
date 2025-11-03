# Deployment Commands Cheat Sheet

## Quick Deployment
```bash
./deploy.sh
```

## Manual Commands

### 1. Configure kubectl
```bash
aws eks update-kubeconfig --region us-east-1 --name TerraReviewBot
```

### 2. Build & Push Image
```bash
docker build -t terrareviewbot .
docker tag terrareviewbot:latest 444824169367.dkr.ecr.us-east-1.amazonaws.com/devpost/terrareviewbot:latest
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 444824169367.dkr.ecr.us-east-1.amazonaws.com
docker push 444824169367.dkr.ecr.us-east-1.amazonaws.com/devpost/terrareviewbot:latest
```

### 3. Deploy to Kubernetes
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### 4. Check Status
```bash
kubectl get pods -l app=terrareviewbot
kubectl get svc terrareviewbot-service
kubectl logs -f deployment/terrareviewbot
```

### 5. Get LoadBalancer URL
```bash
kubectl get svc terrareviewbot-service -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

### 6. Clean Up
```bash
kubectl delete -f k8s/
```

## Troubleshooting

### Check Pod Status
```bash
kubectl describe pod -l app=terrareviewbot
```

### View Logs
```bash
kubectl logs -f deployment/terrareviewbot
```

### Scale Deployment
```bash
kubectl scale deployment terrareviewbot --replicas=3
```

### Update Image
```bash
# After pushing new image
kubectl rollout restart deployment/terrareviewbot
```
