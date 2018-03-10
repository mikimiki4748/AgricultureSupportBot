from datetime import datetime
from datetime import timedelta

from src.daily_db import extract_data
from src.daily_db import put_data
from src.kosen_api import download_one_day_data


def get_daily_temp(sensor_id, node_id, dt_bgn, dt_end):
    '''日ごとの平均・最高・最低気温を返す
    昨日より未来の日付は指定できない
    今日のデータは別の関数で取得する'''
    date_format = '%Y-%m-%d'
    daystamp_format = '%Y%m%d'
    daily_temps = []
    
    dt_yday = datetime.now().replace(hour=23,minute=59,second=59,microsecond=999) - timedelta(days=1)
    if dt_end > dt_yday:
        dt_end = dt_yday
    
    dt_target = dt_bgn
    while dt_target <= dt_end:

        daily_temp = extract_data(sensor_id, node_id, dt_target, 0)
        
        if not daily_temp:
            print("Not found on DB "+ datetime.strftime(dt_target, date_format))
            daily_dict = download_one_day_data(sensor_id, node_id, 0, dt_target)
            
            daily_dict['all'] = True
            put_data(sensor_id, node_id, dt_target, 0, daily_dict)
            #redis から出すときバイナリになるため、一回DBにセットしたものを使う.
            daily_dict = extract_data(sensor_id, node_id, dt_target, 0)
            print('DB save this:', daily_dict)
            daily_temps.append(daily_dict)
        else:
            # print("Can find on DB . date:"+ datetime.strftime(dt_target, date_format))
            # print("Can find on DB . data:"+ str(daily_temp))
            daily_temps.append(daily_temp)
        
        dt_target += timedelta(days=1)

    return daily_temps