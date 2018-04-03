from datetime import datetime
from datetime import timedelta

from src.daily_db import extract_data
from src.kosen_api import download_day_data
from src.daily_db import save_daily_data


def get_daily_data(sensor_id, node_id, dt_bgn, dt_end, env_id):
    '''日ごとの環境データを返す
    昨日より未来の日付は指定できない
    TODO:今日のデータは別の関数で取得するようにする(グラフでなく文字表示する用)'''
    debug_format = '%Y-%m-%d'
    daily_temps = []
    
    dt_yday = datetime.now().replace(hour=23,minute=59,second=59,microsecond=999) - timedelta(days=1)
    if dt_end > dt_yday:
        dt_end = dt_yday
    
    dt_target = dt_bgn
    while dt_target <= dt_end:

        daily_temp = extract_data(sensor_id, node_id, dt_target, env_id)

        if not daily_temp:
            print("Not found on DB "+ datetime.strftime(dt_target, debug_format))
            response_list = download_day_data(sensor_id, node_id, dt_target, env_id)
            save_daily_data(sensor_id, node_id, dt_target, env_id, response_list)
            
            #redis から出すときバイナリになるため、一回DBにセットしたものを使う.
            daily_dict = extract_data(sensor_id, node_id, dt_target, env_id)
            #print('DB save this:', daily_dict)
            daily_temps.append(daily_dict)
        else:
            print("Can find on DB {0}\n Data: {1}".format(datetime.strftime(dt_target, debug_format), str(daily_temp)))
            daily_temps.append(daily_temp)
        
        dt_target += timedelta(days=1)

    return daily_temps

def update_one_year(sensor_id, node_id):
    '''一年分'''
    debug_format = '%Y-%m-%d'
    daystamp_format = '%Y%m%d'
    
    dt_bgn = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0) -  timedelta(days=250, hours=0, minutes=0, seconds=0, microseconds=0)
    dt_end = datetime.now().replace(hour=23,minute=59,second=59,microsecond=999) - timedelta(days=1)
    
    dt_target = dt_bgn
    while dt_target <= dt_end:
        daily_dict = download_one_day_data(sensor_id, node_id, dt_target, 0 )
        daily_dict['all'] = True
        put_data(sensor_id, node_id, dt_target, 0, daily_dict)
        print('DB update:', extract_data(sensor_id, node_id, dt_target, 0))
        dt_target += timedelta(days=1)

    return True

if __name__ == '__main__' :
    # anan  = {'sensor': '45327972', 'nodes': ['7', '15']}
    # ishii  = {'sensor': '45324459', 'nodes': ['7', '15']}
    now = datetime.now()
    response = get_daily_data('45324459', '7', now - timedelta(days=4),now - timedelta(days=3), 1)
    print(response)