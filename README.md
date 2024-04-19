# StyleGAN FastAPI

Simplified Web REST API of the StyleGAN using FastAPI

This is a web backend application to make the generator models trained by [Precure StyleGAN ADA](https://github.com/curegit/precure-stylegan-ada) available on the web in a simplified manner.
An example implementation of the front-end client is [StyleGAN Vue](https://github.com/curegit/stylegan-vue) and is [deployed here]() for immediate trial.

## Requirements

To run this application, you need a Unix-like system with Python >= 3.12 installed.
[Precure StyleGAN ADA](https://github.com/curegit/precure-stylegan-ada)'s dependencies.

Use the `requirements.txt` to install minimal dependencies for serving and inferencing.

```sh
pip3 install -r requirements.txt
```

While Uvicorn is recommended as ASGI middleware, other alternatives such as Hypercorn also work.

In a product environment, a typical example is process replication using a combination of Gunicorn and Uvicorn.

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

## API

See the

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
complete raw schema definition in Python `api/conf.py`

All properties are optional except model files
You must specify at least one model.

#### General Settings (root table)

| Key           | Type    | Description                                                                           |
| ------------- | ------- | ------------------------------------------------------------------------------------- |
| `title`       | string  | The title of the software.                                                            |
| `version`     | string  | The version number of the software.                                                   |
| `description` | string  | A brief description of the software.                                                  |
| `lossy`       | boolean | A boolean value indicating whether lossy compression is used. The default is `false`. |
| `docs`        | boolean | A boolean value indicating whether documentation is enabled.                          |
| `redoc`       | boolean | A boolean value indicating whether ReDoc is enabled.                                  |

#### Server Settings

| Key       | Type                                 | Description                                        |
| --------- | ------------------------------------ | -------------------------------------------------- |
| `gpu`     | boolean or integer                   | A boolean value indicating whether GPU is enabled. |
| `logger`  | The name of the logger used.         |
| `tmp_dir` | The path to the temporary directory. |

#### HTTP Settings

| HTTP Settings | Description                                                    |
| ------------- | -------------------------------------------------------------- |
| `forwarded`   | A boolean value indicating whether HTTP forwarding is enabled. |

#### CORS Settings

| CORS Settings | Description                                         |
| ------------- | --------------------------------------------------- |
| `enabled`     | A boolean value indicating whether CORS is enabled. |
| `origins`     | A list of allowed origins.                          |

### Limit Settings

| Limit Settings | Description                                |
| -------------- | ------------------------------------------ |
| `min_delay`    | The minimum delay time.                    |
| `block`        | A block of settings for blocking requests. |
| `concurrency`  | A block of settings for concurrency.       |
| `rate`         | A block of settings for rate limiting.     |

## Model Settings

| Model Settings | Description                                                               |
| -------------- | ------------------------------------------------------------------------- |
| `file`         | models: relative path from working directory. The path to the model file. |
| `relative`     | A boolean value indicating whether the path is relative.                  |
| `name`         | The name of the model.                                                    |
| `description`  | A brief description of the model.                                         |
| `lossy`        | A boolean value indicating whether lossy compression is used.             |
| `gpu`          | A boolean value indicating whether GPU is enabled.                        |

## For production (reverse proxy layer)

- set proxy header correctly

`RuntimeDirectory`

```ini
[Unit]
Description=Gunicorn StyleGAN Daemon
Requires=stylegan.socket
After=network.target

[Service]
Type=notify
User=hanon
Group=hanon
WorkingDirectory=/home/hanon/stylegan
ExecStart=/usr/local/bin/python3.11 -B -m gunicorn -c gunicorn.config.py
RuntimeDirectory=stylegan
PrivateTmp=true
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=30
Restart=always

[Install]
WantedBy=multi-user.target
```

```ini
[Unit]
Description=Gunicorn StyleGAN Socket

[Socket]
ListenStream=/run/stylegan.sock
SocketUser=www-data
SocketMode=600

[Install]
WantedBy=sockets.target
```

change

```

```

It is also recommeded to set limit header and body size
