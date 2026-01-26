# Supply Chain Network Frontend

This folder is a placeholder for the React application from GitHub Spark.

## Setup Instructions

1. Generate your React app using GitHub Spark or create-react-app:
   ```bash
   npx create-react-app .
   ```

2. Install necessary dependencies:
   ```bash
   npm install axios react-router-dom
   ```

3. Configure the API endpoint to connect to the backend at `http://backend:8000`

## Docker

The Dockerfile is configured to:
- Build the React application
- Serve it using nginx
- Expose port 80

## Development

Run locally:
```bash
npm start
```

Build for production:
```bash
npm run build
```

## Tech Stack

This frontend is designed for a modern React application. The recommended stack includes:

- **React** (via create-react-app or GitHub Spark)
- **Axios** for API requests
- **React Router DOM** for routing
- **Nginx** for production serving (via Docker)

You may also consider:
- **Material-UI** or **Ant Design** for UI components
- **Redux Toolkit** for state management (optional)
- **Jest** and **React Testing Library** for testing

## Integration Notes
- The backend API is available at `http://backend:8000` (Docker Compose) or `http://localhost:8000` (local dev)
- Update your `.env` or config files to point API requests to the backend

## Reproducibility & Onboarding

For full documentation of backend analytics, API endpoints, and data flows, see:
- `../backend/app/README.md` (backend setup, endpoints, and architecture)
- `../docs/apis.md` (API documentation, analytics engine, and data model mapping)

### Onboarding Steps
1. Clone the repository and review the backend and frontend README files.
2. Set up environment variables as described in `.env.example` (backend) and configure API endpoints for the frontend.
3. Use Docker Compose for a reproducible environment, or run backend/frontend locally as described above.
4. See API docs at `http://localhost:8000/docs` for interactive testing.
