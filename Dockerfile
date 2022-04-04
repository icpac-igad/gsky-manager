###########
# BUILDER #
###########

# Use an official Python runtime based on Debian 10 "buster" as a parent image.
FROM python:3.8.1-slim-buster as builder

# Use /app folder as a directory where the source code is stored.
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system packages required by Wagtail and Django.
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libmariadbclient-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
    netcat \
 && rm -rf /var/lib/apt/lists/*

# Install the project requirements.
COPY requirements.txt /usr/src/app
RUN pip wheel --no-deps --wheel-dir /usr/src/app/wheels -r ./requirements.txt
# Install gunicorn
RUN pip wheel --no-deps --wheel-dir /usr/src/app/wheels gunicorn

# Copy the source code of the project into the container.
COPY . .

#########
# FINAL #
#########
# Use an official Python runtime based on Debian 10 "buster" as a parent image.
FROM python:3.8.1-slim-buster


# install dependencies
RUN apt-get update && apt-get install --yes --quiet --no-install-recommends netcat
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

# create directory for the app user
RUN mkdir -p /home/app

# create the app user
RUN useradd app

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME

WORKDIR $APP_HOME

RUN touch app.log && chown app:app app.log

# copy entrypoint.sh
COPY ./entrypoint.sh $APP_HOME

COPY --chown=app:app . $APP_HOME

RUN usermod -u 1000 app

RUN mkdir -p /home/app/web/static && chown -R app:app /home/app/web/static
RUN mkdir -p /home/app/web/media && chown -R app:app /home/app/web/media

# change to the app user
USER app

# run entrypoint.sh
ENTRYPOINT ["/home/app/web/entrypoint.sh"]
