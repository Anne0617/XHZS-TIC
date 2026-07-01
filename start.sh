#!/bin/sh
# Start gunicorn in background for health check
gunicorn config.wsgi --log-file - --bind 0.0.0.0:${PORT:-8080} &
GUNICORN_PID=$!
# Wait for gunicorn to be ready
sleep 3
# Run database tasks
python manage.py migrate --noinput
python manage.py seed_data
# Keep running and wait for gunicorn
echo "Setup complete, waiting for gunicorn..."
wait $GUNICORN_PID
