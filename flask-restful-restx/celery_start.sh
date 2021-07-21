#!/bin/bash

log_path=$LOG_PATH

rm -f "${log_path}/worker.pid"
rm -f "${log_path}/beat.pid"

echo "------start------celery---------"

/root/projects/TaxPlatformService/venv/bin/celery -A app.jobs.celery_app worker -l info \
      --pidfile="${log_path}/worker.pid" \
& /root/projects/TaxPlatformService/venv/bin/celery -A app.jobs.celery_app beat -l info \
      --pidfile="${log_path}/beat.pid" \
& /root/projects/TaxPlatformService/venv/bin/celery -A app.jobs.celery_app flower -l info \
      --pidfile="${log_path}/flower.pid"

echo "------end------celery---------"
