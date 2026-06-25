# CloudStatus

A monitoring dashboard for tracking the status of web services and APIs.

## Features

- Real-time monitoring of HTTP/HTTPS endpoints
- Status history and analytics
- Admin interface for managing monitored services
- Dockerized deployment with PostgreSQL and Redis
- Responsive UI with dark mode support
- Basic authentication for admin access
- Configurable polling intervals

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌────────────────┐
│  Frontend   │    │  Backend     │    │    Nginx       │
│ (React/HTML)│    │ (FastAPI)    │    │ (Reverse Proxy)│
└─────────────┘    └──────────────┘    └────────────────┘
          │                   │                  │
          │                   ▼                  │
          │             ┌────────────┐          │
          │             │ PostgreSQL │          │
          │             │   (DB)     │          │
          │             └────────────┘          │
          │                   │                  │
          │                   ▼                  │
          │             ┌────────────┐          │
          └────────────►│   Redis    │◄─────────┘
                       │  (Cache)   │
                       └────────────┘
```

## Prerequisites

- Docker and Docker Compose
- Git (for cloning the repository)

## Quick Start

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd cloudstatus
   ```

2. Copy the example environment file and configure it:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Start the services:
   ```bash
   docker-compose up -d
   ```

4. Access the application:
   - Public dashboard: http://localhost
   - Admin interface: http://localhost/admin.html

5. Default admin credentials (change these in production!):
   - Username: admin
   - Password: changeme

## Configuration

Environment variables are defined in the `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| POSTGRES_USER | PostgreSQL username | cloudstatus |
| POSTGRES_PASSWORD | PostgreSQL password | changeme |
| POSTGRES_DB | PostgreSQL database name | cloudstatus_db |
| DATABASE_URL | PostgreSQL connection string | postgresql://cloudstatus:changeme@db:5432/cloudstatus_db |
| REDIS_URL | Redis connection string | redis://redis:6379/0 |
| SECRET_KEY | Secret key for JWT signing | generate-a-strong-secret-here |
| ADMIN_USERNAME | Admin username | admin |
| ADMIN_PASSWORD | Admin password | changeme |
| POLL_INTERVAL | Polling interval in seconds | 60 |

## API Endpoints

### Public Endpoints

- `GET /health` - Health check endpoint
- `GET /api/status` - Get current status of all monitored services
- `GET /api/status/{service_id}/history` - Get status history for a specific service

### Admin Endpoints (Require Basic Auth)

- `GET /api/admin/services` - List all monitored services
- `POST /api/admin/services` - Add a new service to monitor
  - Parameters: `name` (string), `url` (string)
- `DELETE /api/admin/services/{service_id}` - Remove a service

## Development

### Backend

The backend is built with FastAPI and uses PostgreSQL for data storage and Redis for caching.

To run the backend locally for development:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

The frontend is a simple HTML/CSS/JavaScript application that consumes the backend API.

No build step is required - just open the HTML files in a browser or serve them with any static file server.

## Deployment

### Docker Compose (Local/Development)

The included `docker-compose.yml` file defines all services:
- `db`: PostgreSQL database
- `redis`: Redis cache
- `backend`: FastAPI application
- `frontend`: Static HTML/CSS/JS served by Nginx
- `nginx`: Reverse proxy routing requests to appropriate services

### Production Deployment

For production deployment, consider:
1. Using managed PostgreSQL and Redis services
2. Configuring proper TLS/SSL certificates
3. Setting up resource limits and monitoring
4. Using a CDN for static assets
5. Implementing proper backup strategies

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with FastAPI, PostgreSQL, Redis, and Nginx
- Inspired by various status page solutions