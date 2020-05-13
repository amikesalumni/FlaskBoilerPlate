from flask import Flask, Response, render_template, request
import webbrowser

import numpy as np
import scipy.integrate as integrate
import pandas as pd


app = Flask(__name__)

def TPD_analyze(fn, TPDs, TPDe, Ars, Are, wf):
    # read the data in, requires some modification when dealing with weird csv's
    data = pd.read_csv(fn, header=2,dtype='a',names=['time','intensity'],index_col=False)
    
    # grab the column labels, used to assign the columns to the different m/z values
    theader = data.columns.tolist()[0]
    yheader = data.columns.tolist()[1]
    
    # assign the time to be the first column
    t = np.asarray(data[theader])
    
    # find where to cut, ie where the 17 stops and the 18 starts, and same for the 18 and 40
    cuts = [i for i, elem in enumerate(t) if 'Ion' in elem]
    # assign the time and m/z data to arrays
    x = np.asarray(data[theader][:cuts[0]]).astype(np.float)
    y17 = np.asarray(data[yheader][:cuts[0]]).astype(np.float)
    y18 = np.asarray(data[yheader][cuts[0]+1:cuts[1]]).astype(np.float)
    y40 = np.asarray(data[yheader][cuts[1]+1:]).astype(np.float)
    if len(y40) != len(y18):
        y40 = np.asarray(data[yheader][cuts[1]+1:cuts[2]]).astype(np.float)
    
    # initialize index variables (always set to zero)
    Arsi = 0 # Ar_start_index
    TPDsi = 0 # TPD_start_index

    # finds the start and end index for the TPD and Ar pulse, used for baseline correction and integration range
    for i,j in zip(x,range(len(x))):
        if i > Ars and Arsi == 0:
            Arsi = j
        elif i > Are and i < Are + .01:
            Arei = j # Ar_end_index
        if i > TPDs and TPDsi == 0:
            TPDsi = j
        elif i > TPDe and i < TPDe + .01:
            TPDei = j # TPD_end_index
    
    # correct for water in the m/z 17
    if wf == 1:
        ratio1718 = []
        watstart = TPDsi - 6500
        watend = TPDsi-500
        for k,l in zip(y17[watstart:watend],y18[watstart:watend]):
            ratio1718.append(k/l)
        water_fractionation = np.average(ratio1718)
        #print(min(ratio1718), max(ratio1718))
    else:
        water_fractionation = wf
        watstart, watend = (0, 0)
        ratio1718 = 0
    y17w = list(y17) # create a new variable to store the water correction
    y17w -= y18*water_fractionation # correct for water in the m/z 17
    
    # Baseline correct the m/z 17, sensitive to start and end times
    y17b = list(y17w) # create a new variable to store the baseline correction
    TPD_slope = (y17b[TPDsi] - y17b[TPDei])/(x[TPDsi]-x[TPDei])
    TPD_intercept = y17b[TPDsi]-x[TPDsi]*TPD_slope
    for k in range(len(x[TPDsi:TPDei])):
        y17b[TPDsi+k] -= TPD_slope*x[TPDsi+k] + TPD_intercept
    
    # Baseline correct the m/z 40, the Ar pulse
    y40b = list(y40) # create a new variable to store the baseline correction
    Ar_slope = (y40b[Arsi] - y40b[Arei])/(x[Arsi]-x[Arei])
    Ar_intercept = y40b[Arsi]-x[Arsi]*Ar_slope
    for l in range(len(x[Arsi:Arei])):
        y40b[Arsi+l] -= Ar_slope*x[Arsi+l] + Ar_intercept 
        
    # integrates the baseline corrected and water corrected m/z17 and m/z40 lines using trapezolidal rule
    # uses the ranges defined by the start and stop times provided at the beginning of the cell
    y17int = integrate.trapz(y17b[TPDsi:TPDei],x[TPDsi:TPDei])
    y40int = integrate.trapz(y40b[Arsi:Arei],x[Arsi:Arei])
    return(y17int, y40int, y17int/y40int, water_fractionation, 
           x, y17, y17w, y17b, y18, y40, y40b, watstart, watend, ratio1718,
          TPDsi, TPDei, Arsi, Arei)

# randomly for this function I decided that inputs are two capital letters and variables in function are longer
def Proton_count(ML, TL, RF, MA, AR, SA):
    Mw_H = 1
    Mw_Al = 27
    Mw_Si = 28
    Mw_O = 16
    gcat = (1-TL)*ML # calculate true mass of catalyst following loss of NH3
    NH3_gcat = AR*MA*RF/gcat # moles of ammonia per gram catalyst, based on response factor
    # moles of Al per gram catalyst, based on Si/Al determined from elemental analysis, equation based on CHA framework
    Al_gcat =(1/(1+SA))/((Mw_H+Mw_Al)/(1+SA) + (1-(1/(1+SA)))*Mw_Si + 2*Mw_O)
    NH3_Al = NH3_gcat/Al_gcat # moles NH3 per mole Al, this is the proton count and is 1:1 w/ Proton per Al
    return(NH3_Al)

#print commands will show in the console
# methods = post means it expects to receive something
# get means its asking for something
# how is what is returned by this function related to the jscript? 
# to publish changes to github
# git add file
# git commit -m "describe changes you are making" .
# git push
# make sure to ctrl shift R to get rid of cached website
@app.route('/myFunc', methods=['POST'])
def myFunc():
	input = request.files['file']
	#test = request.form['TPDs']
	print('test')
	#print(float(test))
	#TPD_start_time = 30          # start and end times for NH3 peak integration (TPDs)
	#TPD_end_time = TPD_start_time + 90              # (TPDe)
	#Ar_start_time = 190              # start and end times for Ar pulse integration (Ars)
	#Ar_end_time = 220               # (Are)
	#water_fraction = 1/4.2    # set to 1 to use average of y17/y18 ratio immediately preceeding TPD (wf)
	#result = TPD_analyze(input,TPD_start_time,TPD_end_time,Ar_start_time,Ar_end_time,water_fraction)
	# Proton_count inputs
	#mass_loaded = 0.0356 # grams, ML
	#TGA_loss = 0 # entered as a percent, TL
	#response_factor = 46.277 # changes frequently, RF for old 3184 is 2.36E-4, for new 3184 is 1.05e-4, 31.44 for 3150
	#moles_Ar = 1.59E-05 # MA, for the 3184 unit set this to 1 as it's included in the listed RF, set to 1.59E-05 in 3150
	#area_ratio = result[2] # AR
	#Si_Al = 2.55 # Si/Al
	#protons = Proton_count(mass_loaded, TGA_loss, response_factor, moles_Ar, area_ratio, Si_Al)
	#print(protons)
	# will have to do some funky stuff to get plots to show w/ matplotlib or something else
	# altair python library to use vegalite which is useful for visulation
	csv = '1,2,3\n4,5,6\n' #put csv file here
	return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=fileName.csv"})

@app.route('/parameters', methods=['POST'])
def parameters():
	TPDstart = float(request.form["TPDs"])
	Arstart = float(request.form["Ars"])
	Arend = float(request.form["Are"])
	watfrac = float(request.form["wf"])
	mass = float(request.form["SM"])
	resfac = float(request.form["RF"])
	moles = float(request.form["MA"])
	SiAL = float(request.form["SA"])
	result = (TPDstart+Arstart)
	return ('nothing')

@app.route('/result', methods=['POST'])
def result():
	result = 45
	print("this fires")
	return render_template('index.html',text=result)

@app.route('/')
def webpage():
	return render_template('index.html', text=35)

if __name__ == '__main__':
	webbrowser.open('http://127.0.0.1:5000/', new=2)
	app.run()