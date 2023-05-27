# StyleGAN FastAPI

Simplified Web REST API of the StyleGAN using FastAPI

## Requirements

Use the `requirements.txt` to install minimal dependencies for serving and inferencing.

```sh
pip3 install -r requirements.txt
```

Uvicorn is recommended as ASGI middleware, but other alterbatives such as Hypercorn also work.

process replication using Gunicorn and Uvicorn.

## Quick Start: Run the Default Server

This repository includes the default server configuration using Uvicorn with some trained models.
You can try out quickly as below.

```sh
git clone --recursive https://github.com/curegit/stylegan-fastapi.git
cd stylegan-fastapi
pip3 install -r requirements.txt
uvicorn main:app --reload
```

Note that it is only for trial or debugging, and not suitable for production because it is not process-replication-enabled.

## Configuration

StyleGAN FastAPI can be customized by using a configuration file.
StyleGAN FastAPI uses the TOML format for configuration, and the default TOML file is located in `default/config.toml`.

You can specify a different TOML file to use by setting the `STYLEGAN_TOML` environment variable.
`STYLEGAN_TOML` must be an absolute path or a relative path from the working directory to the TOML file.
Note that the `STYLEGAN_TOML` environment variable must be set before importing the `api` Python package.

```sh
export STYLEGAN_TOML="./custom_config.toml"
uvicorn main:app
```

### Configuration TOML Specification

standard TOML
complete raw schema definition in Python  `api/conf.py`


#### General Settings (root table)

| Key | Type | Description |
| --- | --- | --- |
| `title` | String | The title of the software. |
| `version` | String | The version number of the software. |
| `description` | String | A brief description of the software. |
| `lossy` | String | A boolean value indicating whether lossy compression is used. The default is `false`. |
| `docs` | String | A boolean value indicating whether documentation is enabled.  |
| `redoc` | String | A boolean value indicating whether ReDoc is enabled. |



models: relative path from working directory

## For production (reverse proxy layer)

- set proxy header correctly
- set max header & body size
- set timeout
