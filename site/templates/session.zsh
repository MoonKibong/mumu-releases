# Recipient: source this file in an interactive zsh session with tracing disabled.
# Do not execute it as a child process: the agent must inherit this shell's environment.
set +x
IFS= read -r -s "MUMU_API_KEY?Mumu API key: " || return 1
printf '\n'
[ -n "$MUMU_API_KEY" ] || return 1
export MUMU_API_KEY
# Success: test -n "$MUMU_API_KEY". Do not print its value.
