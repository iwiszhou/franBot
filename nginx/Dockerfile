FROM nginx:latest

COPY nginx-selfsigned.crt /etc/ssl/certs/nginx-selfsigned.crt
COPY nginx-selfsigned.key /etc/ssl/private/nginx-selfsigned.key
COPY index.html /etc/nginx/html/index.html

COPY nginx.conf /etc/nginx/nginx.conf
