"""
Gunicorn configuration for Academic Management System
Location: studentmanagement/gunicorn_config.py
Run with: gunicorn -c gunicorn_config.py studentmanagement.wsgi:application
"""

import multiprocessing
import os

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Server mechanics
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Logging
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "studentmanagement-gunicorn"

# Server hooks
def on_starting(server):
    print("Starting Gunicorn server for Academic Management System")

def when_ready(server):
    print("Gunicorn server ready. Spawning workers")

def on_exit(server):
    print("Gunicorn server shutting down")
