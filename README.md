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

| Key           | Type                             | Description                                                                           |
| ------------- | -------------------------------- | ------------------------------------------------------------------------------------- |
| `title`       | string                           | The title of the software.                                                            |
| `version`     | string                           | The version number of the software.                                                   |
| `description` | string                           | A brief description of the software.                                                  |
| `lossy`       | boolean                          | A boolean value indicating whether lossy compression is used. The default is `false`. |
| `docs`        | boolean                          | A boolean value indicating whether documentation is enabled.                          |
| `redoc`       | boolean                          | A boolean value indicating whether ReDoc is enabled.                                  |
| `server`      | [ServerConfig]()                 | dd                                                                                    |
| `models`      | {[key: string]: [ModelConfig]()} | d                                                                                     |

#### Server Settings

| Key       | Type               | Description                                        |
| --------- | ------------------ | -------------------------------------------------- |
| `gpu`     | boolean or integer | A boolean value indicating whether GPU is enabled. |
| `logger`  | string             | The name of the logger used.                       |
| `tmp_dir` | string             | The path to the temporary directory.               |
| `http`    | HTTPConfig         | The path to the temporary directory.               |
| `limit`   | LimitConfig        | The path to the temporary directory.               |

#### HTTP Settings

| HTTP Settings       | Type           | Description                                                    |
| ------------------- | -------------- | -------------------------------------------------------------- |
| `forwarded`         | boolean        | A boolean value indicating whether HTTP forwarding is enabled. |
| `forwarded_headers` | string[]       |                                                                |
| `cors`              | [CORSConfig]() | A boolean value indicating whether HTTP forwarding is enabled. |

#### CORS Settings

| `CORSConfig` | Type     | Description                                         |
| ------------ | -------- | --------------------------------------------------- |
| `enabled`    | boolean  | A boolean value indicating whether CORS is enabled. |
| `origins`    | string[] | A list of allowed origins.                          |

### Limit Settings

| Limit Settings | Type                   | Description                                |
| -------------- | ---------------------- | ------------------------------------------ |
| `min_delay`    | float                  | The minimum delay time.                    |
| `block`        | SignallingBlockConfig  | A block of settings for blocking requests. |
| `concurrency`  | ConcurrencyLimitConfig | A block of settings for concurrency.       |
| `rate`         | RateLimitConfig        | A block of settings for rate limiting.     |

### SignallingBlockConfig

| Limit Settings | Type    | Description                            |
| -------------- | ------- | -------------------------------------- |
| `enabled`      | boolean | A block of settings for rate limiting. |
| `timeout`      | float   | A block of settings for rate limiting. |
| `poll`         | float   | A block of settings for rate limiting. |

### ConcurrencyLimitConfig

| Limit Settings    | Type    | Description                            |
| ----------------- | ------- | -------------------------------------- |
| `enabled`         | boolean | A block of settings for rate limiting. |
| `max_concurrency` | int     | A block of settings for rate limiting. |
| `max_queue`       | int     | A block of settings for rate limiting. |
| `timeout`         | float   | A block of settings for rate limiting. |
| `poll`            | float   | A block of settings for rate limiting. |

### RateLimitConfig

| Limit Settings | Type    | Description                            |
| -------------- | ------- | -------------------------------------- |
| `enabled`      | boolean | A block of settings for rate limiting. |
| `window`       | float   | A block of settings for rate limiting. |
| `max_request`  | int     | A block of settings for rate limiting. |

### Model Settings

| Model Settings | Type           | Description                                                               |
| -------------- | -------------- | ------------------------------------------------------------------------- |
| `file`         | string         | models: relative path from working directory. The path to the model file. |
| `relative`     | boolean        | A boolean value indicating whether the path is relative.                  |
| `name`         | string         | The name of the model.                                                    |
| `description`  | string         | A brief description of the model.                                         |
| `lossy`        | boolean        | A boolean value indicating whether lossy compression is used.             |
| `gpu`          | boolean or int | A boolean value indicating whether GPU is enabled.                        |

## Gunicorn

## Example

### `stylegan.service`

```ini
[Unit]
Description=Gunicorn StyleGAN Daemon
Requires=stylegan.socket
After=network.target

[Service]
Type=notify
User=spam
Group=spam
WorkingDirectory=/home/spam/stylegan
ExecStart=/usr/local/bin/python3.12 -B -m gunicorn -c gunicorn.config.py
RuntimeDirectory=stylegan
PrivateTmp=true
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=30
Restart=always

[Install]
WantedBy=multi-user.target
```

### `stylegan.socket`

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

## Notes

- set proxy header correctly
 For production (reverse proxy layer)
It is also recommeded to set limit header and body size

## License

[CC BY-NC 4.0](LICENSE)
