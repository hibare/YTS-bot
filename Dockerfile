FROM python:3.11.0rc2-slim as base

LABEL Github="hibare"

FROM base as builder

RUN apt-get update && apt-get install -y build-essential python3-dev libpq-dev libssl-dev libffi-dev rustc

COPY src/requirements.txt .

RUN pip install -r requirements.txt

FROM base

COPY --from=builder /usr/local/bin/ /usr/local/bin/

COPY --from=builder /usr/local/lib/ /usr/local/lib/

# Add source directory
ADD src /app

WORKDIR /app

# Run the command on container startup
CMD ["python", "yts_bot.py"]