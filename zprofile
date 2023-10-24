# Set PATH, MANPATH, etc., for Homebrew.
eval "$(/opt/homebrew/bin/brew shellenv)"
# Add Go to PATH
export PATH=$PATH:$(go env GOPATH)/bin
# SSH Agent
eval $(ssh-agent -s)

eval "$(/opt/homebrew/bin/brew shellenv)"

export AWS_PROFILE=sockshop
export OBSERVE_CUSTOMER=194903047712
export OBSERVE_DOMAIN=observeinc.com
export OBSERVE_USER_EMAIL=jack.coates@observeinc.com

ssh_with_color() {
    CHANGE_TERMINAL_COLOR=/usr/local/bin/change_terminal_profile.sh
    # Left out Homebrew because that's my real default
    arr[1]="Red Sands"
    arr[2]="Ocean"
    arr[3]="Man Page"
    arr[4]="Basic"
    arr[5]="Novel"
    arr[6]="Silver Aerogel"
    arr[7]="Pro"
    arr[8]="Grass"
    rand=$[$RANDOM % ${#arr[@]}]
    NEW_SCHEME=${arr[$rand]}

    if [ -f ${CHANGE_TERMINAL_COLOR} ]; then
        $CHANGE_TERMINAL_COLOR $NEW_SCHEME
        exec ssh "$@"
    else
        ssh "$@"
    fi
}
alias ssh=ssh_with_color

