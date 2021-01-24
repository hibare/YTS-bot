FROM python:3-alpine

LABEL author="Hibare (docker@hibare.in)"

# Add source directory
ADD src /app

# Install requirements in custom directory
RUN mkdir /app/python_modules
RUN pip3 install -r /app/requirements.txt --target=/app/python_modules

WORKDIR /app

# Run the command on container startup
CMD ["python", "yts.py"]