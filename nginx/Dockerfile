FROM nginx:1.25-alpine
RUN apk add --no-cache curl
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY frontend/index.html /usr/share/nginx/html/index.html
COPY frontend/admin.html /usr/share/nginx/html/admin.html
COPY frontend/login.html /usr/share/nginx/html/login.html
