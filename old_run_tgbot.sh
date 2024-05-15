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

findName(){
    ps aux | grep $1
}

killName(){
    ps aux | grep $1 | awk 'NR!=1 {print $2}' | xargs -r kill -9
}

name="telegram_bot"
# findName $name
killName $name

pdm run python telegram_bot.py
