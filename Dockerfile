FROM python:3

# Install cron
RUN apt-get update
RUN apt-get install cron -y

# Add source directory
ADD src /app

# Install requirements
RUN pip3 install -r /app/requirements.txt

# # Grant execution rights
# RUN chmod +x /app/yts_bot.py

# # Grant execution rights
# RUN chmod +x /app/script.sh

# # Add crontab file in the cron directory
# ADD src/crontab /etc/cron.d/yts-cron

# # Grant execution rights on the cron job
# RUN chmod 0644 /etc/cron.d/yts-cron

# # Create the log file to be able to run tail
# RUN touch /var/log/cron.log

RUN crontab /app/crontab

# Run the command on container startup
CMD ["cron", "-f"]