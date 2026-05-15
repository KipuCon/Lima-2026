FROM oven/bun:1-alpine

WORKDIR /app

# Install deps first (cached layer)
COPY backend/package.json ./backend/
RUN cd backend && bun install --production

# Copy everything else
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY data/ ./data/

EXPOSE 3000

HEALTHCHECK --interval=5s --timeout=2s --retries=3 \
  CMD wget -qO- http://localhost:3000/api/stats || exit 1

CMD ["bun", "run", "backend/server.js"]
