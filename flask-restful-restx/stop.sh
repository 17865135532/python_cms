echo "------stop------"
sh ./celery_stop.sh
pkill -9 gunicorn
echo "------end-------"