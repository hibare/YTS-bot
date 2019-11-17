echo "$(date): executed script" >> /var/log/cron.log 2>&1
cd /app  >> /var/log/cron.log 2>&1
python3 yts_bot.py  >> /var/log/cron.log 2>&1
