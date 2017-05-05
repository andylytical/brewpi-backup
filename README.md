# brewpi-backup
Backup brewlog history from brewpi and create graphs for offline viewing.

NOTES:

1. Assume logged in as user `pi` with default home at `/home/pi` and default brewpi
   webdir at `/var/www/html`.
1. Tested on Raspbery Pi 3 running `Raspbian GNU/Linux 8 (jessie)`

# Dependencies
* Dropbox account

# Installation
1. Create a Dropbox app in the 
   1. Go to https://www.dropbox.com/developers/apps
   1. Click `Create app`
   1. Choose an API: *Dropbox API*
   1. Access type: *App folder*
   1. App name: *this is freetext, type whatever name you like here*
   1. Click the `Create app` button
   1. The new app will be created and will load the *Settings* screen.
   1. Look for the section titled `Generated access token` and click the
      `Generate` button.
   1. Copy the `Generated access token`
1. Save dropbox app access token on the raspberry pi
   1. Login to raspberry pi as user `pi`
   1. Create a new file called `/home/pi/.dropbox_token` and paste the access token
1. Download brewpi-backup repo
   1. `cd $HOME`
   1. `git clone https://github.com/andylytical/brewpi-backup.git`
   1. `/home/pi/brewpi-backup/install.sh`

# Usage
## Create static html pages for offline viewing
```
python3 /home/pi/brewpi-backup/mk_brewlog_graphs.py
```

## Sync static html pages (and supporting files) to Dropbox
```
python3 /home/pi/brewpi-backups/sync.py
```

# Automation
1. Create a cron job for running each command above
   1. `crontab -e`
   1. `01 */4 * * * python3 /home/pi/brewpi-backup/mk_brewlog_graphs.py`
   1. `12 */4 * * * python3 /home/pi/brewpi-backups/sync.py`


