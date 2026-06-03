# ==================== СТАДИЯ 1: builder ====================
FROM python:3.14-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
RUN uv pip install --no-cache -r pyproject.toml

# ==================== СТАДИЯ 2: final ====================
FROM python:3.14-slim-bookworm AS final

# Устанавливаем необходимые системные библиотеки
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl libexpat1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN addgroup --system app && \
    adduser --system --no-create-home --ingroup app app

COPY --from=builder --chown=app:app /opt/venv /opt/venv

COPY --chown=app:app . /app

WORKDIR /app

USER app

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
