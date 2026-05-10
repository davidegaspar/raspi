FROM debian:bookworm-slim
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    nginx \
    libnginx-mod-http-dav-ext \
    apache2-utils && \
    rm -rf /var/lib/apt/lists/*
COPY nginx.conf /etc/nginx/nginx.conf
CMD ["nginx", "-g", "daemon off;"]