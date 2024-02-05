export PYENV_ROOT="$HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
alias tf="terraform"
alias ll="ls -l"
alias la="ls -la"
alias diffy="diff -y --recursive --suppress-common-lines"
alias findy="find . -name "
alias dates='date +%s'
alias gti="git"
source /opt/homebrew/opt/zsh-git-prompt/zshrc.sh
PROMPT='%B%m%~%b$(git_super_status) %# '
