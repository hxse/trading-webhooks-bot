echo 'please run ". ./run_tgbot.sh" to set global environment variable'

if [[ -z "${tg_bot_url_api}" ]]; then
    echo -n "Enter your tg_bot_url_api:"  
    read tg_bot_url_api  
    export tg_bot_url_api=$tg_bot_url_api
else
    echo "tg_bot_url_api is exists"
fi

findPort(){
    lsof -i tcp:$1
    }

killPort() {   
    lsof -i tcp:$1 | awk 'NR!=1 {print $2}' | xargs -r kill -9
    }

PORT_NUMBER=8234
# findPort $PORT_NUMBER
killPort $PORT_NUMBER
pdm run fastapi dev server.py --host 0.0.0.0 --port $PORT_NUMBER &
