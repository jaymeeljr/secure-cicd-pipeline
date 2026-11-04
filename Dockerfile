# ---- build stage: install dependencies in isolation ----
FROM python:3.13-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- runtime stage: minimal image, no build tools ----
FROM python:3.13-slim

# Dedicated unprivileged user with a fixed UID (matches runAsUser in k8s).
# pip/setuptools are not needed at runtime and carry their own vendored CVEs
# (flagged by Trivy), so they are removed from the final image.
RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app
RUN python -m pip uninstall -y pip setuptools wheel || python -m pip uninstall -y pip
RUN rm -rf /usr/local/lib/python3.13/site-packages/setuptools* /usr/local/lib/python3.13/ensurepip

WORKDIR /srv
COPY --from=builder /install /usr/local
COPY --chown=app:app app/ ./app/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

USER 10001
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/health').status==200 else 1)"

# gunicorn: production WSGI server instead of Flask's dev server.
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--worker-tmp-dir", "/tmp", "app.main:app"]
