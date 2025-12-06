FROM ghcr.io/github/github-mcp-server AS git-mcp_stage

FROM python:3.11-slim
COPY --from=git-mcp_stage /server/github-mcp-server /usr/local/bin/github-mcp-server

# Set working directory
WORKDIR /app

# Set default environment variables
ENV SERVICE_PORT=8000
ENV SERVICE_HOST=0.0.0.0
ENV ENVIRONMENT=production
ENV LOG_LEVEL=INFO

# Install dependencies directly from config
RUN pip install --no-cache-dir fastapi>=0.104.0 uvicorn>=0.24.0 pydantic>=2.4.0 requests>=2.31.0 pyyaml>=6.0

# Copy source code
COPY . .

# Expose port
EXPOSE ${SERVICE_PORT}

# Run the FastAPI service directly
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "8000"]

# Additional configuration from git-mcp
RUN pip install --no-cache-dir supervisor
RUN mkdir -p /etc/supervisor/conf.d
RUN echo '[supervisord]' > /etc/supervisor/conf.d/mcp.conf
RUN echo 'nodaemon=true' >> /etc/supervisor/conf.d/mcp.conf
RUN echo '[program:mcp-server]' >> /etc/supervisor/conf.d/mcp.conf
RUN echo 'command=/usr/local/bin/github-mcp-server stdio' >> /etc/supervisor/conf.d/mcp.conf
RUN echo 'environment=GITHUB_PERSONAL_ACCESS_TOKEN="%(ENV_GITHUB_PERSONAL_ACCESS_TOKEN)s"' >> /etc/supervisor/conf.d/mcp.conf
RUN echo 'stdout_logfile=/dev/stdout' >> /etc/supervisor/conf.d/mcp.conf
RUN echo 'stderr_logfile=/dev/stderr' >> /etc/supervisor/conf.d/mcp.conf
RUN echo '[program:mcp-proxy]' >> /etc/supervisor/conf.d/mcp.conf
RUN echo 'command=uvicorn service:app --host 0.0.0.0 --port 8000' >> /etc/supervisor/conf.d/mcp.conf
RUN echo 'stdout_logfile=/dev/stdout' >> /etc/supervisor/conf.d/mcp.conf
RUN echo 'stderr_logfile=/dev/stderr' >> /etc/supervisor/conf.d/mcp.conf
CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]
