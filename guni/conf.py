import os as _os
import uvicorn_worker as _uvicorn_worker

daemon = False
preload_app = True
workers = _os.cpu_count() + 1
worker_class = _uvicorn_worker.UvicornWorker

max_requests = 1024
max_requests_jitter = 128
graceful_timeout = 60

limit_request_line = 2048
limit_request_fields = 64
limit_request_field_size = 1024
