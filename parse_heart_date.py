import json
import time
from datetime import datetime


def parse_heart_data():
    f = open('heart_data.json',)
    heart_data = json.load(f)
    for ind in range(len(heart_data["point"])):
        heart_point = {}
        ms = heart_data["point"][ind]["modifiedTimeMillis"]
        heart_point["time"] = datetime.fromtimestamp(float(ms) // 1000.0)
        heart_point["bpm"] = heart_data["point"][ind]["value"][0]["fpVal"]
        source = heart_data["point"][ind]["originDataSourceId"].split(':')
        heart_point["data source"] = source[2]
        if heart_point["data source"] != "com.google.android.gms":
            heart_point["manufacturer"] = source[3]
            heart_point["type"] = source[4]
            heart_point["uid"] = source[5]
        # print(heart_point)
    #     перевести heart_point в class для заполнения таблицы
    f.close()
    return


# parse_heart_data()