# INET 4031 Lab 12: Docker Compose Ticket System

## Overview

This lab deployed a three-tier IT ticket dashboard using Docker and Docker Compose. The application includes an Apache web frontend, a Flask API backend, and a MariaDB database. Apache acts as the public-facing reverse proxy, Flask handles the application logic, and MariaDB stores the ticket data.

## Application Components

- **Apache**: Exposes the site on port 80 and forwards API requests to Flask.
- **Flask**: Provides health checks and ticket API endpoints.
- **MariaDB**: Stores ticket records and seed data.
- **Docker Compose**: Builds, networks, and starts all three services together.

## Setup and Deployment

Create the environment file:

```bash
cp .env.example .env
```
Start the application:
```bash
docker compose up --build
```
Check container status:
```bash
docker compose ps
```
The database and app containers should show as healthy. The web container should show as running.

## Accessing the Dashboard
Open the dashboard in a browser:
```bash
http://<VM-IP>:80
```
The page should show the Ticket System dashboard, a green API health indicator, and ticket records from the database.

## Testing the Application
Check the frontend:
```bash
curl http://localhost:80/
```
Check the health endpoint:
```bash
curl http://localhost:80/health
```
Expected output:
```JSON
{"database": "connected","status": "healthy"}
```
Check tickets:
```bash
curl http://localhost:80/api/tickets
```
Create a ticket:
```bash
curl -X POST http://localhost:80/api/tickets \
  -H "Content-Type: application/json" \
  -d '{"title": "My first ticket", "description": "Testing the API"}'
```
## Persistence Test
The database uses a named Docker volume, so ticket data should persist after restarting the database container:
```bash
docker compose stop db
docker compose start db
curl http://localhost:80/api/tickets
```
## Common Fixes
If port 80 is already in use, stop Apache on the host VM:
```bash
sudo systemctl stop apache2
```
If MariaDB initialization fails or the database schema is missing, reset the database volume:
```bash
docker compose down -v
docker compose up --build
```
## Check Script
Run the final check script:
```bash
chmod +x check-lab.sh
./check-lab.sh
```
All checks should pass before submission.

## Reflection
This lab showed how Docker Compose can run a multi-container application with separate services for the frontend, backend, and database. It also showed the importance of health checks, service dependencies, environment variables, internal DNS, and persistent storage.


# INET 4031 Lab 13: Kubernetes Deployment with k3s

## Overview

This lab moved the completed Lab 12 ticket dashboard from Docker Compose into Kubernetes using k3s. The application still uses Apache, Flask, and MariaDB, but Kubernetes now manages the containers through Deployments, Services, a PersistentVolumeClaim, a ConfigMap, and a Secret.

The main goal was to understand how Kubernetes maintains desired state and provides self-healing when a pod fails or is deleted.

## What Changed from Lab 12

In Lab 12, Docker Compose started and connected the three services on a single VM. In Lab 13, the application runs inside a Kubernetes cluster. Kubernetes now controls the running pods, internal networking, persistent database storage, and service exposure.

Key changes:

- Docker Compose was replaced by Kubernetes manifests.
- Flask and Apache images were pushed to Docker Hub.
- Database credentials were moved from `.env` into a Kubernetes Secret.
- MariaDB uses a PersistentVolumeClaim for storage.
- Apache is exposed through a NodePort Service on port 30080.
- Kubernetes automatically recreates pods when they are deleted.

## Application Components

- **MariaDB Deployment**: Runs the database container.
- **MariaDB Service**: Provides the internal hostname `db`.
- **PersistentVolumeClaim**: Stores database data across pod restarts.
- **Flask Deployment**: Runs the application API.
- **Flask Service**: Makes Flask reachable inside the cluster.
- **Apache Deployment**: Runs the public-facing web server.
- **Apache NodePort Service**: Exposes the dashboard externally on port 30080.
- **Secret**: Stores database credentials.
- **ConfigMap**: Provides database initialization SQL.

## Build and Push Images

Build the Flask and Apache images:
```bash
docker build -t <dockerhub-username>/flask-app:latest ./app
docker build -t <dockerhub-username>/apache-web:latest ./apache
```
Log in to Docker Hub:
```bash
docker login
```
Push the images:
```bash
docker push <dockerhub-username>/flask-app:latest
docker push <dockerhub-username>/apache-web:latest
```
## Kubernetes Setup
Create the namespace:
```bash
kubectl create namespace ticket-app
```
Create the Secret:
```bash
bash create-secret.sh
```
Verify the Secret:
```bash
kubectl get secret db-credentials -n ticket-app
kubectl describe secret db-credentials -n ticket-app
```
## Deploy the Application
Apply all Kubernetes manifests:
```bash
kubectl apply -f k8s/
```
Check pods:
```bash
kubectl get pods -n ticket-app
```
Check services:
```bash
kubectl get services -n ticket-app
```
Check persistent storage:
```bash
kubectl get pvc -n ticket-app
```
The pods should show as running, and the PVC should show as bound.

## Accessing the Dashboard
Open the dashboard in a browser:
```bash
http://<VM-IP>:30080
```
The dashboard should show the Ticket System page with a green API health indicator.

## Testing the Application
Check the health endpoint:
```bash
curl http://localhost:30080/health
```
Expected output:
```JSON
{"database": "connected", "status": "healthy"}
```
Check the tickets API:
```bash
curl http://localhost:30080/api/tickets
```
## Self-Healing Test
Get the pod names:
```bash
kubectl get pods -n ticket-app
```
Delete the Flask app pod:
```bash
kubectl delete pod <app-pod-name> -n ticket-app
```
Watch Kubernetes recreate it:
```bash
kubectl get pods -n ticket-app -w
```
When the pod is deleted, Kubernetes detects that the actual state no longer matches the desired state defined by the Deployment. The Deployment controller uses the ReplicaSet to create a replacement pod automatically. This demonstrates Kubernetes self-healing.

Check Script
Run the Lab 13 check script:
```bash
chmod +x check-lab13.sh
./check-lab13.sh
```
All checks should pass before submission.

## Reflection

This lab showed the difference between running containers and orchestrating containers. Docker Compose is simpler and lighter, but Kubernetes adds stronger reliability, self-healing, service discovery, and deployment control. The most important concept was desired state: Kubernetes continuously works to keep the running application matched to the configuration defined in the YAML manifests.
