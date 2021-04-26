from crontab import CronTab

# Creates a crontab that schedules the
# referesh of the log file for every Sunday
# add other schedule jobs in here
# author : @mihaivaduva21
# Usage:
# Install : python3 -m pip install python-crontab
# List : crontab -l
# Remove : crontab -r

# TODO : change user to the username and paths as the ones on server.
cron = CronTab(user='wdw')
job = cron.new(command='python3 /home/wdw/chessboard/project/src/utils/refresh_logfile.py')
job.dow.on('SUN')
cron.write()
