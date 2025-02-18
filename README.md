A Flask-based web application that retrieves nearby places using the Google Maps Places API. Given a location link, the app fetches relevant places within a defined parameter and sorts them based on rating, distance, and a weighted recommendation system.
Features:
- Retrieves nearby places based on a given location.
- Sorting options:
  - *By Rating* – Displays places with the highest ratings first.
  - *By Distance* – Lists places closest to the given location.
  - *By Recommendation* – Uses a weighted system to suggest the best options.
- Simple and efficient backend built with Flask.
- Uses Google Maps APIs for precise location-based results.
Installation:
1. Clone the repository
2. Set up a virtual environment (optional but recommended)
3. Install dependencies
4. Set up your Google Maps API Key:
   - Obtain an API key from [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the Places API (new)
Usage:

1. Run the Flask application
2. Open `http://127.0.0.1:5000/` in your browser.
3. Enter a location link and retrieve nearby places.

## API Endpoints

- `GET /` - Home page with input form.
- `POST /search` - Fetches and displays sorted places.

Contributions are welcome! 
