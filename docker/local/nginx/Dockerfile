# Use the official nginx image with Alpine Linux for a smaller footprint
FROM docker.io/nginx:1.27.0-alpine3.19-slim

# Remove the default nginx configuration file
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom nginx configuration
# This will be used instead of the default configuration
COPY ./nginx.conf /etc/nginx/conf.d/default.conf