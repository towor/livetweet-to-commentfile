import tweepy
import datetime
import sys
import query_config as qc
from api_config import key_and_token
from datetime import timedelta

CONSUMER_KEY = key_and_token["Consumer_key"]
CONSUMER_SECRET = key_and_token["Consumer_secret"]
ACCESS_TOKEN = key_and_token["Access_token"]
ACCESS_SECRET = key_and_token["Access_secret"]

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

#検索ワードをセット
query = qc.query
since_date = qc.since_date 
until_date = qc.until_date
filename = qc.filename

#vpos計算用のdatetime型を準備
since_date_cut = since_date.rstrip("_JST").replace("_", " ")
start_date = datetime.datetime.strptime(since_date_cut, "%Y-%m-%d %H:%M:%S")

sum_comment = 0
roop_counter = 0
num_from = 1    #進捗表示用
num_to = 1000   #進捗表示用

search = api.search(q=query, lang="ja", count=100, since=since_date, until=until_date, exclude="retweets")
if len(search) == 0:    #取得件数が0件やAPI範囲外の時の返り値は空のリスト
    print("ツイートを取得できませんでした(APIの取得範囲外かも)")
    sys.exit()
else:
    f = open(filename, "w", encoding="utf-8")
    f.write("<packet>\n")
    roop_counter += 1
    next_max_id = search[-1].id #次回ループのため取得したツイートの中で一番古いもののツイートIDを取得
    print(f"ツイート収集中...({str(num_from)} ~ {str(num_to)})")
    for tweet in search:
        if "http" in tweet.text: #リンクや画像つきのツイートをスキップ
            continue
        else:
            sum_comment += 1
            live_comment = tweet.text
            hashtag_list = tweet.entities.get("hashtags")
            for hashtag in hashtag_list:
                live_comment = live_comment.replace("#" + hashtag['text'], "")

            live_comment = live_comment.replace("\n", " ").strip()
            vpos = str(((tweet.created_at + timedelta(hours=9) - start_date).seconds)*100) #UTCで格納されているため９時間勧めてから計算
            twitter_user_id = tweet.user.id_str
            f.write(f'<chat vpos="{vpos}" user_id="{twitter_user_id}">{live_comment}</chat>\n')

while True:
    search = api.search(q=query, lang="ja", count=100, since=since_date,
                        until=until_date, exclude="retweets", max_id=next_max_id-1)
    if len(search) == 0:
        print("収集が完了しました。")
        break
    else:
        roop_counter +=1
        next_max_id = search[-1].id
        if roop_counter % 10 == 1: #総取得件数が1000の倍数件時に進捗を表示
            num_from += 1000
            num_to += 1000
            print(f"ツイート収集中...({str(num_from)} ~ {str(num_to)})")
        for tweet in search:
            if "http" in tweet.text:
                continue
            else:
                sum_comment += 1
                live_comment = tweet.text
                hashtag_list = tweet.entities.get("hashtags")
                for hashtag in hashtag_list:
                    live_comment = live_comment.replace("#" + hashtag['text'], "")

                live_comment = live_comment.replace("\n", " ").strip()
                vpos = str(((tweet.created_at + timedelta(hours=9) - start_date).seconds)*100)
                twitter_user_id = tweet.user.id_str
                f.write(f'<chat vpos="{vpos}" user_id="{twitter_user_id}">{live_comment}</chat>\n')

f.write("</packet>")
f.close()
print(str(sum_comment) + "件の実況ツイートをコメントとして保存しました。")
