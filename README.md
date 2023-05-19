# StyleGAN FastAPI

Simplified Web REST API of the StyleGAN using FastAPI

## Requirements

Use the `requirements.txt` to install minimal dependencies for serving and inferencing.

```sh
pip3 install -r requirements.txt
```

Uvicorn is recommended as ASGI middleware, but other alterbatives such as Hypercorn also work.

process replication using Gunicorn and Uvicorn.

## Run the default server

This repository includes the default server configuration with some trained models.
You can try

```sh
cd
uvicorn
```

Note that it is for trial or debugging, and



## Configuration

```
STYLEGAN_TOML="./custom_config.toml"
```



`STYLEGAN_TOML` can be absolute or relative from the working directory.

### Configuration file spec

models: relative path from working directory

## For production (reverse proxy layer)

- set proxy header correctly
- set max header & body size
- set timeout
