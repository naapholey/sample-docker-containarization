# Flask Docker Demo Application

A simple Flask web application demonstrating Docker containerization for educational purposes.

## Features

- Displays welcome message: "Hello Class, welcome to Docker class, how is it going?"
- Shows container information (hostname, IP, Python version, timestamp)
- Health check endpoint for monitoring
- JSON API endpoint for container details
- Beautiful responsive UI
- Production-ready Dockerfile with security best practices

## Project Structure
```
flask-docker-demo/
├── app.py              # Flask application
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker build instructions
├── .dockerignore      # Files to exclude from Docker build
└── README.md          # This file
```

## Prerequisites

- Docker installed on your system
- Basic knowledge of command line

## Quick Start- Run App Locally

### Local Development (without Docker)

For local development , python must be installed on your system 

```bash
# Create virtual environment
python -m venv venv
python3 -m venv venv #for when using python3

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
pyhton3 app.py #when using python3

# or run using 
flask run

# Access at http://localhost:5000
```
![alt text](<Screenshot 2026-01-30 at 3.39.36 AM.png>)

## RUN APP AS CONTAINER
###  Build the Docker Image
```bash
# Navigate to project directory
cd flask-docker-demo

# Build the image with tag 'docker-container-demo'
docker build -t docker-container-demo .

# Verify image was created
docker images | grep docker-container-demo
```
![alt text](<Screenshot 2026-01-30 at 4.02.40 AM.png>)

### 2. Run the Container
```bash
# Run container in detached mode, mapping port 5000
docker run -d -p 5000:5000 --name demo-container docker-container-demo

# Verify container is running
docker ps
```
![alt text](<Screenshot 2026-01-30 at 4.06.19 AM.png>)

### 3. Access the Application

Open your browser and visit:
- **Main Page**: http://localhost:5000
- **Health Check**: http://localhost:5000/health
- **Info Endpoint**: http://localhost:5000/info

### 4. View Container Logs
```bash
# View logs
docker logs demo-container

# Follow logs in real-time
docker logs -f demo-container
```
![alt text](<Screenshot 2026-01-30 at 4.33.41 AM.png>)

### 5. Stop and Remove Container
```bash
# Stop the container
docker stop demo-container

# Remove the container
docker rm demo-container
```

## Advanced Usage

### Run with Custom Port
```bash
docker run -d -p 8080:5000 --name demo-container docker-container-demo
# Access at http://localhost:8080
```
![alt text](<Screenshot 2026-01-30 at 4.07.03 AM.png>)

### Run with Environment Variables
```bash
docker run -d \
  -p 5000:5000 \
  -e APP_ENV=staging \
  -e PORT=5000 \
  --name demo-container \
  docker-container-demo
```
![alt text](<Screenshot 2026-01-30 at 4.37.05 AM.png>)

### Interactive Mode (for debugging)
```bash
# Run container with interactive terminal
docker run -it -p 5000:5000 docker-container-demo

# Execute commands inside running container
docker exec -it demo-container bash
```
![alt text](<Screenshot 2026-01-30 at 4.42.36 AM.png>)

### Using Gunicorn (Production)

Edit Dockerfile and uncomment the gunicorn CMD line:
```dockerfile
# Replace this line:
# CMD ["python", "app.py"]

# With this line:
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

Then rebuild:
```bash
docker build -t docker-container-demo:prod .
docker run -d -p 5000:5000 --name demo-container docker-container-demo:prod
```
![alt text](<Screenshot 2026-01-30 at 4.53.46 AM.png>)


### Rebuild After Code Changes
```bash
# Stop and remove old container
docker stop demo-container
docker rm demo-container

# Rebuild image
docker build -t docker-container-demo .

# Run new container
docker run -d -p 5000:5000 --name demo-container docker-container-demo
```

## Docker Commands Reference
```bash
# List all containers (including stopped)
docker ps -a

# List all images
docker images

# Remove image
docker rmi docker-container-demo

# View container resource usage
docker stats demo-container

# Inspect container details
docker inspect demo-container

# Execute command in running container
docker exec demo-container python -c "print('Hello from inside container!')"
```

## Troubleshooting

### Container won't start
```bash
# Check logs for errors
docker logs demo-container

# Check if port is already in use
# On Linux/Mac:
lsof -i :5000
# On Windows:
netstat -ano | findstr :5000
```
![alt text](<Screenshot 2026-01-30 at 5.07.54 AM.png>)
### Cannot access application
- Ensure container is running: `docker ps`
- Check port mapping is correct: `docker port demo-container`
- Verify firewall settings

### Permission denied errors
- Ensure Docker daemon is running
- On Linux, add user to docker group: `sudo usermod -aG docker $USER`

## Security Best Practices Implemented

1. ✅ Using official Python slim image (smaller attack surface)
2. ✅ Running as non-root user
3. ✅ No unnecessary packages installed
4. ✅ .dockerignore to prevent secret leakage
5. ✅ Health checks for monitoring
6. ✅ Minimal layer count for efficiency
7. ✅ Environment variables for configuration
