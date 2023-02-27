import os
import pathlib
import uvicorn.workers

a = pathlib.Path(__file__).resolve().parent()

wsgi_app = "main:app"

bind = "127.0.0.1:8080"
daemon = False
preload_app = True
workers = os.cpu_count() or 2
worker_class = uvicorn.workers.UvicornWorker
max_requests = 1024
max_requests_jitter = 128
graceful_timeout = 60

limit_request_line = 2048
limit_request_fields = 64
limit_request_field_size = 1024

pythonpath = str(a)
