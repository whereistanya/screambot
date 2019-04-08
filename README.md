Screambot just freaks out about everything all the time, on slack.

# running screambot

## Create a slackbot in your workspace.
* Go to https://api.slack.com/apps and create new app.

* Give it a name and a background colour.

* Go to OAuth and Permissions" and give it the "post to specific channels in Slack" and "Add a bot user" scopes.

* Go to Bot Users and add a bot user.

* Go to OAuth and Permissions and Install App to Workspace. This generates access tokens. 

## Set up a server to run it on
I use the smallest size of GCE VM. Any server will do so long as slack can get to it.

## Get the code working
* Install the slackclient module. On ubuntu that's:  

`sudo apt-get install python-pip`  
`sudo pip install slackclient`

* Grab the Bot User OAuth Access Token from the OAuth and Permissions tab for your app on https://api.slack.com/apps. Put it in a file called secret.py, like
SLACK_BOT_TOKEN="xoxb-your-access-token"

* Copy down the code. To run the tests, install python-pytest  
`sudo apt-get install python-pytest`

and run

`$ py.test test_screambot.py`

## Configure systemd to keep the bot running.

There's a systemd config at config/screambot.service 

Change the directory in WorkingDirectory= and ExecStart= to point at wherever the code is.

Drop it at `/etc/systemd/system/screambot.service` and enable it to start at boot with
`systemctl enable screambot`. It logs to regular syslog so grep for
screambot in /var/log/daemon.log or equivalent.

You can start/stop it with `systemctl start`, `systemctl stop`, etc.
