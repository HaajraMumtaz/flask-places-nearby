from flask import Flask,render_template,request,jsonify
import requests
import re
import time
from decimal import Decimal
from dotenv import load_dotenv
import os
import math
app = Flask(__name__)

load_dotenv()  # Load variables from .env
api_key = os.getenv("API_KEY")

def remove_duplicates(places):
    seen_names = set()
    unique_places = []

    for place in places:
        if place['name'] not in seen_names and ("mall" and "Mall" not in place['name']):
            unique_places.append(place)
            seen_names.add(place['name'])

    return unique_places


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0

    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    lon1_rad = math.radians(lon1)
    lon2_rad = math.radians(lon2)

    # Differences in coordinates
    x = (lon2_rad - lon1_rad) * math.cos((lat1_rad + lat2_rad) / 2)
    y = lat2_rad - lat1_rad

    # Distance using the flat Earth formula
    distance = math.sqrt(x**2 + y**2) * R

    return distance

def populatearr(data,places,api_key,pagecount):
    nextpage = data['next_page_token']
    print(f"Fetching next page...")
    print("\nPAGE COUNTTTT:"+str(pagecount))
    time.sleep(1)
    params={'pagetoken':nextpage,'key':api_key}
    # print("success 1")
    response = requests.get(ep, params=params)
    data = response.json()
    # print("success 2")
    if data.get('status') == 'OK':
    # print("success")
        places.extend(data['results'])
    else:
        print(f"Error: {data.get('status')}")
def tolocation(url):
    pattern = r"@([^,]+),([^,]+)"
    match = re.search(pattern, url)
    if match:
        latitude = match.group(1)
        longitude = match.group(2)
    else:
        latitude = longitude = -1
    return latitude, longitude
ep = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    pagecount=1
    print("here")
    url = request.form['location']
    radius = int(request.form['radius'])
    typeloc = request.form['typeloc']
    
    latitude, longitude = tolocation(url)
    # Prepare API request parameters
    try:
        latitude = Decimal(latitude)
        longitude = Decimal(longitude)
    except Exception as e:
        return("Invalid location data")
    sorting=request.form['sortby']
    if(sorting=="distance" ):
        params = {
                'location': f"{latitude},{longitude}",
                'key': api_key,
                'type':typeloc,
                'radius':radius*1000
                }
            
    elif(sorting=="absolute_rating" or (sorting=="recomended" and request.form["priority"]=="rating")):
            params = {
                'location': f"{latitude},{longitude}",
                'radius':radius*1000,
                'key': api_key,
                'type':typeloc,
                'rankby':"prominence"}
                    
    else:
            params = {
                'location': f"{latitude},{longitude}",
                'radius':radius*1000,
                'key': api_key,
                'type':typeloc
                }


    print("location:"+ str(f"{latitude},{longitude}"))
    response = requests.get(ep, params=params)
    if response.status_code == 200:
        try:
            pagecount=0
            print("success")
            data = response.json()
            places = data.get('results', [])   
            while 'next_page_token' in data and pagecount<7:
                populatearr(data,places,api_key,pagecount)
                pagecount+=1
            selected=[]
            arrix=0
            print("sorting") 

            arrix=0
            if(sorting=="absolute_rating"): #if sorting is through rating
                for place in places:
                    if(int(place.get('user_ratings_total'))>=40):
                            latitude2 = place.get("geometry", {}).get("location", {}).get("lat",latitude)    
                            longitude2= place.get("geometry", {}).get("location", {}).get("lng",longitude)
                            try:
                                latitude2 = Decimal(latitude2)
                                longitude2 = Decimal(longitude2)
                            except Exception as e:
                                return("Invalid location data")
                            place['distance']=haversine_distance(latitude,longitude,latitude2,longitude2)
                            rating=place.get('rating', '0')
                            place['holrating']=rating
                            selected.append(place)
                            arrix+=1
                    for place in selected:
                        print(place['name'],"------")
                    selected = sorted(selected, key=lambda x: x.get('rating',0),reverse=True)
                    
            
            elif(sorting=="recommended"): #if sorting through holisic rating
                    priority=request.form["priority"]
                    if(priority=="distance"):#setting up priority wise weights
                        distance_weight=7
                        rating_weight=3
                    elif(priority=="rating"):
                        distance_weight=3
                        rating_weight=7

                        
                    arrix=0
                    for place in places:
                        if(int(place.get('user_ratings_total'))>=35):
                            rating=place.get('rating','0')
                            latitude2 = place.get("geometry", {}).get("location", {}).get("lat",latitude)    
                            longitude2= place.get("geometry", {}).get("location", {}).get("lng",longitude)
                            try:
                                latitude2 = Decimal(latitude2)
                                longitude2 = Decimal(longitude2)
                            except Exception as e:
                                return("Invalid location data")
                            distance=haversine_distance(latitude,longitude,latitude2,longitude2)
                            print("distance of",place['name'],distance)
                            holrating=((float(rating)/5*rating_weight)+(distance/10*distance_weight))/10*5
                            place['holrating']=round(float(holrating),2)
                            place['distance']=haversine_distance(latitude,longitude,latitude2,longitude2)
                            selected.append(place)
                            arrix+=1
                    selected = sorted(selected, key=lambda x: x.get('holrating',0),reverse=True)
            else:
                for place in places:
                        if(int(place.get('user_ratings_total',0))>=35):
                            latitude2 = place.get("geometry", {}).get("location", {}).get("lat",latitude)    
                            longitude2= place.get("geometry", {}).get("location", {}).get("lng",longitude)
                            try:
                                latitude2 = Decimal(latitude2)
                                longitude2 = Decimal(longitude2)
                            except Exception as e:
                                return("Invalid location data")
                            distance=haversine_distance(latitude,longitude,latitude2,longitude2)
                            place['holrating']=place.get('rating',0)
                            place['distance']=haversine_distance(latitude,longitude,latitude2,longitude2)
                            if (place['distance'])<=float(request.form['radius']):
                                selected.append(place)
                selected = sorted(selected, key=lambda x: x.get('distance',0),reverse=True)

            Unique=remove_duplicates(selected)
            for place in Unique:
                print(place,"--------")
            return render_template('results.html', places=Unique)
        except Exception as e:
            return f"Error parsing API response: {e}"
    else:
        return f"Error: {response.status_code}"
    

if __name__ == '__main__':
    app.run(debug=True)