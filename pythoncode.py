from flask import Flask, Response, render_template, request, session
from flask_session import Session

import webbrowser

import NH3TPD as NH3



app = Flask(__name__)
# This should start a session for each user that then later lets them set a unique working directory for their session
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

# to publish changes to github
# git add file
# git commit -m "describe changes you are making" .
# git push
# make sure to ctrl shift R to get rid of cached website

@app.route('/')
def webpage():
    return render_template('index.html')

@app.route('/fileupload', methods=['POST'])
def myFunc():
    # store the name of the file
    session["storedfile"] = request.files['file'].filename
    return 'file uploaded'    

@app.route('/plot', methods=['POST'])
def plot():
    # TPD Analyzer inputs
    TPD_start_time = int(request.form["TPDs"])
    TPD_end_time = int(request.form["TPDe"])
    Ar_start_time = int(request.form["Ars"])
    Ar_end_time = int(request.form["Are"])
    water_fraction = float(request.form["wf"])
    session["result"] = NH3.TPD_analyze(session["storedfile"],TPD_start_time,TPD_end_time,Ar_start_time,Ar_end_time,water_fraction)

    nth = 20 # grab every nth point, need to add this as an input at somepoint
    plots_return = NH3.Plots(session["result"], nth)
    chart_list = ('{} {} {} {} {}'.format(plots_return[0].to_json(),plots_return[1].to_json(),plots_return[2].to_json(),plots_return[3].to_json(),plots_return[4].to_json()))
    return chart_list

@app.route('/calculate', methods=['POST'])
def calculate():
    # protons input
    mass_loaded = float(request.form["SM"]) # grams, ML
    response_factor = float(request.form["RF"]) # changes frequently, RF for old 3184 is 2.36E-4, for new 3184 is 1.05e-4, 31.44 for 3150
    moles_Ar = float(request.form["MA"]) # MA, for the 3184 unit set this to 1 as it's included in the listed RF, set to 1.59E-05 in 3150
    area_ratio = session["result"][2] # AR
    Si_Al = float(request.form["SA"])# Si/Al
    protons = round(NH3.CHA_H_count(mass_loaded, response_factor, moles_Ar, area_ratio, Si_Al),3)
    response = Response(str(protons), content_type='text/plain')
    return response
