ps auxww | grep 'celery worker' | awk '{print $2}' | xargs kill -9
ps auxww | grep 'celery beat' | awk '{print $2}' | xargs kill -9
pkill -9 celery
echo '-----------stop------celery---------'