FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN useradd --create-home --uid 1000 app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY inbox/ inbox/
COPY bus/ bus/

RUN mkdir -p checkpoints/leads \
    && chown -R app:app /app

USER app

ENTRYPOINT ["python", "-m", "src.pipeline"]
CMD ["--list"]
