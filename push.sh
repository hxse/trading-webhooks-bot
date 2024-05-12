echo 'please run ". ./push.sh" to set global environment variable'

if [[ -z "${github_token}" ]]; then
    echo -n "Enter your github_token:"  
    read github_token
    export hxse_github_token=$github_token
    echo $github_token
else
    echo "github_token exists"
fi


echo -n "Enter commit:"  
read commit
git add .
git commit -m $commit
git push "https://hxse:${github_token}@github.com/hxse/trading-webhooks-bot.git"
