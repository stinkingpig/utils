#!/bin/sh
## Shamelessly stolen from Michael Richmond (mar) and hacked up
## Set the default Terminal profile name
## This profile will be used if no argument
## provided to this script.
## Add this to your .zprofile:
## ssh_with_color() {
##     CHANGE_TERMINAL_COLOR=/usr/local/bin/change_terminal_profile.sh
##     # Left out Homebrew because that's my real default
##     arr[1]="Red Sands"
##     arr[2]="Ocean"
##     arr[3]="Man Page"
##     arr[4]="Basic"
##     arr[5]="Novel"
##     arr[6]="Silver Aerogel"
##     arr[7]="Pro"
##     rand=$[$RANDOM % ${#arr[@]}]
##     NEW_SCHEME=${arr[$rand]}
## 
##     if [ -f ${CHANGE_TERMINAL_COLOR} ]; then
##         $CHANGE_TERMINAL_COLOR $NEW_SCHEME
##         exec ssh "$@"
##     else
##         ssh "$@"
##     fi
## }
## alias ssh=ssh_with_color

DEFAULT_SCHEME="Homebrew"

## Set SCHEME to $1 if an argument is provided,
## otherwise set SCHEME to $DEFAULT_SCHEME
SCHEME=${1:-$DEFAULT_SCHEME}

## Sanitize the profile name by adding double
## quotes on each end.
SAFE_SCHEME=\"${SCHEME//\"/}\"

/usr/bin/osascript <<EOF
tell application "Terminal"
  set current settings of window 1 to settings set $SAFE_SCHEME
end tell
EOF

