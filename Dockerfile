FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY myapp/requirements.txt /app/
RUN pip install -r requirements.txt
COPY myapp /app/