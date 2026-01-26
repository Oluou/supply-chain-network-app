# For now, serve the placeholder HTML
# When you add a React app, uncomment the multi-stage build below

FROM nginx:alpine

# Copy placeholder HTML
COPY index.html /usr/share/nginx/html/

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

# Uncomment below when you have a React app:
# FROM node:18-alpine as build
# WORKDIR /app
# COPY package*.json ./
# RUN npm install
# COPY . .
# RUN npm run build
# 
# FROM nginx:alpine
# COPY --from=build /app/build /usr/share/nginx/html
# COPY nginx.conf /etc/nginx/conf.d/default.conf
# EXPOSE 80
# CMD ["nginx", "-g", "daemon off;"]

# Security Best Practices
# 1. Do not hardcode secrets in Dockerfiles. Use environment variables or secret managers.
# 2. Avoid exposing sensitive ports to the public internet.
# 3. Use minimal base images and keep dependencies up to date.
# 4. Remove build tools and caches after installation to reduce image size and attack surface.
# 5. Set proper file permissions for application code and config files.
# 6. Use multi-stage builds for frontend to avoid leaking source code in production images.
