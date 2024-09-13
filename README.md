# StyleGAN FastAPI

Simplified Web REST API of the StyleGAN using FastAPI

This is a web backend application to make the generator models trained by [Precure StyleGAN ADA](https://github.com/curegit/precure-stylegan-ada) available on the web in a simplified way.
[StyleGAN Vue](https://github.com/curegit/stylegan-vue) is a sample implementation of its frontend client and is [deployed here](#) connected to [a demo backend with some models](#) for immediate trial.

## API Specifications

Refer to the Swagger or ReDoc documentation on the sample backend or on your deployed instance at the paths `/docs` or `/redoc`.

## Application Requirements

To run this application, you need a Unix-like system with Python >= 3.12 installed.

Use the `requirements.txt` to install the minimal dependencies for serving and inferencing, including the dependencies of [Precure StyleGAN ADA](https://github.com/curegit/precure-stylegan-ada).

```sh
pip3 install -r requirements.txt
```

While Uvicorn is the recommended as ASGI middleware, other alternatives such as Hypercorn may also work.
However, in a production environment, it is common to use process replication with a combination of Gunicorn and Uvicorn.

## Quick Start: Running the default server

This repository contains the default server configuration using Uvicorn with some trained models.
You can quickly try it out as follows:

```sh
git clone --recursive https://github.com/curegit/stylegan-fastapi.git
cd stylegan-fastapi
pip3 install -r requirements.txt
python3 -m uvicorn main:app
```

Please note that this setup is intended for trial or debugging purposes only and is not suitable for production use as it does not support process replication.

## Application Configuration

StyleGAN FastAPI can be customized by using a configuration file.
StyleGAN FastAPI uses the TOML format for configuration, and the default server's TOML file is located in `default/config.toml`.

You can specify a different configuration TOML file to use by setting the `STYLEGAN_TOML` environment variable.
`STYLEGAN_TOML` must be an absolute TOML file path or a TOML file path relative to the working directory.
Note that the `STYLEGAN_TOML` environment variable must be set before importing the `api/` Python package.

```sh
export STYLEGAN_TOML="./custom_config.toml"
uvicorn main:app
```

### Configuration TOML Specifications

The configuration file follows the standard TOML format.
A complete raw schema definition and its default values can be found in the `api/conf.py` Python file.

All properties are optional except the `file` field in `ModelConfig` to specify model files, and you must specify at least one model.

#### General Settings (Root)

| Key           | Type                                    | Description                                                          |
| ------------- | --------------------------------------- | -------------------------------------------------------------------- |
| `title`       | string                                  | The title of the API service. Used in the OpenAPI spec.              |
| `version`     | string                                  | The version number of the API. Used in the OpenAPI spec.             |
| `description` | string                                  | A brief description of the API service. Used in the OpenAPI spec.    |
| `docs`        | boolean                                 | Whether the Swagger page is enabled. The default is `true`.          |
| `redoc`       | boolean                                 | Whether the ReDoc page is enabled. The default is `true`.            |
| `lossy`       | boolean                                 | Whether to use lossy compression for output. The default is `false`. |
| `server`      | [ServerConfig](#serverconfig)           | Internal server configuration settings.                              |
| `models`      | { string: [ModelConfig](#modelconfig) } | A dictionary of model configurations to use.                         |

#### ServerConfig

| Key       | Type                        | Description                                                                                                              |
| --------- | --------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `gpu`     | boolean or int              | A boolean indicating whether GPU is enabled or an integer value specifying which GPU device is being used.               |
| `logger`  | string                      | The name of the parent logger from which this application's logger is derived.                                           |
| `tmp_dir` | string                      | The path to the temporary directory where the runtime files are located. Volatile locations such as `tmpfs` are allowed. |
| `http`    | [HTTPConfig](#httpconfig)   | HTTP configuration settings.                                                                                             |
| `limit`   | [LimitConfig](#limitconfig) | Limit configuration settings.                                                                                            |

#### HTTPConfig

| Key                 | Type                      | Description                                                                                                                                                                                                                                                                                                                    |
| ------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `forwarded`         | boolean                   | Indicates whether reverse proxy servers are involved in the path of the requests. The default is `false`. You can leave this `false` if your middleware such as Uvicorn is configured to fill in real remote address info.                                                                                                     |
| `forwarded_headers` | [string]                  | A list of headers to check for the original client address, such as "Forwarded" or "X-Forwarded-For", which can be multiple and is left in order. This is used for identifying clients when `forwarded` is true. Regardless of the header type, the entire string equivalence of the header value is used to identify clients. |
| `cors`              | [CORSConfig](#corsconfig) | Cross-Origin Resource Sharing (CORS) configuration settings.                                                                                                                                                                                                                                                                   |

#### CORSConfig

| Key       | Type     | Description                                                                               |
| --------- | -------- | ----------------------------------------------------------------------------------------- |
| `enabled` | boolean  | A boolean value indicating whether CORS configuration is enabled. The default is `false`. |
| `origins` | [string] | A list of allowed origins. Set `["*"]` for wildcard.                                      |

#### LimitConfig

| Key           | Type                                              | Description                                             |
| ------------- | ------------------------------------------------- | ------------------------------------------------------- |
| `min_delay`   | float                                             | The minimum response delay time for CPU-bound requests. |
| `block`       | [SignallingBlockConfig](#signallingblockconfig)   | A block of settings for the signalling block.           |
| `concurrency` | [ConcurrencyLimitConfig](#concurrencylimitconfig) | A block of settings for the concurrency limit.          |
| `rate`        | [RateLimitConfig](#ratelimitconfig)               | A block of settings for rate limiting.                  |

#### SignallingBlockConfig

| Key       | Type    | Description                                                                                                           |
| --------- | ------- | --------------------------------------------------------------------------------------------------------------------- |
| `enabled` | boolean | Whether the signalling block for CPU-bound requests (delaying simultaneous requests from the same client) is enabled. |
| `timeout` | float   | The timeout duration in seconds for the signalling block.                                                             |
| `poll`    | float   | The polling interval in seconds for the signalling block.                                                             |

#### ConcurrencyLimitConfig

| Key               | Type    | Description                                                      |
| ----------------- | ------- | ---------------------------------------------------------------- |
| `enabled`         | boolean | Whether the concurrency limit for CPU-bound requests is enabled. |
| `max_concurrency` | int     | The maximum number of concurrent requests.                       |
| `max_queue`       | int     | The maximum number of requests in the queue.                     |
| `timeout`         | float   | The timeout duration in seconds for the concurrency limit.       |
| `poll`            | float   | The polling interval in seconds for the concurrency limit.       |

#### RateLimitConfig

| Key           | Type    | Description                                                                         |
| ------------- | ------- | ----------------------------------------------------------------------------------- |
| `enabled`     | boolean | A boolean value indicating whether rate limiting for CPU-bound requests is enabled. |
| `window`      | float   | The time window for rate limiting in seconds.                                       |
| `max_request` | int     | The maximum number of requests allowed in the time window.                          |

#### ModelConfig

| Key           | Type           | Description                                                                                                                                                        |
| ------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `file`        | string         | The path to the model file.                                                                                                                                        |
| `relative`    | boolean        | Indicates whether the model file path is relative to this TOML file rather than the working directory. The default value is `false`.                               |
| `name`        | string         | A display name of the model.                                                                                                                                     |
| `description` | string         | A short description of the model.                                                                                                                                  |
| `lossy`       | boolean        | Whether lossy compression is used. This overrides the `lossy` in the [General Settings](#general-settings-root).                                                   |
| `gpu`         | boolean or int | A boolean indicating whether GPU is enabled or an integer value specifying which GPU device is being used. This overrides the [ServerConfig](#serverconfig) `gpu`. |

## Gunicorn

`logger = "gunicorn.error"`

```py
from guni.conf import *

wsgi_app = "main:app"
workers = 3
raw_env = ["STYLEGAN_TOML=myconfig.toml"]
```

### Service Configuration Example

#### `stylegan.service`

When using
set `tmp_dir = "/run/stylegan"` in StyleGAN FastAPI co better perfomance

```ini
[Unit]
Description=Gunicorn StyleGAN Daemon
Requires=stylegan.socket
After=network.target
After=syslog.target

[Service]
Type=notify
User=spam
Group=spam
WorkingDirectory=/home/spam/stylegan
ExecStart=/usr/local/bin/python3.12 -B -m gunicorn -c gunicorn.conf.py \
                                                   --log-level info \
                                                   --log-file /var/log/stylegan/system.log \
                                                   --access-logfile /var/log/stylegan/access.log \
                                                   --capture-output
RuntimeDirectory=stylegan
LogsDirectory=stylegan
PrivateTmp=true
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStartSec=240
TimeoutStopSec=30
Restart=always

[Install]
WantedBy=multi-user.target
```

#### `stylegan.socket`

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

#### `logrotate.d/stylegan`

```txt
/var/log/stylegan/*.log {
  monthly
  dateformat -%Y-%m-%d
  rotate 12
  compress
  ifempty
  missingok
  copytruncate
  maxsize 100M
}
```

## Notes

- Ensure that proxy headers, if used, are set correctly (e.g., Forwarded, X-Forwarded-For) for production environments with a reverse proxy layer.
- It is also recommended to set header and body size limits via Gunicorn or a reverse proxy.

## License

[CC BY-NC 4.0](LICENSE)
