# Use an official Python image as the base image
FROM python:3.9-alpine

# Set the working directory to /app
WORKDIR /app

# Copy everything into the container
# except for items specified in .dockerignore
COPY . .

# Install the required packages
RUN apk add --no-cache build-base libxml2-dev libxslt-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt

# Add the Scrapy executable to the PATH
ENV PATH=$PATH:/usr/local/bin/scrapy


# Listening to nothing, this way the container will stay up forever
# and we can start the crawler many times without having to restart the container
ENTRYPOINT ["tail", "-f", "/dev/null"]