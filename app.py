from flask import Flask,render_template,request,jsonify
import requests
import re
import time
from decimal import Decimal

app = Flask(__name__)

import math

def haversine_distance(lat1, lon1, lat2, lon2):
    # Radius of Earth in kilometers
    R = 6371.0

    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Differences in coordinates
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c  # Distance in kilometers

    return distance

def populatearr(data,places,api_key,pagecount):
    nextpage = data['next_page_token']
    print(f"Fetching next page...")
    print("\nPAGE COUNTTTT:"+str(pagecount))
    time.sleep(2)
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
def sortarr(place,prefval,selected,arrix,preftype):
    # print(f"rating:{rating}\n")
    print(preftype)
    selected.append(place)
    # # if(arrix>0):
    # #     if(preftype=="rating"):
    # #         print("here")
    # #         print("for this:", selected[arrix-1].get('rating',0),">",str(prefval))
    # #         selected=sorted(selected, key=lambda x: x["rating"])

                
    # #     elif(preftype=="holrating"):
    # #         selected.sort(key=lambda x: x['holrating'])
    # arrix+=1
    # print("arrix",arrix)
    # return arrix
api_key="AIzaSyAezb9x0qjZcBVrNv86APb7Yh9b6-M51V8"

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
    params = {
        'location': f"{latitude},{longitude}",
        'rankby':'distance',
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
            while 'next_page_token' in data and pagecount<2:
                populatearr(data,places,api_key,pagecount)
                pagecount+=1
            selected=[]
            arrix=0
            sorting=request.form['sortby']
            print("sorting")

            for place in places:
                print(place['name'])
            arrix=0
            if(sorting=="absolute_rating"):
                for place in places:
                    rating=place.get('rating', '0')
                    place['holrating']=rating
                    selected.append(place)
                    arrix+=1
                selected = sorted(selected, key=lambda x: x.get('rating',0),reverse=True)
                    # arrix=sortarr(place,rating,selected,arrix,"rating")
                # selected=sorted(selected,key=lambda x:x["rating"])
            elif(sorting=="recommended"): 
                priority=request.form["priority"]
                if(priority=="distance"):
                    distance_weight=6
                    rating_weight=4
                elif(priority=="rating"):
                    distance_weight=4
                    rating_weight=6

                    
                arrix=0
                for place in places:
                    rating=place.get('rating','0')
                    latitude2 = place.get("geometry", {}).get("location", {}).get("lat",latitude)    
                    longitude2= place.get("geometry", {}).get("location", {}).get("lng",longitude)
                    try:
                        latitude2 = Decimal(latitude2)
                        longitude2 = Decimal(longitude2)
                    except Exception as e:
                        return("Invalid location data")
                    distance=haversine_distance(latitude,longitude,latitude2,longitude2)
                    holrating=(float(rating)/5*rating_weight)+(distance/10*distance_weight)
                    place['holrating']=round(float(holrating),2)
                    selected.append(place)
                    arrix+=1
                    selected = sorted(selected, key=lambda x: x.get('holrating',0),reverse=True)
            return render_template('results.html', places=selected)
        except Exception as e:
            return f"Error parsing API response: {e}"
    else:
        return f"Error: {response.status_code}"
    

if __name__ == '__main__':
    app.run(debug=True)