
# Gsky Manager

An experimental wagtail based CMS and layer manager for [GSKY Server](https://github.com/icpac-igad/gsky)

## Dependencies

Execution using Docker requires:
- [Docker](https://www.docker.com/)


## Installation

Start by cloning the repository from github to your execution environment

`git clone https://github.com/icpac-igad/gsky-manager`

`cd gsky-manager`

Follow the steps below:

1. Create and update your `.env`. You can find an example `.env.sample` file in the project root.The variables are described in detail in [this section](#environment-variables) of the documentation

    `cp .env.sample .env`

2. Build the image

    `docker build -t gsky_manager .`

3. Run the service

`docker run --env-file ./.env -p 8000:8000 gsky_manager gunicorn gskymanager.wsgi:application --bind 0.0.0.0:8000`


## Environment Variables
- DEBUG => on or off. Django DEBUG setting
- CURRENT_UID => host user id to use to run the app
- ALLOWED_HOSTS => Django allowed hosts
- FORCE_SCRIPT_NAME => base path to force django to resolve to. see details [here](https://docs.djangoproject.com/en/3.2/ref/settings/#force-script-name)
- SECRET_KEY => Django secret key
- DATABASE_URL => postgres connection URI for your database, `postgres://<user>:<pass>@<ip>:<port>/<db>`
- HOST_DATA_ROOT_PATH => absolute host path to where the base directory for gsky data is located
- CONTAINER_DATA_ROOT_PATH => absolute container path where the gskydata volume is mapped
- GSKY_CONFIG_FILE => absolute host path to gsky config.json file
- GSKY_OWS_HOST_NAME => IP address of domain name to the gsky ows services, without the protocol
- GSKY_OWS_PROTOCOL => protocol http or https
- GSKY_MAS_ADDRESS => gsky mas address
- GSKY_WORKER_NODES => a list gsky grpc worker nodes. Comma separated.
- GSKY_INGEST_SCRIPT => absolute host path to the gsky ingest.sh file
- GSKY_WPS_TEMPLATES_HOST_PATH => host absolute path to templates directory
- GSKY_WPS_TEMPLATES_CONTAINER_PATH => container absolute path to templates directory
- GSKY_RULESETS_HOST_PATH => host absolute path to gsky rulesets directory
- GSKY_RULESETS_CONTAINER_PATH => container absolute path to gsky rulesets directory
- OWS_BASE_URL => Gsky OWS base URL

## Production Deployment 
This service is meant to be deployed together with other gsky related services as 
described [here](https://github.com/icpac-igad/eahw-gsky) using docker compose.

    