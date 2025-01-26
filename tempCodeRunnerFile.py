@app.route('/submit',methods=['POST'])
def submit():
    url=request.form['location']
    latitude,longitude=tolocation(url)
    return render_template('results.html',latitude=latitude,longitude=longitude)