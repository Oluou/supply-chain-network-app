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
