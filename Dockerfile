FROM python:3

LABEL author="Hibare (docker@hibare.in)"

# Install cron
RUN apt-get update
RUN apt-get install cron -y

# Add source directory
ADD src /app

# Install requirements in custom directory
RUN mkdir /app/python_modules
RUN pip3 install -r /app/requirements.txt --target=/app/python_modules

# Create cron entry
RUN crontab /app/crontab

# Run the command on container startup
CMD ["cron", "-f"]