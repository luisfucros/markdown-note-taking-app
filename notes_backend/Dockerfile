FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8001

RUN pip install --upgrade pip

RUN apt-get update && \
    apt-get install -y python3-dev build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Install auth lib
COPY wheels/ /tmp/py-wheels
RUN cd /tmp/py-wheels && ls . | grep \.whl | xargs pip install --no-cache-dir

COPY src/ ./

EXPOSE $PORT

CMD sleep 10 && alembic upgrade head && uvicorn app:app --host 0.0.0.0 --port 8001
