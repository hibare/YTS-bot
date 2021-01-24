FROM python:3-alpine 

LABEL Github="hibare"

ENV PATH="/opt/venv/bin:$PATH"

# Add source directory
ADD src /app

WORKDIR /app

RUN pip install -r requirements.txt

# Run the command on container startup
CMD ["python", "yts_bot.py"]