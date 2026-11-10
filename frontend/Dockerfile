# Production Dockerfile for CrystaGraph Next.js 14 Frontend
FROM node:20-alpine

WORKDIR /app

ENV NODE_ENV=production \
    PORT=3000 \
    NEXT_PUBLIC_API_URL=http://localhost:8000

# Install dependencies
COPY package*.json ./
RUN npm install --legacy-peer-deps

# Copy application code
COPY . .

# Build production Next.js bundle
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
