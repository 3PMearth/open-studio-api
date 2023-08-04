#!/usr/bin/env bash

# check pip version
pip --version

# Create the celery systemd service file
echo "[Unit]
Description=Celery service
After=network.target
StartLimitInterval=0

[Service]
Type=simple
Restart=always
RestartSec=1
User=root
WorkingDirectory=/var/app/current
ExecStart=$PYTHONPATH/celery --app=studio_api worker --logfile="/var/log/app-logs/celery.log" --loglevel=INFO
ExecReload=$PYTHONPATH/celery --app=studio_api worker --logfile="/var/log/app-logs/celery.log" --loglevel=INFO
EnvironmentFile=/opt/elasticbeanstalk/deployment/env

[Install]
WantedBy=multi-user.target
" | tee /etc/systemd/system/celery.service

# Start celery service
systemctl start celery.service

# Enable celery service to load on system start
systemctl enable celery.service

# restart celery service
systemctl restart celery.service