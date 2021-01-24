# Build

FROM python:3-alpine as build

RUN apk add libxml2-dev libxslt-dev gcc libc-dev

RUN python3 -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY src/requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

# Release

FROM python:3-alpine as release

LABEL Github="hibare"

COPY --from=build /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

# Add source directory
ADD src /app

# Install requirements 
RUN pip3 install -r /app/requirements.txt

WORKDIR /app

# Run the command on container startup
CMD ["python", "yts_bot.py"]