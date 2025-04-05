# import requests
# from flask import Flask, render_template, jsonify, request
# import pandas as pd
# import plotly
# import plotly.express as px
# import json
# import xml.etree.ElementTree as ET

# app = Flask(__name__)

# def fetch_oecd_data():
#     url = "https://sdmx.oecd.org/public/rest/data/OECD.ENV.EPI,DSD_EWASTE@DF_EWASTE,1.0/.A..T.GEN?startPeriod=2010&dimensionAtObservation=AllDimensions"
#     response = requests.get(url)
#     if response.status_code == 200:
#         # Return the XML content as text, not JSON
#         return response.text
#     else:
#         print(f"Error fetching data: {response.status_code}")
#         return {"error": f"Failed to fetch data: {response.status_code}"}

# def process_oecd_data(xml_data):
#     """
#     Process the XML data from OECD API into a pandas DataFrame
#     """
#     try:
#         # Define namespaces used in the XML
#         namespaces = {
#             'message': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message',
#             'generic': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic',
#             'common': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common'
#         }
        
#         # Parse XML
#         if isinstance(xml_data, dict) and "error" in xml_data:
#             return pd.DataFrame()  # Return empty DataFrame if error
            
#         root = ET.fromstring(xml_data)
        
#         # Lists to store data
#         countries = []
#         years = []
#         values = []
#         units = []
#         measures = []
#         categories = []
        
#         # Find all observation elements
#         observations = root.findall('.//generic:Obs', namespaces)
        
#         for obs in observations:
#             # Extract data from each observation
#             obs_key = obs.find('./generic:ObsKey', namespaces)
            
#             # Initialize variables
#             country = None
#             year = None
#             value = None
#             unit = None
#             measure = None
#             category = None
            
#             # Get values from ObsKey
#             for key_value in obs_key.findall('./generic:Value', namespaces):
#                 id_attr = key_value.get('id')
#                 value_attr = key_value.get('value')
                
#                 if id_attr == 'TIME_PERIOD':
#                     year = value_attr
#                 elif id_attr == 'REF_AREA':
#                     country = value_attr
#                 elif id_attr == 'UNIT_MEASURE':
#                     unit = value_attr
#                 elif id_attr == 'MEASURE':
#                     measure = value_attr
#                 elif id_attr == 'PRODUCT_CATEGORIES':
#                     category = value_attr
            
#             # Get observation value
#             obs_value = obs.find('./generic:ObsValue', namespaces)
#             if obs_value is not None:
#                 value = float(obs_value.get('value'))
                
#                 # Add data to lists
#                 countries.append(country)
#                 years.append(int(year))
#                 values.append(value)
#                 units.append(unit)
#                 measures.append(measure)
#                 categories.append(category)
        
#         # Create DataFrame
#         df = pd.DataFrame({
#             'country': countries,
#             'year': years,
#             'value': values,
#             'unit': units,
#             'measure': measures,
#             'category': categories
#         })
        
#         print(f"Processed data: {len(df)} records found")
#         return df
    
#     except Exception as e:
#         print(f"Error processing OECD data: {e}")
#         # Return empty DataFrame with expected columns if processing fails
#         return pd.DataFrame(columns=['country', 'year', 'value', 'unit', 'measure', 'category'])

# def load_policy_data():
#     df = pd.read_csv('data/policies.csv')
#     return df

# @app.route('/')
# def index():
#     data_types = ['policy', 'ewaste']
#     return render_template('index.html', data_types=data_types)

# @app.route('/get_data')
# def get_data():
#     # Get selected data type from dropdown
#     data_type = request.args.get("data_type", "policy")  # Default to policy
    
#     try:
#         if data_type == "policy":
#             df = load_policy_data()
#             fig = create_policy_map(df)
#         else:  # ewaste
#             raw_data = fetch_oecd_data()
#             if isinstance(raw_data, dict) and "error" in raw_data:
#                 return jsonify({"error": raw_data["error"]})
#             ewaste_df = process_oecd_data(raw_data)
#             if ewaste_df.empty:
#                 return jsonify({"error": "No data available"})
#             fig = create_ewaste_map(ewaste_df)
        
#         graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
#         return jsonify(graphJSON)
#     except Exception as e:
#         print(f"Error processing data: {e}")
#         return jsonify({"error": f"Error processing data: {str(e)}"})

# def create_policy_map(df):
#     """
#     Create a choropleth map showing policy data by country
#     """
#     fig = px.choropleth(
#         df,
#         locations='country_code',  # Column containing ISO-3 country codes
#         color='policy_score',      # Column for color intensity
#         hover_name='country',      # Column for hover labels
#         title='E-Waste Policies by Country',
#         color_continuous_scale='Viridis',
#         labels={'policy_score': 'Policy Score'}
#     )
    
#     fig.update_layout(
#         geo=dict(
#             showframe=False,
#             showcoastlines=True,
#             projection_type='equirectangular'
#         )
#     )
    
#     return fig

# def create_ewaste_map(df):
#     """
#     Create a choropleth map showing e-waste generation by country
#     """
#     # Filter for the most recent year if there are multiple years
#     if 'year' in df.columns and not df.empty:
#         latest_year = df['year'].max()
#         df_latest = df[df['year'] == latest_year]
#     else:
#         df_latest = df
    
#     # Add debugging output
#     print(f"Creating map with {len(df_latest)} countries for year {latest_year}")
    
#     fig = px.choropleth(
#         df_latest,
#         locations='country',       # Column containing ISO-3 country codes
#         locationmode='ISO-3',
#         color='value',            # Column for color intensity
#         hover_name='country',     # Column for hover labels
#         hover_data=['measure', 'unit', 'category'],
#         title=f'E-Waste Data by Country ({latest_year if "year" in df.columns else "Latest Data"})',
#         color_continuous_scale='Reds',
#         labels={'value': 'Value'}
#     )
    
#     fig.update_layout(
#         geo=dict(
#             showframe=False,
#             showcoastlines=True,
#             projection_type='equirectangular'
#         )
#     )
    
#     return fig

# @app.route('/debug_api')
# def debug_api():
#     """
#     Debug endpoint to view the raw XML data
#     """
#     raw_data = fetch_oecd_data()
#     if isinstance(raw_data, dict) and "error" in raw_data:
#         return jsonify(raw_data)
    
#     # If it's XML data, return it as text with XML content type
#     return raw_data, 200, {'Content-Type': 'application/xml'}

# if __name__ == '__main__':
#     app.run(debug=True)


import requests
from flask import Flask, render_template, jsonify, request
import pandas as pd
import plotly
import plotly.express as px
import json
import xml.etree.ElementTree as ET


app = Flask(__name__)


def fetch_oecd_data():
   url = "https://sdmx.oecd.org/public/rest/data/OECD.ENV.EPI,DSD_EWASTE@DF_EWASTE,1.0/AUS.A..T.GEN?startPeriod=2010&dimensionAtObservation=AllDimensions"
   response = requests.get(url)
   if response.status_code == 200:
       return response.text
   else:
       print(f"Error fetching data: {response.status_code}")
       return {"error": f"Failed to fetch data: {response.status_code}"}


def process_oecd_data(xml_data):
   """
   Process the XML data from OECD API into a pandas DataFrame
   """
   try:
       namespaces = {
           'message': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message',
           'generic': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic',
           'common': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common'
       }


       if isinstance(xml_data, dict) and "error" in xml_data:
           return pd.DataFrame()


       root = ET.fromstring(xml_data)


       countries = []
       years = []
       values = []
       units = []
       measures = []
       categories = []


       observations = root.findall('.//generic:Obs', namespaces)


       for obs in observations:
           obs_key = obs.find('./generic:ObsKey', namespaces)


           country = None
           year = None
           value = None
           unit = None
           measure = None
           category = None


           for key_value in obs_key.findall('./generic:Value', namespaces):
               id_attr = key_value.get('id')
               value_attr = key_value.get('value')


               if id_attr == 'TIME_PERIOD':
                   year = value_attr
               elif id_attr == 'REF_AREA':
                   country = value_attr
               elif id_attr == 'UNIT_MEASURE':
                   unit = value_attr
               elif id_attr == 'MEASURE':
                   measure = value_attr
               elif id_attr == 'PRODUCT_CATEGORIES':
                   category = value_attr


           obs_value = obs.find('./generic:ObsValue', namespaces)
           if obs_value is not None:
               value = float(obs_value.get('value'))


               countries.append(country)
               years.append(int(year))
               values.append(value)
               units.append(unit)
               measures.append(measure)
               categories.append(category)


       df = pd.DataFrame({
           'country': countries,
           'year': years,
           'value': values,
           'unit': units,
           'measure': measures,
           'category': categories
       })


       print(f"Processed data: {len(df)} records found")
       return df


   except Exception as e:
       print(f"Error processing OECD data: {e}")
       return pd.DataFrame(columns=['country', 'year', 'value', 'unit', 'measure', 'category'])


def load_policy_data():
   df = pd.read_csv('data/policies.csv')
   return df


@app.route('/')
def index():
   data_types = ['policy', 'ewaste']
   return render_template('index.html', data_types=data_types)


@app.route('/get_data')
def get_data():
   data_type = request.args.get("data_type", "policy")


   try:
       if data_type == "policy":
           df = load_policy_data()
           fig = create_policy_map(df)
       else:
           raw_data = fetch_oecd_data()
           if isinstance(raw_data, dict) and "error" in raw_data:
               return jsonify({"error": raw_data["error"]})
           ewaste_df = process_oecd_data(raw_data)
           if ewaste_df.empty:
               return jsonify({"error": "No data available"})
           fig = create_ewaste_map(ewaste_df)


       graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
       return jsonify(graphJSON)
   except Exception as e:
       print(f"Error processing data: {e}")
       return jsonify({"error": f"Error processing data: {str(e)}"})


def create_policy_map(df):
   """
   Create a choropleth map showing policy data by country
   """
   fig = px.choropleth(
       df,
       locations='country_code',
       color='policy_score',
       hover_name='country',
       title='E-Waste Policies by Country',
       color_continuous_scale='Viridis',
       labels={'policy_score': 'Policy Score'}
   )


   fig.update_layout(
       geo=dict(
           showframe=False,
           showcoastlines=True,
           projection_type='equirectangular'
       )
   )


   return fig


def create_ewaste_map(df):
   """
   Create a choropleth map showing e-waste generation by country
   """
   if 'year' in df.columns and not df.empty:
       latest_year = df['year'].max()
       df_latest = df[df['year'] == latest_year]
   else:
       df_latest = df


   print(f"Creating map with {len(df_latest)} countries for year {latest_year}")


   fig = px.choropleth(
       df_latest,
       locations='country',
       locationmode='ISO-3',
       color='value',
       hover_name='country',
       hover_data=['measure', 'unit', 'category'],
       title=f'E-Waste Data by Country ({latest_year if "year" in df.columns else "Latest Data"})',
       color_continuous_scale='Reds',
       labels={'value': 'Value'}
   )


   fig.update_layout(
       geo=dict(
           showframe=False,
           showcoastlines=True,
           projection_type='equirectangular'
       )
   )


   return fig


@app.route('/debug_api')
def debug_api():
   """
   Debug endpoint to view the raw XML data
   """
   raw_data = fetch_oecd_data()
   if isinstance(raw_data, dict) and "error" in raw_data:
       return jsonify(raw_data)


   return raw_data, 200, {'Content-Type': 'application/xml'}


if __name__ == '__main__':
   app.run(debug=True)