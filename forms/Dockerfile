# Use an official Python runtime as a parent image
FROM python:3.12.1-slim-bookworm


# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# # Install system dependencies
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y gcc default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/

RUN pip install --upgrade pip \
    && pip install mysqlclient \
    &&  pip install gunicorn \
    && pip install -r requirements.txt

# Copy the Django project code into the container
COPY . /app/

# Collect static files (customize this as per your project)
# RUN python manage.py collectstatic --noinput
ENV FORMS_PORT 8012
# Expose the port that Gunicorn will listen on
RUN ls
# Run Gunicorn
CMD gunicorn --bind 0.0.0.0:$FORMS_PORT forms.wsgi:application
