# ============================================================
# Frontend Dockerfile — The Lenny Growth Assistant
# ============================================================

FROM node:20-slim

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy application source
COPY . .

# Expose the Vite dev server port
EXPOSE 5173

# Run the dev server (host 0.0.0.0 for Docker access)
CMD ["npm", "run", "dev"]
