# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 08:55:28 2021

Purpose of the script:

The purpose of the script is to load informations from files created by both the Quality Control of Nergica and the lidar installed on Nergica's site.
The informations is extracted for heights and the year selected a the top of this script. The information is then saved in a dataframe (.pkl) that can 
be easily loaded to plot graphes and compare data from the met mast (with a quality control from nergica) and the lidar. 

This code contains 4 sections
    1. The first section contains the code for loading lidar and met mast data from Nergica site
        The met mast has been run through a Quality Control.
        
        The Code cleans the data with the Quality Control and uniformize data like the timestamps to
        easily plot comparison graphs between the lidar and the met mast data.
        
        The code saves all dataFrame in a pickle file that can be extracted easily from python in order
        to plot graphs.
        
    2. The second section is a function to plot different data from the lidar in comparison with 
        the double anemometry that was performed with the Quality Control (the name of the result
                of the double anemometry is INFO01)
        
    
    3. The third section presents how we got the temperature, pressure and humidity data
        since we had problems on our hand with some data from the lidar (Windcube V2) 
        
        It also presents an easy correlation comparison
        
    4. The fourth section use the 3 previous sections to demonstrate how to use these functions
        You can manually change the informations to test other combinations
    
Example to run the code : 
    on spyder or other related IDEs -> Run the script
    on anaconda or other related prompts -> Make sure the file is in the right directory and run this command : python ScriptTask32_CorrelationLidarMetMast_Nergica.py

@author: oplambert
"""

#%%
"""

This section load data from windcube v2 files on Nergica site and put all data in a dictionnary
There is an entry for each height that we want

This section load data from the control quality of the met mast at Nergica site and put all data in a dictionary
There is an entry of each captor on the met mast that we want

"""

#Importation of python libraries used in this script
import datetime
import glob
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pickle

###################################################
###### PARAMETERS TO CHANGE MANUALLY - Lidar ######
###################################################
# Chosen year for lidaryear que l'on veut évaluer les données du Lidar
str_year = "2015" #2020
#List of heights that we want to evaluate
list_heights = ["80"]#,"60","80","100","120","140","160","180","200"]
# Path directory where lidar data files are saved
str_pathDirectory_lidar = ""

###################################################
#### PARAMETERS TO CHANGE MANUALLY - Met Mast #####
###################################################
# Data that we want to discard after the Quality Control
# Each code refers to a specific condition (ex.:R101 -> No Data, R104 -> instruments under maintenance)
list_dropColumn_CQ = ["R101","R103","R104","R105","R201","R202","R203","R204","R205","R206"]#,"R301","R303","R401","R403"]
#Path Directory where CQ files are saved
str_pathDirectory_CQ = "./"
# Height Filter in the CQ file name / In that case, height of 80m is chosen
str_filesFilter="*mmv1*Ht80m*"

###################################################
########### INITIALIzATION of VARIABLES ###########
###################################################
# Dictionary initialisation for raw CQ data and cleaned CQ data
dict_data_CQ={}
dict_data_CQ_cleaned={}
# Dictionary initialisation for raw lidar data and cleaned lidar data
dict_data_lidar={}
dict_data_lidar_cleaned={}


####################################################
########### Importation of lidar data ##############
####################################################
# Loop importing Lidar data for desired heights
# Save data in dict_data_lidar
# Name each dataFrame inside a dict : data_[annee]_[hauteur]m
for iter_height in list_heights:
    with open(str_pathDirectory_lidar+iter_height+"m_"+str_year+"_dataWindCube.pkl", 'rb') as file:
        vars()["df_"+str_year+"_"+iter_height+"m"]=pickle.load(file)
    dict_data_lidar["df_"+str_year+"_"+iter_height+"m"]=(vars()["df_"+str_year+"_"+iter_height+"m"])

####################################################
########## Cleaning of Control lidar data ##########
####################################################

# Add column for months in lidar dataframe : dict_data_lidar_cleaned    
for height_lidar in dict_data_lidar:
    df_lidar = dict_data_lidar[height_lidar]
    list_column_month_lidar = df_lidar["TimeObjectData"].astype(str).str[5:7]
    df_column_month=pd.DataFrame({"Month":list_column_month_lidar})
    df_lidar = df_lidar.join(df_column_month)
    dict_data_lidar_cleaned[height_lidar]=df_lidar
        
####################################################
####### Importation of Control Quality data ########
####################################################
# loop importing CQ data for chosen filter height
# Save data inside a dictionary : 
for str_file_n in glob.glob(str_pathDirectory_CQ + str_filesFilter):
    with open(str_file_n,mode='r') as file:
        int_posi_name = str(file).find("mmv1")
        str_name_key = str(file)[int_posi_name+5:int_posi_name+19]
        dict_data_CQ[str_name_key]= pd.read_csv(file, delimiter=';')


# Since there is no barometer at 80m, we add this entry to compare
# pressure on site with the lidar        
for str_file_m in glob.glob(str_pathDirectory_CQ+"*mmv1*Baroh*"):
    with open(str_file_m,mode='r') as file:
        int_posi_name = str(file).find("mmv1")
        str_name_key = str(file)[int_posi_name+5:int_posi_name+19]
        dict_data_CQ[str_name_key]= pd.read_csv(file, delimiter=';')

        

####################################################
######### Cleaning of Control Quality data #########
####################################################
# Loop to clean data from the CQ 
# Iteration over all captors in dict_data_CQ
for captor in dict_data_CQ:
    # Assign data from captor in a dataframe
    df_captor_CQ = dict_data_CQ[captor]
    # Initialisation of variables needed to clean dataframe
    array_columnTotalValue = np.zeros(len(df_captor_CQ))
    array_columnIndexValue=np.arange(0,len(df_captor_CQ))
    list_DateTime=[]
    
    # Inside loop to determine which row delete from CQ according to RXXX codes
    for column in list_dropColumn_CQ:
        # Add 1 in the row where RXXX is true 
        array_columnTotalValue += df_captor_CQ[column].to_numpy()
        
    # Loop over all timestamp to uniform Cq timestamps with lidar timestamps   
    for iter_timestamp in df_captor_CQ["Timestamp"]:
        # Correct the timestamp in a new list : list_DateTime
        list_DateTime.append(datetime.datetime.strptime(iter_timestamp[0:17].replace("-"," "),'%d %b %Y %H:%M'))  
    
    # Convert list_DateTime to a dataframe : df_timeObject     
    df_timeObject = pd.DataFrame(list_DateTime,columns=["TimeObjectData"])
    # Add a new column in df_captor_CQ with the new timestamps
    df_captor_CQ=df_captor_CQ.join(df_timeObject) 
    # Find index where a selected RXXX code is true
    array_columnIndex = (array_columnTotalValue > np.zeros(len(df_captor_CQ)))*array_columnIndexValue
    # Remove all rows where value is 0 to only keep none zero numbers
    array_columnIndex = array_columnIndex[array_columnIndex != 0]
    # Remove all rows of df_captor_CQ where a RXXX code is true and save new dataframe
    df_captor_CQ_cleaned = df_captor_CQ.drop(array_columnIndex)
    # Add a column Month in dataframe from timestamp object
    list_column_month = df_captor_CQ_cleaned["TimeObjectData"].astype(str).str[5:7]
    df_column_month=pd.DataFrame({"Month":list_column_month})
    df_captor_CQ_cleaned = df_captor_CQ_cleaned.join(df_column_month)
    # Assign cleaned dataframe in the dictionary : dict_data_CQ_cleaned
    dict_data_CQ_cleaned[captor] = df_captor_CQ_cleaned
    
    
####################################################
############ save data in pickle file ##############
####################################################
# Save lidar entry in pickle file for each height
for lidar_entry in dict_data_lidar_cleaned:
    df_save_output = dict_data_lidar_cleaned[lidar_entry]
    df_save_output.to_pickle("savedFiles/"+lidar_entry+".pkl")

# Save CQ entry in pickle file for each captor
for captor_entry in dict_data_CQ_cleaned:
    df_save_output = dict_data_CQ_cleaned[captor_entry]
    df_save_output.to_pickle("savedFiles/"+captor_entry+".pkl")
#%%
"""

This section initializes the function to plot graphs from the cleaned files of the previous section
You can directly go to the next section to use it

"""

####################################################
############## Function to plot graphs #############
####################################################
# Function that plot a comparison between lidar and Met Mast value for
# - a specified variable
#      -> Variable must be a string : Temp_int, Temp_ext, Pressure, Rel_hum, WiperCounts, Vbatt, Wdspd, Data_availability, Data_availability_2, wdspd_dis, CNR and Z-wind
# - specified months (in a list, ex.; ["08", "09"])
# - dictionary of captors from CQ
# - dictionary of lidar dataframe
# - list of heights of lidar in lidar dictionary (ex.: ["80","40"])
# - with ice detection from double anemometry (use INFO01)
def FunctionPlotGraphsIceLidar(Variable, Months, dictionary_CQ, dictionary_lidar, list_height_lidar, INFO="INFO01"):

    # loop over all months to create a graph for each month
    for iter_months in Months:
        plt.figure(num=int(iter_months))
        
        # loop over captors in dictionary of CQ Data
        for captor in dictionary_CQ:
            # Assign captor to a dataframe and only keep specified months
            df_captor_inter = dictionary_CQ[captor]
            df_captor = df_captor_inter[df_captor_inter["Month"] == iter_months]  
            int_iteration = 0
            
            # loop over heigts in dictionary of lidar Data
            for iter_heights in dictionary_lidar:
                df_lidar = dictionary_lidar[iter_heights] 
                                         
                # Don't take into account empty dataframes        
                if df_lidar.size > 1:
                    df_lidar_month=df_lidar[df_lidar["Month"] == iter_months]
                else:
                    print("Empty dataframe")
                    break
                    
                if Variable == "Temp_int":
                    plt.plot(df_lidar_month['TimeObjectData'], df_lidar_month["Int Temp (°C)"].astype("float"),'.k',markersize=1, label='_nolegend_')
                    plt.plot(df_captor["TimeObjectData"], df_captor[INFO].replace({0:np.nan}).astype("float")*10, 'sb', label='ice detected')
                    plt.xlabel("Time", fontsize=13)
                    plt.ylabel("Internal temperature (°C) ", fontsize=13)
                    plt.yticks(np.arange(-5,30,5))
                    plt.ylim(-5,30)
                    plt.xticks(rotation=45)
                    plt.legend(["ice detected"])
                    plt.tight_layout()
                    plt.grid(True)
                    # plt.show()
                elif Variable == "Temp_ext":
                    plt.plot(df_lidar_month['TimeObjectData'], df_lidar_month["Ext Temp (°C)"].astype("float"),'.k',markersize=1,label='_nolegend_')
                    plt.plot(df_captor["TimeObjectData"], df_captor[INFO].replace({0:np.nan}).astype("float")*5, 'sb', label='ice detected')
                    plt.xlabel("Time", fontsize=13)
                    plt.ylabel("External temperature (°C)", fontsize=13)
                    plt.yticks(np.arange(-20,20,5))
                    plt.ylim(-20,20)
                    # plt.yticks([])
                    plt.xticks(rotation=45)
                    plt.legend(["ice detected"])
                    plt.tight_layout()
                    plt.grid(True)
                    plt.show()              
                elif Variable == "Pressure":
                    plt.plot(df_lidar_month['TimeObjectData'], df_lidar_month["Pressure (hPa)"].astype("float"),".k",markersize=1,label='_nolegend_')
                    plt.plot(df_captor["TimeObjectData"], df_captor[INFO].replace({0:np.nan}).astype("float")*5, 'sb', label='ice detected')
                    plt.xlabel("Time", fontsize=13)
                    plt.ylabel("Pressure (hPa)", fontsize=13)
                    plt.yticks(np.arange(900,1010,10))
                    plt.ylim(900,1010)
                    # plt.yticks([])
                    plt.xticks(rotation=45)
                    plt.legend(["ice detected"])
                    plt.tight_layout()
                    plt.grid(True)
                    plt.show()                
                elif Variable == "Rel_hum":                
                    plt.plot(df_lidar_month['TimeObjectData'], df_lidar_month["Rel Humidity (%)"].astype("float"),".k", markersize=1,label='_nolegend_')
                    plt.plot(df_captor["TimeObjectData"], df_captor[INFO].replace({0:np.nan}).astype("float")*5, 'sb', label='ice detected')
                    plt.xlabel("Time", fontsize=13)
                    plt.ylabel("Relative humidity (%)", fontsize=13)
                    plt.yticks(np.arange(0,100,5))
                    plt.ylim(0,100)
                    # plt.yticks([])
                    plt.xticks(rotation=45)
                    plt.legend(["ice detected"])
                    plt.tight_layout()
                    plt.grid(True)
                    plt.show() 
                elif Variable == "WiperCounts":                
                    plt.plot(df_lidar_month['TimeObjectData'], df_lidar_month["Wiper count"].astype("float"),".k",markersize=1,label="_nolegend_")
                    plt.plot(df_captor["TimeObjectData"], df_captor[INFO].replace({0:np.nan}).astype("float")*25, 'sb', label='ice detected')
                    plt.xlabel("Time", fontsize=13)
                    plt.ylabel("Wiper counts", fontsize=13)
                    plt.yticks(np.arange(0,50,5))
                    plt.ylim(0,50)
                    # plt.yticks([])
                    plt.xticks(rotation=45)
                    plt.legend(["ice detected"])
                    plt.tight_layout()
                    plt.grid(True)
                    plt.show()
                elif Variable == "Vbatt": 
                    plt.plot(df_lidar_month['TimeObjectData'], df_lidar_month["Vbatt (V)"].astype("float"),".k",markersize=1,label='_nolegend_')
                    plt.plot(df_captor["TimeObjectData"], df_captor[INFO].replace({0:np.nan}).astype("float")*5, 'sb', label='ice detected')
                    plt.xlabel("Time", fontsize=13)
                    plt.ylabel("Voltage batterie (V)", fontsize=13)
                    plt.yticks(np.arange(0,30,5))
                    plt.ylim(0,30)
                    # plt.yticks([])
                    plt.xticks(rotation=45)
                    plt.legend(["ice detected"])
                    plt.tight_layout()
                    plt.grid(True)
                    plt.show()                               
                elif Variable == "Wdspd":                 
                    plt.plot(df_lidar_month['TimeObjectData'], df_lidar_month[list_height_lidar[int_iteration]+"m Wind Speed (m/s)"].astype("float"),".k",markersize=1,label='_nolegend_')
                    plt.plot(df_captor["TimeObjectData"], df_captor[INFO].replace({0:np.nan}).astype("float")*5, 'sb', label='ice detected')
                    plt.xlabel("Time", fontsize=13)
                    plt.ylabel("Windspeed (m/s)", fontsize=13)
                    plt.yticks(np.arange(0,30,5))
                    plt.ylim(0,30)
                    # plt.yticks([])
                    plt.xticks(rotation=45)
                    plt.legend(["ice detected"])
                    plt.tight_layout()
                    plt.grid(True)
                    plt.show()                
                elif Variable == "Data_availability":                 
                    plt.plot(df_lidar_month['TimeObjectData'], df_lidar_month[list_height_lidar[int_iteration]+"m Data Availability (%)"].astype("float"),".k",markersize=1,label='_nolegend_')
                    plt.plot(df_captor["TimeObjectData"], df_captor[INFO].replace({0:np.nan}).astype("float")*70, 'sb', label='ice detected')
                    plt.xlabel("Time", fontsize=13)
                    plt.ylabel("Data availability (%)", fontsize=13)
                    plt.yticks(np.arange(0,125,5))
                    plt.ylim(0,125)
                    # plt.yticks([])
                    plt.xticks(rotation=45)
                    plt.legend(["ice detected"])
                    plt.tight_layout()
                    plt.grid(True)
                    plt.show()                            
                elif Variable == "Data_availability_2":                 
                    vector_availability = (df_lidar_month[list_height_lidar[int_iteration]+"m Data Availability (%)"].astype("float") < 20)*1
                    plt.plot(df_lidar_month['TimeObjectData'], vector_availability.replace({0:np.nan}),".k",markersize=1,label='_nolegend_')
                    plt.plot(df_captor["TimeObjectData"], df_captor[INFO].replace({0:np.nan}).astype("float")*5, 'sb', label='ice detected')
                    plt.xlabel("Time", fontsize=13)
                    plt.ylabel("Data availability below 20%", fontsize=13)
                    plt.yticks(np.arange(-45,20,5))
                    plt.ylim(-45,20)
                    plt.yticks([])
                    plt.xticks(rotation=45)
                    plt.legend(["ice detected"])
                    plt.tight_layout()
                    plt.grid(True)
                    plt.show()                
                elif Variable == "wdspd_dis":                 
                    plt.plot(df_lidar_month['TimeObjectData'], df_lidar_month[list_height_lidar[int_iteration]+"m Wind Speed Dispersion (m/s)"].astype("float"),".k",markersize=1,label='_nolegend_')
                    plt.plot(df_captor["TimeObjectData"], df_captor[INFO].replace({0:np.nan}).astype("float")*5, 'sb', label='ice detected')
                    plt.xlabel("Time", fontsize=13)
                    plt.ylabel("Windspeed dispersion (m/s)", fontsize=13)
                    plt.yticks(np.arange(0,15,5))
                    plt.ylim(0,15)
                    # plt.yticks([])
                    plt.xticks(rotation=45)
                    plt.legend(["ice detected"])
                    plt.tight_layout()
                    plt.grid(True)
                    plt.show()
                elif Variable == "CNR": 
                    plt.plot(df_lidar_month['TimeObjectData'], df_lidar_month[list_height_lidar[int_iteration]+"m CNR (dB)"].astype("float"),'.k',markersize=1,label='_nolegend_')
                    plt.plot(df_captor["TimeObjectData"], df_captor[INFO].replace({0:np.nan}).astype("float")*5, 'sb', label='ice detected')
                    plt.xlabel("Time", fontsize=13)
                    plt.ylabel("CNR (dB)", fontsize=13)
                    plt.yticks(np.arange(-45,25,5))
                    plt.ylim(-45,25)
                    # plt.yticks([])
                    plt.xticks(rotation=45)
                    plt.legend(["ice detected"])
                    plt.tight_layout()
                    plt.grid(True)
                    plt.show()
                elif Variable == "Z-wind": 
                    plt.plot(df_lidar_month['TimeObjectData'], df_lidar_month[list_height_lidar[int_iteration]+"m Z-wind (m/s)"].astype("float"),'.k',markersize=1,label='_nolegend_')
                    plt.plot(df_captor["TimeObjectData"], df_captor[INFO].replace({0:np.nan}).astype("float")*5, 'sb', label='ice detected')
                    plt.xlabel("Time", fontsize=13)
                    plt.ylabel("Vertical wind (m/s)", fontsize=13)
                    plt.yticks(np.arange(-8,16,2))
                    plt.ylim(-8,16)
                    # plt.yticks([])
                    plt.xticks(rotation=45)
                    plt.legend(["ice detected"])
                    plt.tight_layout()
                    plt.grid(True)
                    plt.show()
                else:
                    print("Variable must be a string in: Temp_int, Temp_ext, Pressure, Rel_hum, WiperCounts, Vbatt, Wdspd, Data_availability, Data_availability_2, wdspd_dis, CNR and Z-wind")
                    break
    return df_lidar_month


#%%
"""
We had problems on our hand with the met mast on the lidar. Consequently, we are not able to extract:
    - Outside temperature
    - Outisde Pressure
    - Outise Relative Humidity
    
To obtain correlation from this 3 criteria, we used the data from the met mast at Nergica site

This section present an example of a simple correlation between this 3 criteria and ice accumulation
as determined by the double anemometry

"""
########################################################
########## Test for correlation with CQ Data ###########
######################################################## 
def FunctionPlotCorrelationCQandIceDetection(list_Months):

    # Initialisation of dataframe with the right timestamps
    df_test_correlation = df_timeObject
    # Initialization of the column names
    str_name=""
    int_interation = 2
    
    # loop over captors in dictionary of CQ to 
    for captor in dict_data_CQ_cleaned:
        # if captor is a pressure captor
        if captor.find("Baroh") >= 0:
            str_name = "Pressure"
            # Save information in dataframe : df_captor_CQ
            df_captor_CQ = dict_data_CQ_cleaned[captor]
            # Add column with df_captor_CQ in df_test_correlation
            df_test_correlation = df_test_correlation.join(df_captor_CQ["Moyenne"],lsuffix=1)
            
        # if captor is a temperature captor
        elif captor.find("Temp") >= 0:
            str_name="Temperature"
            # Save information in dataframe : df_captor_CQ
            df_captor_CQ=dict_data_CQ_cleaned[captor]
            # Add column with df_captor_CQ in df_test_correlation
            df_test_correlation=df_test_correlation.join(df_captor_CQ["Moyenne"],lsuffix=1)
            
        # if captor is a humidity captor
        elif captor.find("RHH") >= 0:
            str_name="Humidity"
            # Save information in dataframe : df_captor_CQ
            df_captor_CQ=dict_data_CQ_cleaned[captor]
            # Add column with df_captor_CQ in df_test_correlation
            df_test_correlation=df_test_correlation.join(df_captor_CQ["Moyenne"],lsuffix=1)        
        df_test_correlation.rename(columns = {"Moyenne":str_name},inplace=True)
        int_interation += 1
     
    # drop empty columns    
    df_test_correlation = df_test_correlation.dropna(axis=1, how='all')
    # Add a column month to de dataFrame df_test_correlation
    list_column_month = df_test_correlation["TimeObjectData"].astype(str).str[5:7]
    df_column_month=pd.DataFrame({"Month":list_column_month})
    df_test_correlation=df_test_correlation.join(df_column_month)
    
    # Test when humidity is over 90%
    list_bool_Test_Humidity = df_test_correlation["Humidity"] > 90
    # Test when temperature is over -5°C
    list_bool_Test_Temperature_1 = df_test_correlation["Temperature"].astype("float") > -5.0
    # # Test when temperature is under 5°C
    list_bool_Test_Temperature_2 = df_test_correlation["Temperature"].astype("float") < 5.0
    # # Test when pressure is under 970 hpa
    list_bool_Test_Pressure = df_test_correlation["Pressure"].astype("float") < 980
    # When all conditions are true
    list_bool_Test_all = list_bool_Test_Humidity & list_bool_Test_Temperature_1 & list_bool_Test_Temperature_2 & list_bool_Test_Pressure
    # # Add a column for when all conditions are respected
    df_test_correlation=df_test_correlation.join(pd.DataFrame(list_bool_Test_all,columns=["Test_all"]))
    
    
    # loop over specified months
    for iter_months in list_Months:
        plt.figure(num=int(iter_months)+100)
        # Loop over all captors
        for captor in dict_data_CQ_cleaned:
            # Assign captor to a dataframe and only keep specified months
            df_captor_inter = dict_data_CQ_cleaned[captor]
            df_captor = df_captor_inter[df_captor_inter["Month"] == iter_months]  
            # Extract the month of the iteration from the correlation dataframe : df_test_correlation 
            df_test_correlation_month = df_test_correlation[df_test_correlation["Month"] ==iter_months]
            # plot for each month in comparison to double anemometry
            plt.plot(df_test_correlation_month['TimeObjectData'], df_test_correlation_month["Test_all"].replace({0:np.nan}).astype("float"),'.k',markersize=1,label='_nolegend_')
            plt.plot(df_captor["TimeObjectData"], df_captor["INFO01"].replace({0:np.nan}).astype("float")*5, 'sb', label='ice detected')
            plt.xlabel("Time", fontsize=13)
            plt.ylabel("Correlation Test", fontsize=13)
            plt.yticks(np.arange(-45,25,5))
            plt.ylim(-45,25)
            plt.yticks([])
            plt.xticks(rotation=45)
            plt.legend(["ice detected"])
            plt.tight_layout()
            plt.grid(True)
    plt.show()
#%%
"""

This section shows a demonstration of how to use the previous sections

"""
##########################################################
########## Use of FunctionPlotGraphsIceLidar #############
##########################################################

Variable = "Temp_int"
#######################
# Choices of variable #
#######################
# Internal Temperature ("Temp_int")
# Outside Temperature ("Temp_ext")
# Pressure ("Pressure")
# Relative Humidity ("Rel_hum")
# Wiper counts ("WiperCounts")
# Volt battery ("Vbatt")
# WindSpeed ("Wdspd")
# Data availability ("Data_availability")
# Data availability under 20 % ("Data_availability_2")
# WindSpeed dispersion ("wdspd_dis")
# CNR ("CNR")
# vertical wind ("Z-wind")

list_Months= ["10", "11", "12"]
dictionary_CQ = dict_data_CQ_cleaned
dictionary_lidar = dict_data_lidar_cleaned
list_height_lidar = list_heights 

FunctionPlotGraphsIceLidar(Variable, list_Months, dictionary_CQ, dictionary_lidar, list_height_lidar, INFO="INFO01")
FunctionPlotCorrelationCQandIceDetection(list_Months)