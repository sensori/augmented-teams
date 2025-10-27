# Multi-stage build to add GitHub MCP server to mcp-proxy container
FROM ghcr.io/github/github-mcp-server AS mcp-server

# Copy GitHub MCP server binary to the main container
COPY --from=mcp-server /server/github-mcp-server /usr/local/bin/github-mcp-server

# Install supervisord to manage both services
RUN pip install --no-cache-dir supervisor

# Create supervisord config for both services
RUN mkdir -p /etc/supervisor/conf.d && \
    echo '[supervisord]' > /etc/supervisor/conf.d/mcp.conf && \
    echo 'nodaemon=true' >> /etc/supervisor/conf.d/mcp.conf && \
    echo '' >> /etc/supervisor/conf.d/mcp.conf && \
    echo '[program:mcp-server]' >> /etc/supervisor/conf.d/mcp.conf && \
    echo 'command=/usr/local/bin/github-mcp-server stdio' >> /etc/supervisor/conf.d/mcp.conf && \
    echo 'environment=GITHUB_PERSONAL_ACCESS_TOKEN="%(ENV_GITHUB_PERSONAL_ACCESS_TOKEN)s"' >> /etc/supervisor/conf.d/mcp.conf && \
    echo 'stdout_logfile=/dev/stdout' >> /etc/supervisor/conf.d/mcp.conf && \
    echo 'stderr_logfile=/dev/stderr' >> /etc/supervisor/conf.d/mcp.conf && \
    echo '' >> /etc/supervisor/conf.d/mcp.conf && \
    echo '[program:mcp-proxy]' >> /etc/supervisor/conf.d/mcp.conf && \
    echo 'command=uvicorn service:app --host 0.0.0.0 --port 8000' >> /etc/supervisor/conf.d/mcp.conf && \
    echo 'stdout_logfile=/dev/stdout' >> /etc/supervisor/conf.d/mcp.conf && \
    echo 'stderr_logfile=/dev/stderr' >> /etc/supervisor/conf.d/mcp.conf

# Use supervisord to manage both services instead of just uvicorn
CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]
