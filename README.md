# StyleGAN FastAPI

## Requirements

```sh
pip3 install -r requirements.txt
```

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
