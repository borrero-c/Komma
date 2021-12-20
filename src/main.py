import os
import json
import pandas as pd
from scraper import popular_times as pt
from db import db_connection
from dao import table_dao

api_key = os.getenv('GOOGLE_API_KEY')
popular_times = {}

popular_times = pt.keep_searching(popular_times, api_key)

# with open('result.json', 'w') as fp:
#     json.dump(popular_times, fp)

# with open('result.json', 'r') as fp:
#     obj = json.loads(fp.read())

df_lists = {
    'names': [],
    'addresses': [],
    'popularity': [],
}

current_times_df_lists = {
    'names': [],
    'popularity': [],
    'times': [],
    'addresses': []
}



for k,v in popular_times.items():
    name = k
    current_pop_time = v.get('current_time_and_popularity')
    address = v.get('address')
    popularity = v.get('popularity')

    if current_pop_time:
        current_time = current_pop_time['time']
        current_popularity = current_pop_time['popularity']

        current_times_df_lists['names'].append(name)
        current_times_df_lists['times'].append(current_time)
        current_times_df_lists['popularity'].append(current_popularity)
        current_times_df_lists['addresses'].append(address)
    
    if popularity:
        popularity_string = json.dumps(popularity)
    
    df_lists['names'].append(name)
    df_lists['addresses'].append(address)
    df_lists['popularity'].append(popularity_string)


df = pd.DataFrame({
    'name': df_lists['names'],
    'address': df_lists['addresses'],
    'popularity': df_lists['popularity']
})

current_time_df = pd.DataFrame({
    'name': current_times_df_lists['names'],
    'time': current_times_df_lists['times'],
    'address': current_times_df_lists['addresses'],
    'popularity': current_times_df_lists['popularity']
})

# print(df)
# print(current_time_df)

db_connection = db_connection.get_db_connection()

table_dao.insert_rows(db_connection, 'myschema.popular_times_test', df)
table_dao.insert_rows(db_connection, 'myschema.current_popularity_test', current_time_df)
