FROM python:3-alpine

LABEL author="Hibare (docker@hibare.in)"

# Add source directory
ADD src /app

# Install requirements 
RUN pip3 install -r /app/requirements.txt

WORKDIR /app

# Run the command on container startup
CMD ["python", "yts_bot.py"]