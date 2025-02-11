FROM python:3.11.11-slim
LABEL maintainer="zaharsavchen@gmail.com"

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt --no-cache-dir \
    mkdir -p /vol/web/media && \
    mkdir /vol/web/static && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user && \
    chown -R django-user /vol/web/media /vol/web/static && \
    chmod -R 755 /vol/web/media /vol/web/static

USER django-user
