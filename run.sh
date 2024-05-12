echo 'please run ". ./run.sh" to set global environment variable'

if [[ -z "${webhooks_token}" ]]; then
    echo -n "Enter your webhooks_token:"  
    read webhooks_token  
    export webhooks_token=$webhooks_token
    echo $webhooks_token
else
    echo "webhooks_token is exists"
fi

killport() {   
    lsof -i tcp:$1 | awk 'NR!=1 {print $2}' | xargs -r kill 
    }

PORT_NUMBER=8234
killport $PORT_NUMBER
pdm run fastapi dev main.py --host 0.0.0.0 --port $PORT_NUMBER
