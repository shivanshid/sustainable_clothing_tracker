# import requests
# from flask import Flask, render_template, jsonify, request
# import pandas as pd
# import plotly
# import plotly.express as px
# import json
# import xml.etree.ElementTree as ET
# import pycountry


# app = Flask(__name__)


# # Dictionary to convert country codes to full names
# def get_country_name(alpha3):
#    try:
#        return pycountry.countries.get(alpha_3=alpha3).name
#    except (AttributeError, KeyError):
#        return alpha3  # Return the code if no match


# def fetch_oecd_data():
#    """Fetch e-waste data from OECD API"""
#    # Modified URL to get more countries for better visualization
# #    url = "https://sdmx.oecd.org/public/rest/data/OECD.ENV.EPI,DSD_EWASTE@DF_EWASTE,1.0/.A..T.?startPeriod=2015&dimensionAtObservation=AllDimensions"
#    url = "https://sdmx.oecd.org/public/rest/data/OECD.ENV.EPI,DSD_EWASTE@DF_EWASTE,1.0//.A..T.GEN?startPeriod=2010&dimensionAtObservation=AllDimensions"

  
#    try:
#        response = requests.get(url, timeout=10)
#        response.raise_for_status()  # Raise exception for HTTP errors
#        return response.text
#    except requests.exceptions.RequestException as e:
#        print(f"Error fetching data: {e}")
#        return {"error": f"Failed to fetch data: {str(e)}"}


# def process_oecd_data(xml_data):
#    """Process XML data from OECD API into a DataFrame"""
#    try:
#        # Return early if there was an error fetching data
#        if isinstance(xml_data, dict) and "error" in xml_data:
#            return pd.DataFrame(), xml_data["error"]
          
#        # Define namespaces used in the XML
#        namespaces = {
#            'message': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message',
#            'generic': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic',
#            'common': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common'
#        }
      
#        # Parse XML
#        root = ET.fromstring(xml_data)
      
#        # Lists to store data
#        data_rows = []
      
#        # Find all observation elements
#        observations = root.findall('.//generic:Obs', namespaces)
#        print(f"Found {len(observations)} observations in XML")
      
#        for obs in observations:
#            # Extract data from each observation
#            obs_key = obs.find('./generic:ObsKey', namespaces)
          
#            # Initialize data row
#            data_row = {}
          
#            # Get values from ObsKey
#            for key_value in obs_key.findall('./generic:Value', namespaces):
#                id_attr = key_value.get('id')
#                value_attr = key_value.get('value')
              
#                if id_attr == 'TIME_PERIOD':
#                    data_row['year'] = int(value_attr)
#                elif id_attr == 'REF_AREA':
#                    data_row['country_code'] = value_attr
#                    data_row['country_name'] = get_country_name(value_attr)
#                elif id_attr == 'UNIT_MEASURE':
#                    data_row['unit'] = value_attr
#                elif id_attr == 'MEASURE':
#                    data_row['measure'] = value_attr
#                elif id_attr == 'PRODUCT_CATEGORIES':
#                    data_row['category'] = value_attr
#                elif id_attr == 'FREQ':
#                    data_row['frequency'] = value_attr
          
#            # Get observation value
#            obs_value = obs.find('./generic:ObsValue', namespaces)
#            if obs_value is not None:
#                data_row['value'] = float(obs_value.get('value'))
              
#                # Get unit multiplier from attributes
#                attributes = obs.find('./generic:Attributes', namespaces)
#                if attributes is not None:
#                    for attr in attributes.findall('./generic:Value', namespaces):
#                        if attr.get('id') == 'UNIT_MULT':
#                            mult = int(attr.get('value'))
#                            # Apply multiplier (e.g., 3 means *1000)
#                            data_row['value'] = data_row['value'] * (10 ** mult)
              
#                # Add complete row to our data
#                data_rows.append(data_row)
      
#        # Create DataFrame
#        df = pd.DataFrame(data_rows)
      
#        if df.empty:
#            return df, "No data found in the XML response"
          
#        # Add descriptive labels based on measure codes
#        measure_labels = {
#            'GEN': 'Generation',
#            'COL': 'Collection',
#            'RCY': 'Recycling',
#            'EXP': 'Export'
#        }
      
#        df['measure_label'] = df['measure'].map(measure_labels)
      
#        print(f"Processed data: {len(df)} records with {df['country_code'].nunique()} countries")
#        return df, None
  
#    except Exception as e:
#        print(f"Error processing OECD data: {e}")
#        # Return empty DataFrame and error message
#        return pd.DataFrame(), f"Error processing data: {str(e)}"


# def load_policy_data():
#    try:
#        df = pd.read_csv('data/policies.csv')
#        df = df.rename(columns={
#            'Country': 'country_name',
#            'ISO_Code': 'country_code',
#            'Policy_Index': 'policy_score'
#        })
#        return df, None
#    except Exception as e:
#        return pd.DataFrame(), f"Error loading policy data: {str(e)}"


# @app.route('/')
# def index():
#    data_types = ['policy', 'ewaste']
#    measure_types = ['GEN', 'COL', 'RCY', 'EXP']
#    years = list(range(2015, 2023))  # Add appropriate years
  
#    return render_template('index.html', data_types=data_types, measure_types=measure_types, years=years)


# @app.route('/get_data')
# def get_data():
#    # Get parameters from request
#    data_type = request.args.get("data_type", "policy")
#    measure_type = request.args.get("measure_type", "GEN")
#    year = request.args.get("year", "2021")
  
#    try:
#        year = int(year)
#    except ValueError:
#        year = 2021  # Default if invalid
  
#    try:
#        if data_type == "policy":
#            df, error = load_policy_data()
#            if error:
#                return jsonify({"error": error})
#            fig = create_policy_map(df)
#        else:  # ewaste
#            raw_data = fetch_oecd_data()
#            if isinstance(raw_data, dict) and "error" in raw_data:
#                return jsonify({"error": raw_data["error"]})
              
#            ewaste_df, error = process_oecd_data(raw_data)
#            if error:
#                return jsonify({"error": error})
              
#            if ewaste_df.empty:
#                return jsonify({"error": "No data available"})
              
#            # Filter by measure type and year
#            filtered_df = ewaste_df[
#                (ewaste_df['measure'] == measure_type) &
#                (ewaste_df['year'] == year)
#            ]
          
#            if filtered_df.empty:
#                return jsonify({"error": f"No data available for {measure_type} in {year}"})
              
#            fig = create_ewaste_map(filtered_df, measure_type, year)
      
#        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
#        return jsonify(graphJSON)
#    except Exception as e:
#        print(f"Error processing data: {e}")
#        return jsonify({"error": f"Error processing data: {str(e)}"})


# def create_policy_map(df):
#    """Create a choropleth map showing policy data by country"""
#    fig = px.choropleth(
#        df,
#        locations='country_code',
#        color='policy_score',
#        hover_name='country_name',
#        title='E-Waste Policies by Country',
#        color_continuous_scale='Viridis',
#        labels={'policy_score': 'Policy Score'}
#    )
  
#    fig.update_layout(
#        geo=dict(
#            showframe=False,
#            showcoastlines=True,
#            projection_type='equirectangular'
#        ),
#        margin={"r":0,"t":50,"l":0,"b":0}
#    )
  
#    return fig


# def create_ewaste_map(df, measure_type, year):
#    """Create a choropleth map showing e-waste data by country"""
#    measure_titles = {
#        'GEN': 'E-Waste Generation',
#        'COL': 'E-Waste Collection',
#        'RCY': 'E-Waste Recycling',
#        'EXP': 'E-Waste Export'
#    }
  
#    # Choose appropriate color scale based on measure
#    color_scales = {
#        'GEN': 'Reds',
#        'COL': 'Greens',
#        'RCY': 'Blues',
#        'EXP': 'Purples'
#    }
  
#    # Get appropriate hover data
#    hover_data = ['value', 'unit', 'category']
  
#    title = f"{measure_titles.get(measure_type, 'E-Waste Data')} by Country ({year})"
  
#    fig = px.choropleth(
#        df,
#        locations='country_code',
#        locationmode='ISO-3',
#        color='value',
#        hover_name='country_name',
#        hover_data=hover_data,
#        title=title,
#        color_continuous_scale=color_scales.get(measure_type, 'Reds'),
#        labels={'value': 'Value'}
#    )
  
#    fig.update_layout(
#        geo=dict(
#            showframe=False,
#            showcoastlines=True,
#            projection_type='equirectangular',
#            showland=True,
#            landcolor='lightgray',
#        ),
#        margin={"r":0,"t":50,"l":0,"b":0}
#    )
  
#    return fig


# @app.route('/debug_api')
# def debug_api():
#    """Debug endpoint to view the raw XML data"""
#    raw_data = fetch_oecd_data()
#    if isinstance(raw_data, dict) and "error" in raw_data:
#        return jsonify(raw_data)
  
#    # Sample of the XML data (first 1000 chars)
#    sample = raw_data[:1000] + "..." if len(raw_data) > 1000 else raw_data
  
#    # Return a readable debug page
#    html = f"""
#    <html>
#    <head><title>API Debug</title></head>
#    <body>
#        <h1>API Response Sample</h1>
#        <pre>{sample}</pre>
#        <h2>Process Data</h2>
#        <a href="/debug_processed">View Processed Data</a>
#    </body>
#    </html>
#    """
#    return html


# @app.route('/debug_processed')
# def debug_processed():
#    """Debug endpoint to view the processed data"""
#    raw_data = fetch_oecd_data()
#    if isinstance(raw_data, dict) and "error" in raw_data:
#        return jsonify(raw_data)
      
#    df, error = process_oecd_data(raw_data)
#    if error:
#        return f"Error: {error}"
      
#    # Display as HTML table
#    table_html = df.to_html(classes='table table-striped', index=False)
  
#    html = f"""
#    <html>
#    <head>
#        <title>Processed Data</title>
#        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
#    </head>
#    <body>
#        <div class="container mt-4">
#            <h1>Processed OECD Data</h1>
#            <p>Found {len(df)} records with {df['country_code'].nunique()} countries.</p>
#            {table_html}
#        </div>
#    </body>
#    </html>
#    """
#    return html


# @app.route('/chatbot')
# def chatbot():
#    """Render the chatbot page"""
#    return render_template('chatbot.html')


# @app.route('/api/chat', methods=['POST'])
# def process_chat():
#    """Process chat messages and return AI responses"""
#    data = request.json
#    user_message = data.get('message', '')
  
#    if not user_message:
#        return jsonify({"error": "No message provided"})
  
#    try:
#        # Configure your API request
#        url = "https://chat-gpt26.p.rapidapi.com/"
      
#        # Add context about e-waste and environmental implications
#        prompt_context = "You are an expert on environmental impacts of technology, especially " \
#                         "e-waste management and AI's environmental footprint. Answer questions " \
#                         "about environmental policies, sustainability in tech, and e-waste management."
      
#        # Build the full message array with context
#        messages = [
#            {"role": "system", "content": prompt_context},
#            {"role": "user", "content": user_message}
#        ]
      
#        payload = {
#            "model": "gpt-3.5-turbo",
#            "messages": messages
#        }
      
#        headers = {
#            "x-rapidapi-key": "230d408ce9msh618b3867aa2fd58p17f418jsn4521e0840677",  # Replace with your actual API key
#            "x-rapidapi-host": "chat-gpt26.p.rapidapi.com",
#            "Content-Type": "application/json"
#        }
      
#        response = requests.post(url, json=payload, headers=headers)
#        response_data = response.json()
      
#        # Extract the AI's response from the API response
#        ai_response = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
      
#        if not ai_response:
#            return jsonify({"error": "Failed to get response from AI"})
          
#        return jsonify({"response": ai_response})
      
#    except Exception as e:
#        print(f"Chat API error: {str(e)}")
#        return jsonify({"error": f"Failed to process request: {str(e)}"})


# if __name__ == '__main__':
#    app.run(debug=True)



# ________________________________________________________________________
from flask import Flask, request, jsonify, render_template
import requests
import pandas as pd
import plotly
import plotly.express as px
import json
import xml.etree.ElementTree as ET


app = Flask(__name__)


# =============================
# Serve HTML pages
# =============================
@app.route("/")
def home():
   return render_template("home.html")


@app.route("/map")
def map_page():
   return render_template("map.html", data_types=["ewaste"], years=list(range(2015, 2025)))


@app.route("/chatbot")
def chatbot_page():
   return render_template("chatbot.html")


@app.route("/how-to-help")
def how_to_help():
   return render_template("how_to_help.html")


@app.route("/contact")
def contact():
   return render_template("contact.html")


# =============================
# Chatbot API Endpoint
# =============================
@app.route('/api/chat', methods=['POST'])
def process_chat():
   """Process chat messages and return AI responses"""
   data = request.json
   user_message = data.get('message', '')
  
   if not user_message:
       return jsonify({"error": "No message provided"})
  
   try:
       # Configure your API request
       url = "https://chat-gpt26.p.rapidapi.com/"
      
       # Add context about e-waste and environmental implications
       prompt_context = "You are an expert on environmental impacts of technology, especially " \
                        "e-waste management and AI's environmental footprint. Answer questions " \
                        "about environmental policies, sustainability in tech, and e-waste management."
      
       # Build the full message array with context
       messages = [
           {"role": "system", "content": prompt_context},
           {"role": "user", "content": user_message}
       ]
      
       payload = {
           "model": "gpt-3.5-turbo",
           "messages": messages
       }
      
       headers = {
           "x-rapidapi-key": "230d408ce9msh618b3867aa2fd58p17f418jsn4521e0840677",  # Replace with your actual API key
           "x-rapidapi-host": "chat-gpt26.p.rapidapi.com",
           "Content-Type": "application/json"
       }
      
       response = requests.post(url, json=payload, headers=headers)
       response_data = response.json()
      
       # Extract the AI's response from the API response
       ai_response = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
      
       if not ai_response:
           return jsonify({"error": "Failed to get response from AI"})
          
       return jsonify({"response": ai_response})
      
   except Exception as e:
       print(f"Chat API error: {str(e)}")
       return jsonify({"error": f"Failed to process request: {str(e)}"})


# =============================
# Data & Map API Endpoint
# =============================
def fetch_oecd_data():
   url = "https://sdmx.oecd.org/public/rest/data/OECD.ENV.EPI,DSD_EWASTE@DF_EWASTE,1.0/.A..T.GEN?startPeriod=2010&dimensionAtObservation=AllDimensions"
   response = requests.get(url)
   if response.status_code == 200:
       return response.text
   else:
       print(f"Error fetching data: {response.status_code}")
       return {"error": f"Failed to fetch data: {response.status_code}"}


def process_oecd_data(xml_data):
   namespaces = {
       'message': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message',
       'generic': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic',
       'common': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common'
   }


   if isinstance(xml_data, dict) and "error" in xml_data:
       return pd.DataFrame()


   try:
       root = ET.fromstring(xml_data)
       countries, years, values, units, measures, categories = [], [], [], [], [], []


       observations = root.findall('.//generic:Obs', namespaces)
       for obs in observations:
           obs_key = obs.find('./generic:ObsKey', namespaces)


           country = year = unit = measure = category = None
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


       return pd.DataFrame({
           'country': countries,
           'year': years,
           'value': values,
           'unit': units,
           'measure': measures,
           'category': categories
       })


   except Exception as e:
       print(f"Error processing OECD data: {e}")
       return pd.DataFrame()




def load_policy_data():
   return pd.read_csv('data/policies.csv')




def create_policy_map(df):
   fig = px.choropleth(
       df,
       locations='country_code',
       color='policy_score',
       hover_name='country',
       title='E-Waste Policies by Country',
       color_continuous_scale='Viridis',
       labels={'policy_score': 'Policy Score'}
   )
   fig.update_layout(geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular'))
   return fig




def create_ewaste_map(df):
   if 'year' in df.columns and not df.empty:
       latest_year = df['year'].max()
       df_latest = df[df['year'] == latest_year]
   else:
       df_latest = df


   fig = px.choropleth(
       df_latest,
       locations='country',
       locationmode='ISO-3',
       color='value',
       hover_name='country',
       hover_data=['measure', 'unit', 'category'],
       title=f'E-Waste Data by Country ({latest_year})',
       color_continuous_scale='Reds',
       labels={'value': 'Value'}
   )
   fig.update_layout(geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular'))
   return fig


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


@app.route('/debug_api')
def debug_api():
   raw_data = fetch_oecd_data()
   if isinstance(raw_data, dict) and "error" in raw_data:
       return jsonify(raw_data)
   return raw_data, 200, {'Content-Type': 'application/xml'}


# =============================
# Run the app
# =============================
if __name__ == "__main__":
   app.run(debug=True)
