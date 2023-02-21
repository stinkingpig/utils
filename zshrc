# Pyenv stuff
export PYENV_ROOT="$HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
# Handy aliases
alias tf="terraform"
alias ll="ls -l"
alias la="ls -la"
alias diffy="diff -y --recursive --suppress-common-lines"

