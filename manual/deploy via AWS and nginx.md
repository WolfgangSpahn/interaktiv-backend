To run two Docker backend services on AWS, mitigated via an NGINX reverse proxy, you need to follow these steps:

### Steps Overview:
1. **Create an EC2 instance** (or use other AWS services like ECS or Fargate if needed).
2. **Install Docker** and run your backend containers.
3. **Install NGINX** and configure it as a reverse proxy to forward traffic to your Docker containers.
4. **Modify NGINX configuration** to forward traffic to the Docker services running on different ports (5000 and 5050).
5. **Ensure proper security settings** like opening the appropriate ports on AWS (for example, 80 for HTTP, and others as needed).

### Step-by-Step Guide

#### 1. **Create an EC2 Instance**

- Go to the EC2 console and launch an EC2 instance.
- Use a Linux-based AMI (e.g., Amazon Linux 2 or Ubuntu).
- Ensure you configure the security group to allow HTTP (port 80) access, and SSH access (port 22) for management.

#### 2. **Install Docker on EC2**

Once you SSH into your EC2 instance, install Docker with the following commands:

For Amazon Linux 2:
```bash
sudo yum update -y
sudo amazon-linux-extras install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user
```

For Ubuntu:
```bash
sudo apt update
sudo apt install docker.io -y
sudo systemctl start docker
sudo usermod -aG docker $USER
```

Log out and log back in for the group change to take effect.

#### 3. **Run Docker Containers**

Start your backend containers:

```bash
# Running the first backend on port 5000
docker run -d --name backend1 -p 5000:5000 your-docker-image-1

# Running the second backend on port 5050
docker run -d --name backend2 -p 5050:5050 your-docker-image-2
```

Verify they are running:
```bash
docker ps
```

#### 4. **Install NGINX**

Install NGINX on the EC2 instance:

For Amazon Linux 2:
```bash
sudo amazon-linux-extras install nginx1 -y
```

For Ubuntu:
```bash
sudo apt install nginx -y
```

Start the NGINX service:
```bash
sudo service nginx start
```

#### 5. **Configure NGINX Reverse Proxy**

Edit the NGINX configuration to forward requests to your Docker containers. Open the default configuration file:

```bash
sudo nano /etc/nginx/nginx.conf
```

Or modify a virtual host file (depending on your setup):
```bash
sudo nano /etc/nginx/conf.d/default.conf
```

Add the following configuration to proxy the requests:

```nginx
server {
    listen 80;

    # Proxy requests to backend 1 (http://your-ec2-public-ip/backend1)
    location /backend1/ {
        proxy_pass http://localhost:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Proxy requests to backend 2 (http://your-ec2-public-ip/backend2)
    location /backend2/ {
        proxy_pass http://localhost:5050/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

This configuration will forward requests:
- `/backend1/` to the container running on port `5000`
- `/backend2/` to the container running on port `5050`

#### 6. **Restart NGINX**

After saving the configuration, restart NGINX to apply changes:

```bash
sudo service nginx restart
```

#### 7. **Security Group Settings**

Ensure that the EC2 instance’s security group allows traffic on port 80 (for HTTP) and port 22 (for SSH).

1. Go to the EC2 console.
2. Select your instance, then click on the Security Group linked with your instance.
3. Edit the inbound rules to allow HTTP traffic:
   - Type: HTTP
   - Protocol: TCP
   - Port: 80
   - Source: Anywhere (0.0.0.0/0)

#### 8. **Accessing Your Backends**

Now you can access your two backends via the following URLs:
- `http://your-ec2-public-ip/backend1/` for the service running on port `5000`
- `http://your-ec2-public-ip/backend2/` for the service running on port `5050`

---

This setup allows NGINX to forward traffic from specific URLs to the corresponding Docker containers, effectively mitigating access to the backend services through a single public endpoint.