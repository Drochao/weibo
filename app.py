import re

import redis
from flask import Flask, request

from utils import b2str

redis_store = None

app = Flask(__name__)
conn = redis.Redis(host="127.0.0.1", port=6379)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/postWeibo', methods=['POST'])
def post_weibo():
    req_dict = request.get_json()
    user = req_dict.get('user')
    content = req_dict.get('content')
    new_data = re.findall(r'@(\w*)', content)
    try:
        old_data = conn.lrange('reco_by_' + user, 0, -1)
        old_data_str = b2str(old_data)
        for i in new_data:
            if i not in old_data_str:
                conn.rpush('reco_by_' + user, i)
    except Exception as e:
        print(e, 'data is not exist')
        for i in new_data:
            conn.rpush('reco_by_' + user, i)

    for i in new_data:
        try:
            be_reco = conn.lrange('be_reco_' + i, 0, -1)
            be_reco_str = b2str(be_reco)
            if user not in be_reco_str:
                conn.rpush('be_reco_' + i, user)
        except Exception as e:
            print(e, 'data is not exist')
            conn.rpush('be_reco_' + i, user)
    return 'post success'


@app.route('/suggest', methods=['POST'])
def suggest():
    req_dict = request.get_json()
    user = req_dict.get('user')
    be_reco_user = conn.lrange('be_reco_' + user, 0, -1)
    be_reco_user_str = b2str(be_reco_user)
    print(be_reco_user_str)
    reco_list = []
    for i in be_reco_user_str:
        reco_by_i = conn.lrange('reco_by_' + i, 0, -1)
        reco_by_i_str = b2str(reco_by_i)
        for j in reco_by_i_str:
            if j != user:
                reco_list.append(j)
    return str(set(reco_list))


if __name__ == '__main__':
    app.run()
