sh ./stop.sh
echo "------start------"
sh ./celery_start.sh & /root/projects/TaxPlatformService/venv/bin/gunicorn -c gunicorn.py application:app
echo "------end-------"