import pandas as pd
import os

DATA_FOLDER = '../mfg-data'

df_6hr = pd.read_csv(os.path.join(DATA_FOLDER, "6hr_data"))
data_6hr_map = {}
for i in range(0,len(df_6hr)):
    data_6hr_map[str(df_6hr['sensor_name'][i])] = {'normal_min':df_6hr['Normal_min'][i],
                                                   'normal_max': df_6hr['Normal_max'][i],
                                                   'anomaly_min': df_6hr['Anomolous_min'][i],
                                                   'anomaly_max': df_6hr['Anomolous_max'][i]}


def populate_6hr_values():

    pass

