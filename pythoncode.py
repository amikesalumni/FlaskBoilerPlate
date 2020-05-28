from flask import Flask, Response, render_template, request
import webbrowser

import NH3TPD as NH3


app = Flask(__name__)

# to publish changes to github
# git add file
# git commit -m "describe changes you are making" .
# git push
# make sure to ctrl shift R to get rid of cached website

# Proton_count inputs
#mass_loaded = float(request.form["SM"]) # grams, ML
#TGA_loss = 0 # entered as a percent, TL
#response_factor = float(request.form["RF"]) # changes frequently, RF for old 3184 is 2.36E-4, for new 3184 is 1.05e-4, 31.44 for 3150
#moles_Ar = float(request.form["MA"]) # MA, for the 3184 unit set this to 1 as it's included in the listed RF, set to 1.59E-05 in 3150
#area_ratio = result[2] # AR
#Si_Al = float(request.form["SA"])# Si/Al
#protons = round(Proton_count(mass_loaded, TGA_loss, response_factor, moles_Ar, area_ratio, Si_Al),3)

# csv = '1,2,3\n4,5,6\n' #put csv file here
# response method for gettting text to update on webpage
#Response(str(protons), content_type='text/plain')

@app.route('/')
def webpage():
    return render_template('index.html')

@app.route('/fileupload', methods=['POST'])
def myFunc():
    # file request
    data = request.files['file']
    return 'file uploaded'    

@app.route('/plot', methods=['POST'])
def plot():
    # grab file
    data = request.files['file']

    # TPD Analyzer inputs
    TPD_start_time = int(request.form["TPDs"])
    TPD_end_time = int(request.form["TPDe"])
    Ar_start_time = int(request.form["Ars"])
    Ar_end_time = int(request.form["Are"])
    water_fraction = float(request.form["wf"])
    result = NH3.TPD_analyze(data,TPD_start_time,TPD_end_time,Ar_start_time,Ar_end_time,water_fraction)

    nth = 20 # grab every nth point, need to add this as an input at somepoint
    plots_return = NH3.Plots(result, nth)
    chart_list = ('{} {} {} {} {}'.format(plots_return[0].to_json(),plots_return[1].to_json(),plots_return[2].to_json(),plots_return[3].to_json(),plots_return[4].to_json()))
    return chart_list

@app.route('/calculate', methods=['POST'])
def calculate():
    # fetch inputs
    data = request.files['file']
    TPD_start_time = int(request.form["TPDs"])
    TPD_end_time = TPD_start_time + 90
    Ar_start_time = int(request.form["Ars"])
    Ar_end_time = int(request.form["Are"])
    water_fraction = float(request.form["wf"])
    result = NH3.TPD_analyze(data,TPD_start_time,TPD_end_time,Ar_start_time,Ar_end_time,water_fraction)

    # protons input
    mass_loaded = float(request.form["SM"]) # grams, ML
    TGA_loss = 0 # entered as a percent, TL
    response_factor = float(request.form["RF"]) # changes frequently, RF for old 3184 is 2.36E-4, for new 3184 is 1.05e-4, 31.44 for 3150
    moles_Ar = float(request.form["MA"]) # MA, for the 3184 unit set this to 1 as it's included in the listed RF, set to 1.59E-05 in 3150
    area_ratio = result[2] # AR
    Si_Al = float(request.form["SA"])# Si/Al
    protons = round(NH3.CHA_H_count(mass_loaded, response_factor, moles_Ar, area_ratio, Si_Al),3)
    response = Response(str(protons), content_type='text/plain')
    return response

if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:5000/', new=2)
    app.run()