import pandas as pd


def process_oecd_data(json_data):
   data = []
   for series_key, series_value in json_data.get('dataSets', [][0].get('series', {})).items():
       country_code = series_key.split(":")[1]
       value = series_value.get('value')


       data.append({'iso_code': country_code, 'value': value})


   df = pd.DataFrame(data)


   return df