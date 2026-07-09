#!/bin/sh

while true; do
    echo 'Running oppiacron...'
    python manage.py oppiacron --hours=48

    echo 'Running update_summaries...'
    python manage.py update_summaries

    sleep "${CRON_INTERVAL_SECONDS:-3600}"
done
