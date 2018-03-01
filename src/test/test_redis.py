import os
import sys
import redis
import enum


# 接続パス、環境変数にあればそれ優先
REDIS_URL = os.environ.get('REDIS_URL') if os.environ.get(
    'REDIS_URL') != None else 'redis://localhost:6379'
# データベースの指定
DATABASE_INDEX = 1  # 0じゃなくあえて1

# コネクションプールから１つ取得
pool = redis.ConnectionPool.from_url(REDIS_URL, db=DATABASE_INDEX)
# コネクションを利用
r = redis.StrictRedis(connection_pool=pool)


class gateway(enum.Enum):
    anan  = "45327972"
    ishii = "45324459"

    
# def get_db_id(gateway_id= "45327972", node_id="7"):
    
#     return gateway_id+"_"+node_id

def set_db():
    # キーの登録 飛び飛び
    r.set('key' + str(i * 2), {'val': 'val' + str(i)})

    # キーの参照
    for i in range(10):
        key = 'key' + str(i)
        print(key + ' → ' + str(r.get(key)))

def del_db():
    # キー一覧
    print("キー一覧 --before--", r.keys())
    # 設定したデータベースの削除
    r.flushdb()
    print("キー一覧 --after--", r.keys())
    

if __name__ == '__main__' :
    # 接続エラーがあれば終了
    try:
        print('DB size : ' + str(r.dbsize()))
    except Exception as e:
        print(type(e))
        sys.exit()
    set_db()
    del_db()
