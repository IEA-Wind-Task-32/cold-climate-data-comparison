# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 08:55:28 2021

Purpose of the script:

Lidar data have been collected on Nergica's site.
The purpose of the script is to analyze lidar data availability as a function of environmental parameters.
The environmental parameters are collected on 2 met masts, and a Quality Control is performed by Nergica.
The lidar data availability is computed by temprature and relavtive humidity, each grouped by bin.
Graphes are plotted to analyse the lidar data availability. 

This code contains 4 sections
    1. Importation of python libraries used in the code
    
    2. Lidar data to be analysed is saved as a dataframe and the format of dates is adjusted to be in
    concordance with dates on the met mast data
        
    3. The lidar data availability is computed monthly 
        
    4. MMV1 data are saved as a dataframe, and the quality control is performed. Then, a column is added to 
    store the windspeed corresponding to each timestamp from the lidar. This allow to identify columns containing
    data on both: Lidar and MMV1
        
    5. The Lidar data availability is computed analyzed, first using MMV1 temperature, second using MMV1 relative
    humudity
    
    6. Here, step 4. is repeated for MMV2
    
    7. Here, step 5 is repeated for MMV2
    
    8. Figures are plotted for analysis: lidar data availability by months, lidar data availability by temperature 
    comparing MMV1 and MMV2, lidar data availability by relative humidity comparing MMV1 and MMV2, number of points
    in each bin of temprature and relative humidity
    
Example to run the code : 
    on spyder or other related IDEs -> Run the script
    on anaconda or other related prompts -> Make sure the file is in the right directory and run this command : python ScriptTask32_LidarDataAvailability_MetMast_Nergica.py

@author: chodonou
"""
###################################################################
########## 1. Importation of python libraries #####################
###################################################################

import glob
import pandas as pd
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import time

start_time = time.time()

# Bins to group temperature or relative humiduty data for analysis, int>0
temp_bin = 1 # temprature bin
RHH_bin = 1 # Relative humidity bin
# data paths
lidar_data_path = "./lidarData/80m_2015_dataWindCube.pkl"
mmv1_data_path = "./metMastData/*80m*.csv"
mmv2_data_path = "./metMastData/*78m*.csv"
# Quality control codes
Droped = ["R101","R103","R104","R105","R201","R202","R203","R204","R205","R206"]

###################################################################
########## 2. Extraction of LIDAR data ############################
###################################################################

dataframe_output_2015 = pd.read_pickle(lidar_data_path)
print("--- Lidar data extracted ---")

# Date format adjustments 
dataframe_output_2015['TimeStamp'] = pd.to_datetime(dataframe_output_2015.TimeStamp)
dataframe_output_2015['Timestamp1'] = dataframe_output_2015['TimeStamp'].dt.strftime('%m/%d/%Y %H:%M')
dataframe_output_2015['Month'] = dataframe_output_2015["Timestamp1"].str[:2]

###################################################################
########## 3. Lidar data availability by month ####################
###################################################################

column_names = ["2015"]
Lidar_avail = pd.DataFrame(columns = column_names)
List_months=["09", "10", "11" ,"12"] #["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11" ,"12"]
heights=["80"] 
k=0
for l in List_months:
    if '80m Wind Speed (m/s)' in dataframe_output_2015.columns:
        temp2 = dataframe_output_2015.loc[dataframe_output_2015["Month"] == l]
        temp = temp2.loc[temp2["80m Wind Speed (m/s)"] != 'NaN' ]
        if len(temp2) > 0:
            Lidar_avail.loc[k,"2015"] = 100*len(temp)/len(temp2)
    k=k+1
print("--- Lidar availability by date computed ---")

###################################################################
########## 4. MMV1 data ###########################################
###################################################################

# Dictionnary for MMV1 data
data_CQ2015={} # MMV1 data as extracted
data_CQ2015_cleaned={} # MMV1 data after quality control
data_CQ2015_cleaned_Lidar={} # MMV1 data after quality control for timestamps with lidar data

# MMV1 data at 80m 
#for name in glob.glob("./DataCQ_2015_MMV1_empty/*80m*.csv" ): # Test if files are empty
for name in glob.glob(mmv1_data_path ):
    tp0=name.find('mmv1_')
    tp1=name.find('.csv')
    data_CQ2015[name[tp0:tp1]]= pd.read_csv(name, delimiter=';')
print("--- MMV1 data extracted ---")

# Perform quality control
for capteur in data_CQ2015:
    df=data_CQ2015[capteur]
    for drp in Droped:    
        df[drp].to_numpy()
        df = df.drop(df[df[drp] == 1].index)   
    data_CQ2015_cleaned[capteur] = df
print("--- MMV1 quality control done ---")

# Add empty column to store Lidar speed
column_names = ["Timestamp1"]
dataframe_output_2015_Time = pd.DataFrame(columns = column_names)
dataframe_output_2015_Time["Timestamp1"] = dataframe_output_2015["Timestamp1"]
for key, df in data_CQ2015_cleaned.items():
    df['Timestamp'] = pd.to_datetime(df.Timestamp)
    df['Timestamp1'] = df['Timestamp'].dt.strftime('%m/%d/%Y %H:%M')
    df['Month'] = df['Timestamp'].dt.strftime('%m')
    common = df.merge(dataframe_output_2015_Time,on=['Timestamp1'])
    df_Time = df["Timestamp1"]
    common2 = dataframe_output_2015.merge(df_Time,on=['Timestamp1'])
    common = common.sort_values(by=['Timestamp1'])
    common2 = common2.sort_values(by=['Timestamp1'])
    common["Lidar 80m Wind Speed (m/s)"] = common2["80m Wind Speed (m/s)"]
    data_CQ2015_cleaned_Lidar[key] = common
    
###################################################################
########## 5. Lidar vs MMV1 data analysis #########################
###################################################################

# Lidar availability by temperature 
column_names = ["temp", "Dispo 2015", "Vitesse Moyemme"]
Avail_Lidar_temp = pd.DataFrame(columns = column_names)

k=0
df = data_CQ2015_cleaned_Lidar["mmv1_TempUnHt80m0d_20150901_20151231"]
for l in range(-25,35,temp_bin):
    temp2 = df.loc[df["Moyenne"] <= l+temp_bin]
    temp2 = temp2.loc[temp2["Moyenne"] > l]
    temp = temp2.loc[temp2["Lidar 80m Wind Speed (m/s)"] != 'NaN' ] 
    temp3 = temp2["Lidar 80m Wind Speed (m/s)"].astype(float)
    if len(temp2) > 0:
        Avail_Lidar_temp.loc[k,"temp"] = l #str(l) #+ " to " + str(l+1)
        Avail_Lidar_temp.loc[k,"Dispo 2015"] = 100*len(temp)/len(temp2)
        Avail_Lidar_temp.loc[k,"Number"] = temp2["Moyenne"].count()
        Avail_Lidar_temp.loc[k,"temp mean"] = temp2["Moyenne"].mean()
        Avail_Lidar_temp.loc[k,"temp stdev"] = temp2["Moyenne"].std()
        Avail_Lidar_temp.loc[k,"Vitesse Moyemme"] = temp3.mean()
    k=k+1

# Lidar availability by relative humidity 
column_names = ["RH", "Dispo 2015", "Vitesse Moyemme"]
Avail_Lidar_RH = pd.DataFrame(columns = column_names)

k=0
df = data_CQ2015_cleaned_Lidar["mmv1_RHHt80m0d_20150901_20151231"]
for l in range(5,100,RHH_bin):
    temp2 = df.loc[df["Moyenne"] <= l+RHH_bin]
    temp2 = temp2.loc[temp2["Moyenne"] > l]
    temp = temp2.loc[temp2["Lidar 80m Wind Speed (m/s)"] != 'NaN' ]
    temp3 = temp2["Lidar 80m Wind Speed (m/s)"].astype(float)
    if len(temp2) > 0:
        Avail_Lidar_RH.loc[k,"RH"] = l #str(l) #+ " to " + str(l+1)
        Avail_Lidar_RH.loc[k,"Dispo 2015"] = 100*len(temp)/len(temp2)
        Avail_Lidar_RH.loc[k,"Number"] = temp2["Moyenne"].count()
        Avail_Lidar_RH.loc[k,"RH mean"] = temp2["Moyenne"].mean()
        Avail_Lidar_RH.loc[k,"RH stdev"] = temp2["Moyenne"].std()        
        Avail_Lidar_RH.loc[k,"Vitesse Moyemme"] = temp3.mean()
    k=k+1

print("--- MMV1 done ---")
print("--- %s seconds ---" % (time.time() - start_time))    

###################################################################
######################## 6. MMV2 data #############################
###################################################################

# Dictionnary for MMV2 data
data_CQ2015={} # MMV2 data as extracted
data_CQ2015_cleaned={} # MMV2 data after quality control
data_CQ2015_cleaned_Lidar={} # MMV2 data after quality control for timestamps with lidar data

# MMV2 data at 78m
for name in glob.glob(mmv2_data_path):
    tp0=name.find('mmv2_')
    tp1=name.find('.csv')
    data_CQ2015[name[tp0:tp1]]= pd.read_csv(name, delimiter=';')
print("--- MMV2 data extracted ---")

# Perform quality control
for capteur in data_CQ2015:
    df=data_CQ2015[capteur]
    for drp in Droped:    
        df[drp].to_numpy()
        df = df.drop(df[df[drp] == 1].index)   
    data_CQ2015_cleaned[capteur] = df
print("--- MMV2 quality control done ---")

# Add empty column to store Lidar speed
column_names = ["Timestamp1"]
dataframe_output_2015_Time = pd.DataFrame(columns = column_names)
dataframe_output_2015_Time["Timestamp1"] = dataframe_output_2015["Timestamp1"]
for key, df in data_CQ2015_cleaned.items():
    df['Timestamp'] = pd.to_datetime(df.Timestamp)
    df['Timestamp1'] = df['Timestamp'].dt.strftime('%m/%d/%Y %H:%M')
    df['Month'] = df['Timestamp'].dt.strftime('%m')
    common = df.merge(dataframe_output_2015_Time,on=['Timestamp1'])
    df_Time = df["Timestamp1"]
    common2 = dataframe_output_2015.merge(df_Time,on=['Timestamp1'])
    common = common.sort_values(by=['Timestamp1'])
    common2 = common2.sort_values(by=['Timestamp1'])
    common["Lidar 80m Wind Speed (m/s)"] = common2["80m Wind Speed (m/s)"]
    data_CQ2015_cleaned_Lidar[key] = common
    
###################################################################
########## 7. Lidar vs MMV2 data analysis #########################
###################################################################

# Lidar availability by temperature 
column_names = ["temp", "Dispo 2015", "Vitesse Moyemme"]
Avail_Lidar_temp2 = pd.DataFrame(columns = column_names)
k=0
df = data_CQ2015_cleaned_Lidar["mmv2_TempUnHt78m174d_20150901_20151231"]
for l in range(-25,35,temp_bin):
    temp2 = df.loc[df["Moyenne"] <= l+temp_bin]
    temp2 = temp2.loc[temp2["Moyenne"] > l]
    temp = temp2.loc[temp2["Lidar 80m Wind Speed (m/s)"] != 'NaN' ] 
    temp3 = temp2["Lidar 80m Wind Speed (m/s)"].astype(float)
    if len(temp2) > 0:
        Avail_Lidar_temp2.loc[k,"temp"] = l #str(l) #+ " to " + str(l+1)
        Avail_Lidar_temp2.loc[k,"Dispo 2015"] = 100*len(temp)/len(temp2)
        Avail_Lidar_temp2.loc[k,"Number"] = temp2["Moyenne"].count()
        Avail_Lidar_temp2.loc[k,"temp mean"] = temp2["Moyenne"].mean()
        Avail_Lidar_temp2.loc[k,"temp stdev"] = temp2["Moyenne"].std()
        Avail_Lidar_temp2.loc[k,"Vitesse Moyemme"] = temp3.mean()
    k=k+1

# Lidar availability by relative humidity 
column_names = ["RH", "Dispo 2015", "Vitesse Moyemme"]
Avail_Lidar_RH2 = pd.DataFrame(columns = column_names)
k=0
df = data_CQ2015_cleaned_Lidar["mmv2_RHUnHt78m174d_20150901_20151231"]
for l in range(5,100,RHH_bin):
    temp2 = df.loc[df["Moyenne"] <= l+RHH_bin]
    temp2 = temp2.loc[temp2["Moyenne"] > l]
    temp = temp2.loc[temp2["Lidar 80m Wind Speed (m/s)"] != 'NaN' ]
    temp3 = temp2["Lidar 80m Wind Speed (m/s)"].astype(float)
    if len(temp2) > 0:
        Avail_Lidar_RH2.loc[k,"RH"] = l #str(l) #+ " to " + str(l+1)
        Avail_Lidar_RH2.loc[k,"Dispo 2015"] = 100*len(temp)/len(temp2)
        Avail_Lidar_RH2.loc[k,"Number"] = temp2["Moyenne"].count()
        Avail_Lidar_RH2.loc[k,"RH mean"] = temp2["Moyenne"].mean()
        Avail_Lidar_RH2.loc[k,"RH stdev"] = temp2["Moyenne"].std()        
        Avail_Lidar_RH2.loc[k,"Vitesse Moyemme"] = temp3.mean()
    k=k+1

print("--- MMV2 done ---")
print("--- %s seconds ---" % (time.time() - start_time))  

###################################################################
########## 8. Plot figures ########################################
###################################################################

print("--- Plotting... ---" ) 

# Plot monthly Lidar data availability  
Lidar_avail.index += 9 
ax = Lidar_avail.plot.bar(rot=0)
ax.set_xlabel('Months', fontsize=16)
ax.set_ylabel('Availability (%)', fontsize=16)
ax.set_title('Lidar data availability by month')
plt.savefig('./savedFiles/Monthly Lidar availability')

# Plot lidar data availability by temperature (MMV1 & MMV2) 
fig = plt.figure()
if 'temp mean' in Avail_Lidar_temp.columns:
    plt.scatter(Avail_Lidar_temp["temp mean"], Avail_Lidar_temp["Dispo 2015"], label="2015, MMV1, 80m")
if 'temp mean' in Avail_Lidar_temp2.columns:
    plt.scatter(Avail_Lidar_temp2["temp mean"], Avail_Lidar_temp2["Dispo 2015"], s=5, label="2015, MMV2, 78m")
fig.suptitle('Lidar data availability by temperature', fontsize=18)
plt.xlabel('Temperature (°C)', fontsize=16)
plt.ylabel('Availability (%)', fontsize=16)
plt.legend(loc='lower right')#, bbox_to_anchor=(0.005, -0.05))
plt.savefig('./savedFiles/Lidar availability by temperature (MMV1 & MMV2)')

# Plot lidar data availability by humidity (MMV1 & MMV2)
fig = plt.figure()
if 'RH mean' in Avail_Lidar_RH.columns:
    plt.scatter(Avail_Lidar_RH["RH mean"], Avail_Lidar_RH["Dispo 2015"], label="2015, MMV1, 80m")
if 'RH mean' in Avail_Lidar_RH2.columns:
    plt.scatter(Avail_Lidar_RH2["RH mean"], Avail_Lidar_RH2["Dispo 2015"], s=5, label="2015, MMV2, 78m")
fig.suptitle('Lidar data availability by relative humidity', fontsize=18)
plt.xlabel('Relative Humidity (%)', fontsize=16)
plt.ylabel('Availability (%)', fontsize=16)
plt.legend(loc='lower right')#, bbox_to_anchor=(0.005, -0.05))
plt.savefig('./savedFiles/Lidar availability by humidity (MMV1 & MMV2)')

# Plot number of points in each bin for relative humidity
fig = plt.figure()
cmap = plt.get_cmap("tab10")
X  = np.arange(len(Avail_Lidar_RH["RH"])) 
X2  = np.arange(len(Avail_Lidar_RH2["RH"])) 
if 'Number' in Avail_Lidar_RH.columns:
    plt.bar(Avail_Lidar_RH["RH"],Avail_Lidar_RH["Number"],  width = 0.6,label="2015, MMV1, 80m")
if 'Number' in Avail_Lidar_RH2.columns:
    plt.bar(Avail_Lidar_RH2["RH"],Avail_Lidar_RH2["Number"], width = 0.4,label="2015, MMV2, 78m")
MMV1 = mpatches.Patch(color = cmap(0), label='2015, MMV1, 80m')
MMV2 = mpatches.Patch(color = cmap(1), label='2015, MMV2, 78m')
plt.legend(handles=[MMV1, MMV2])
fig.suptitle('Number of data points in each relative humidity bin', fontsize=18)
plt.xlabel('Relative Humidity (%)', fontsize=16)
plt.ylabel('Number of data points', fontsize=16)
plt.savefig('./savedFiles/Number of points humidity')

# Plot number of points in each bin for temperature
fig = plt.figure()
cmap = plt.get_cmap("tab10")
X  = np.arange(len(Avail_Lidar_temp["temp"])) 
X2  = np.arange(len(Avail_Lidar_temp2["temp"])) 
if 'Number' in Avail_Lidar_temp.columns:
    plt.bar(Avail_Lidar_temp["temp"],Avail_Lidar_temp["Number"], width = 0.6,label="2015, MMV1, 80m")
if 'Number' in Avail_Lidar_temp2.columns:
    plt.bar(Avail_Lidar_temp2["temp"],Avail_Lidar_temp2["Number"], width = 0.4,label="2015, MMV2, 78m")
MMV1 = mpatches.Patch(color = cmap(0), label='2015, MMV1, 80m')
MMV2 = mpatches.Patch(color = cmap(1), label='2015, MMV2, 78m')
plt.legend(handles=[MMV1, MMV2])
fig.suptitle('Number of data points in each temperature bin', fontsize=18)
plt.xlabel('Temperature (°C)', fontsize=16)
plt.ylabel('Number of data points', fontsize=16)
plt.savefig('./savedFiles/Number of points temperature')

print("--- %s seconds ---" % (time.time() - start_time))  
print("--- FIN ---" ) 
