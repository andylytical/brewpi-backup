# brewpi-backup
Backup brewlog history from brewpi and create graphs for offline viewing.

### Dependencies
* Dropbox account (a free account is fine)

### Notes

1. Assume logged in as user `pi` with default home at `/home/pi` and default brewpi
   webdir at `/var/www/html`.
1. Tested on Raspbery Pi 3 running `Raspbian (jessie) LITE`
1. Per-Day Fermentation Rate requires a Tilt Hydrometer. Backup HTML files *should* still work fine
   but the fermentation rates will be empty.

# Installation

### Create a Dropbox app
1. Go to https://www.dropbox.com/developers/apps
1. Click `Create app`
1. Choose an API: *Dropbox API*
1. Access type: *App folder*
1. App name: *YOUR_APP_NAME* 
   * this is a freetext field, type whatever name you like here
   * The name you provide here will appear as a folder in the `Apps` directory of your Dropbox
   * Files backed up by the `sync` process below will be stored in this folder
1. Click the `Create app` button
1. The new app will be created and will load the *Settings* screen.
1. Look for the section titled `Generated access token` and click the
   `Generate` button.
1. Copy the access token
### Save dropbox access token on the raspberry pi
1. Login to raspberry pi as user `pi`
1. Save the access token to `/home/pi/.dropbox_token`
   * `echo "DROPBOX-ACCESS-TOKEN" > /home/pi/.dropbox_token`
      * NOTE: Replace the text `DROPBOX-ACCESS-TOKEN` with the actual token generated above
### Install brewpi-backup repo
1. `cd $HOME`
1. `git clone https://github.com/andylytical/brewpi-backup.git`
1. `/home/pi/brewpi-backup/install.sh`
1. Logout and login again (this is required to reload user environment with modifications made during install)

# Usage
### Create static html pages for each brewlog
1. `python3 /home/pi/brewpi-backup/mk_brewlog_graphs.py`

### Sync static html pages (and supporting files) to Dropbox
1. `python3 /home/pi/brewpi-backup/sync.py`
2. The static HTML pages (created above) should now be *sync*'d to the folder in `Dropbox/Apps/YOUR_APP_NAME`
3. Double click one of the HTML pages to view it in your default web browser

# Automation
1. Create a cron job for running each command above
   1. `crontab -e`
      1. `01 */4 * * * python3 /home/pi/brewpi-backup/mk_brewlog_graphs.py`
      1. `12 */4 * * * python3 /home/pi/brewpi-backup/sync.py`


