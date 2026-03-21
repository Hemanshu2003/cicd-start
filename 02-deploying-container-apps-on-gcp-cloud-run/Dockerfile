# syntax=docker/dockerfile:1
FROM node:18-alpine AS base
WORKDIR /app

# Install only prod deps
COPY package*.json ./
RUN npm ci --only=production

# Copy source
COPY . .

# Cloud Run expects the service on $PORT (default 8080)
ENV PORT=8080
EXPOSE 8080

CMD ["npm", "start"]
