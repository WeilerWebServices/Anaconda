trap 'kill $(jobs -p)' EXIT
prefect_user_token=$(cat /var/run/secrets/user_credentials/prefectuser)
prefect_runner_token=$(cat /var/run/secrets/user_credentials/prefectrunner)
python -m http.server 8086 --directory endpoint &
prefect auth login -t $prefect_user_token
python flows.py
prefect agent start -t $prefect_runner_token
