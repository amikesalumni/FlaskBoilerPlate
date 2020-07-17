import numpy as np
import scipy.integrate as integrate
import pandas as pd
import altair as alt

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
    
    tolerance = 2*(x[1]-x[0])
    # initialize index variables (always set to zero)
    Arsi = 0 # Ar_start_index
    TPDsi = 0 # TPD_start_index
    # finds the start and end index for the TPD and Ar pulse, used for baseline correction and integration range
    for i,j in zip(x,range(len(x))):
        if i > Ars and Arsi == 0:
            Arsi = j
        elif i > Are and i < Are + tolerance:
            Arei = j # Ar_end_index
        if i > TPDs and TPDsi == 0:
            TPDsi = j
        elif i > TPDe and i < TPDe + tolerance:
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
    # uses the ranges defined by the start and stop times provided as inputs
    y17int = integrate.trapz(y17b[TPDsi:TPDei],x[TPDsi:TPDei])
    y40int = integrate.trapz(y40b[Arsi:Arei],x[Arsi:Arei])
    return(y17int, y40int, y17int/y40int, water_fractionation, 
           x, y17, y17w, y17b, y18, y40, y40b, watstart, watend, ratio1718,
          TPDsi, TPDei, Arsi, Arei, wf)

# randomly for this function I decided that inputs are two capital letters and variables in function are longer
def CHA_H_count(ML, RF, MA, AR, SA):
    Mw_H = 1
    Mw_Al = 27
    Mw_Si = 28
    Mw_O = 16
    NH3_gcat = AR*MA*RF/ML # moles of ammonia per gram catalyst, based on response factor
    # moles of Al per gram catalyst, based on Si/Al determined from elemental analysis, equation based on CHA framework
    Al_gcat =(1/(1+SA))/((Mw_H+Mw_Al)/(1+SA) + (1-(1/(1+SA)))*Mw_Si + 2*Mw_O)
    NH3_Al = NH3_gcat/Al_gcat # moles NH3 per mole Al, this is the proton count and is 1:1 w/ Proton per Al
    return(NH3_Al)

def Plots(result, nth):
    # This allows for data greater than 5000 rows to be plotted
    alt.data_transformers.disable_max_rows()
    
    x, y17, y17w, y17b, y18, y40, y40b = (result[4],result[5],result[6],result[7],result[8],result[9],result[10])
    TPDsi, TPDei, Arsi, Arei = (result[14], result[15], result[16], result[17])
    wf, watstart, watend, ratio1718 = (result[18],result[11], result[12],result[13])
    
    temp = list(x[TPDsi:TPDei])
    temp = temp - temp[0]
    temp = 323 + temp*10
    temp = list(temp[0::nth])
    
    # cut out and keep every nth point
    # Raw data Cuts
    xr = list(x[0::nth])
    y17r = list(y17[0::nth])
    y18r = list(y18[0::nth])
    y40r = list(y40[0::nth])
    
    # TPDsi:TPDei cuts
    xt = (list(x[TPDsi:TPDei]))[0::nth]
    y17t = (list(y17[TPDsi:TPDei]))[0::nth]
    y17wt = (list(y17w[TPDsi:TPDei]))[0::nth]
    y17bt = (list(y17b[TPDsi:TPDei]))[0::nth]
    y18t = (list(y18[TPDsi:TPDei]))[0::nth]
    
    # Ar cuts
    xa = (list(x[Arsi:Arei]))[0::nth]
    y40a = (list(y40[Arsi:Arei]))[0::nth]
    y40ba = (list(y40b[Arsi:Arei]))[0::nth]
    
    raw_data = pd.DataFrame({'x': xr, 'y17': y17r, 'y18': y18r, 'y40': y40r})
    raw_reshape = pd.melt(raw_data, id_vars=['x'], value_vars=['y17','y18','y40'], var_name='legend', value_name='y')
    raw_chart = alt.Chart(raw_reshape).mark_line(
        size=3
    ).encode(
        alt.X('x', axis=alt.Axis(tickCount=7, title='Time (min)')),
        alt.Y('y', axis=alt.Axis(tickCount=7, title='Intensity (counts)')),
        alt.Color('legend', legend=alt.Legend(orient='top-left'))
    ).configure_axis(
        grid=False
    ).properties(
        width=300,
        height=200,
        title='Raw Data from CSV'
    ).interactive()

    TPD_data = pd.DataFrame({'x':xt, 'y17':y17t, 'y17 water corrected':y17wt, 'y17 baseline corrected':y17bt, 'y18':y18t})
    TPD_reshape = pd.melt(TPD_data, id_vars=['x'], value_vars=['y17','y17 water corrected','y17 baseline corrected','y18'], var_name='legend', value_name='y')
    TPD_chart = alt.Chart(TPD_reshape).mark_line(
        size=3
    ).encode(
        alt.X('x', axis=alt.Axis(title='Time (min)')),
        alt.Y('y', axis=alt.Axis(title='Intensity (counts)')),
        alt.Color('legend', legend=alt.Legend(orient='top-right'))
    ).configure_axis(
        grid=False    
    ).properties(
        width = 300,
        height=200,
        title='TPD: y17 Water and Baseline Correction '
    )
    
    Ar_data = pd.DataFrame({'x':xa, 'y40':y40a, 'y40 baseline corrected':y40ba})
    Ar_reshape = pd.melt(Ar_data, id_vars=['x'], value_vars=['y40','y40 baseline corrected'], var_name='legend', value_name='y')
    Ar_chart = alt.Chart(Ar_reshape).mark_line(
        size=3
    ).encode(
        alt.X('x', axis=alt.Axis(title='Time (min)')),
        alt.Y('y', axis=alt.Axis(title='Intensity (counts)')),
        alt.Color('legend', legend=alt.Legend(orient='top-right'))
    ).configure_axis(
        grid=False    
    ).properties(
        width = 300,
        height=200,
        title='Ar Pulse'
    )
    
    T_data = pd.DataFrame({'T':temp, 'y':y17bt})
    T_chart = alt.Chart(T_data).mark_line(
        size=3
    ).encode(
        alt.X('T', axis=alt.Axis(title='Temp (K)')),
        alt.Y('y', axis=alt.Axis(title='Intensity (counts)')),
    ).configure_axis(
        grid=False    
    ).properties(
        width = 300,
        height=200,
        title='TPD as a Function of Temperature'
    )
    
    if wf == 1:
        W_data = pd.DataFrame({'x':x[watstart:watend], 'y':ratio1718})
        W_chart = alt.Chart(W_data).mark_line(
            size=3
        ).encode(
            alt.X('x', axis=alt.Axis(title='Time (min)')),
            alt.Y('y', axis=alt.Axis(title='Value of y17/y18 Preceeding TPD')),
        ).configure_axis(
            grid=False    
        ).properties(
            width = 300,
            height=200
        )
    else:
        W_chart = alt.LayerChart()

    return (raw_chart, TPD_chart, Ar_chart, T_chart, W_chart)