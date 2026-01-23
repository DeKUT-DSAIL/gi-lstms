'''
This python file is used to compute the coulomb counting state of charge values
given current, time, cycles and other variables relevant to the Huazhong University of Science and Technology LFP Battery Dataset
_______
Process
_______
1. Obtain HUST data file names
2. Plot Current vs Time for 1st cycle on test file
3. Plot Current vs Time for 1st cycle on all files
'''

import os
import matplotlib.pyplot as plt
import pickle
import scipy.integrate as integrate
import pandas as pd
import random
from tqdm import tqdm
import numpy as np

DEBUG = not True
base_path = 'data/raw/hust/'
base_outputs_path = 'results/'
os.makedirs(base_outputs_path,exist_ok=True)
#Get HUST data
files = os.listdir(base_path)
print(files,len(files))

#Get cell names
raw_files = [file.rstrip('.pkl') for file in files]
print(raw_files)

#Plot Current vs time
if DEBUG:
    #Load Pickle Files
    with open(f'{base_path}/1-1.pkl', 'rb') as file:
        data = pickle.load(file)

    print('File 1-1 data : ',data)

    print('rul : ',len(data['1-1']['rul']))
    status_df = data['1-1']['data'][1]
    print(status_df['Status'].unique())

    status_df['Current (mA)'].plot();plt.show()

#Plot for all cells in base path
os.makedirs('results/current-plots/',exist_ok=True)
for raw_file in raw_files:
    print('-'*50)
    print(raw_file)
    with open(f'{base_path}/{raw_file}.pkl', 'rb') as file:
        data = pickle.load(file)

    status_df = data[raw_file]['data'][1]
    # # Filter out rows where Status is not 'Constant current charge'
    # filtered_df = status_df[status_df['Status'] != 'Constant current charge']
    
    # # # If you just want the 'Status' column values:
    # # status_values = filtered_df['Status']
    
    # filtered_df.head()
    print('rul : ',len(data[raw_file]['rul']))
    plt.figure(figsize=(8,5)) 
    print(status_df['Status'].unique())
    #status_df['Current (mA)'].plot()
    status_df['Current (mA)'].plot(title=f"Battery {raw_file}")
    plt.xlabel("Time (s)")
    plt.ylabel("Current (mA)")
    plt.savefig('results/current-plots/'+raw_file+'-current-plot.png', dpi=300)
    if DEBUG:
        plt.show()

#Current Integration Equation
def current_integration(initial_SOC,C_rated,I_bat,t_start,t_end):
    change_in_charge,_ = integrate.quad(lambda t:float(I_bat),float(t_start),float(t_end)) 
    #print("Change in Charge : ",change_in_charge)
    return float(initial_SOC) + 100.0/float(C_rated) * change_in_charge

# Precompute rated capacity constant
C_rated = 1100.0 * 3600

    

os.makedirs('results/plots/',exist_ok=True)
os.makedirs('results/csvs/',exist_ok=True)

for cycle_regimen in raw_files:
    #cycle_regimen are the files like '10-1','3-3','1-1'
    unpickled_df = pd.read_pickle(f'{base_path}/{cycle_regimen}.pkl')# read pickle file
    print(cycle_regimen)
    df = pd.DataFrame(unpickled_df[cycle_regimen])#convert pickle file data to dataframe
    rul = unpickled_df[cycle_regimen]['rul'] #obtain RUL (target_1)
    dq = unpickled_df[cycle_regimen]['dq'] #obtain changes in capacity
    data = unpickled_df[cycle_regimen]['data'] #cycling data
    
    ######## Faster Code ########

    # Prepare a list to store all DataFrames, so we only concatenate at the end
    df_list = []

    # Initialize the previous_last_time for cumulative time calculation
    previous_last_time = 0

    # Iterate over the data dictionary
    for cycle_number, cycle_data in data.items():
        df_data = pd.DataFrame(cycle_data)

        # Calculate cumulative time
        df_data['Time (s) cumu'] = df_data['Time (s)'] + previous_last_time

        # Add 'rul' and 'dq' columns directly without creating lists
        df_data['rul'] = rul[cycle_number]
        df_data['dq'] = dq[cycle_number]

        # Update the previous_last_time for the next cycle
        previous_last_time = df_data['Time (s) cumu'].iloc[-1]

        # Store the DataFrame in the list
        df_list.append(df_data)

    # Concatenate all DataFrames at once
    merge_df = pd.concat(df_list, ignore_index=True)

    # Sort only once if needed
    merge_df = merge_df.sort_values(by='Time (s) cumu', ascending=True).reset_index(drop=True)


    df = merge_df

    # Create a figure with 4 vertical subplots
    fig, axs = plt.subplots(4, 1, figsize=(8, 10), sharex=True)

    # Plot Current vs Time
    axs[0].plot(df['Time (s) cumu'], df['Current (mA)'], color='blue')
    axs[0].set_ylabel('Current (mA)')
    axs[0].set_title('Current vs Time')
    axs[0].set_xlabel('Time (s)')

    # Plot Voltage vs Time
    axs[1].plot(df['Time (s) cumu'], df['Voltage (V)'], color='orange')
    axs[1].set_ylabel('Voltage (V)')
    axs[1].set_title('Voltage vs Time')
    axs[1].set_xlabel('Time (s)')

    # Plot Capacity vs Time
    axs[2].plot(df['Time (s) cumu'], df['Capacity (mAh)'], color='green')
    axs[2].set_ylabel('Capacity (mAh)')
    axs[2].set_title('Capacity vs Time')
    axs[2].set_xlabel('Time (s)')

    # Plot RUL vs Time
    axs[3].plot(df['Time (s) cumu'], df['rul'], color='red')
    axs[3].set_ylabel('RUL (time)')
    axs[3].set_title('RUL vs Time')
    axs[3].set_xlabel('Time (s)')

    # # Plot Capacity vs Time
    # axs[4].plot(df['Time (s) cumu'], df['dq'], color='yellow')
    # axs[4].set_ylabel('dq')
    # axs[4].set_title('dq vs Time')
    # axs[4].set_xlabel('Time (s)')

    # Add some spacing between plots
    plt.tight_layout()

    # Specify the DPI (dots per inch) for better resolution
    plt.savefig('results/plots/'+cycle_regimen+'-full-plot.png', dpi=300)
    # Display the plots
    if DEBUG:
        plt.show()


    df = merge_df#.copy()
    df = df[df['Cycle number']<11]

    # instatiate a figure with 4 vertical subplots
    fig, axs = plt.subplots(4, 1, figsize=(8, 10), sharex=True)

    # Plot Current vs Time
    axs[0].plot(df['Time (s) cumu'], df['Current (mA)'], color='blue')
    axs[0].set_ylabel('Current (mA)')
    axs[0].set_title('Current vs Time')
    #axs[0].set_xlabel('Time (s)')

    # Plot Voltage vs Time
    axs[1].plot(df['Time (s) cumu'], df['Voltage (V)'], color='orange')
    axs[1].set_ylabel('Voltage (V)')
    axs[1].set_title('Voltage vs Time')
    #axs[1].set_xlabel('Time (s)')

    # Plot Capacity vs Time
    axs[2].plot(df['Time (s) cumu'], df['Capacity (mAh)'], color='green')
    axs[2].set_ylabel('Capacity (mAh)')
    axs[2].set_title('Capacity vs Time')
    #axs[2].set_xlabel('Time (s)')

    # Plot RUL vs Time
    axs[3].plot(df['Time (s) cumu'], df['rul'], color='red')
    axs[3].set_ylabel('RUL (time)')
    axs[3].set_title('RUL vs Time')
    axs[3].set_xlabel('Time (s)')

    # # Plot Capacity vs Time
    # axs[4].plot(df['Time (s) cumu'], df['dq'], color='yellow')
    # axs[4].set_ylabel('dq')
    # axs[4].set_title('dq vs Time')
    # axs[4].set_xlabel('Time (s)')

    # Sspecify the DPI (dots per inch) for better resolution
    plt.savefig('results/plots/'+cycle_regimen+'-first-10-plot.png', dpi=300)
    # Add some spacing between plots
    plt.tight_layout()

    # Display the plots
    if DEBUG:
        plt.show()

    merge_df.loc[merge_df['Capacity (mAh)'] == 0, 'previous_SOC'] = 0
    
    # Temporary storage for the computed SOC values
    cc_soc_values = np.zeros(len(merge_df))
    
    # Process each group
    for _, group in tqdm(merge_df.groupby('Cycle number')):
        # Initialize variables
        soc_values = []
        initial_SOC = 0  # Assuming this starts at 0 for each group
    
        # Iterate over each row in the group
        t_end = group.iloc[0]['Time (s)']  # Set initial t_end to the first time value
    
        for i, row in group.iterrows():
            if row["previous_SOC"] == 0:
                # Reset SOC calculation at the start of a new cycle
                initial_SOC = row["previous_SOC"]
                I_bat = row['Current (mA)']
                t_start = row['Time (s)']
                t_end = t_start  # Initialize t_end for the first row
            else:
                # Use previous SOC and time values for the next row
                t_start = t_end
                t_end = row['Time (s)']
                I_bat = row['Current (mA)']
    
            # Calculate SOC
            SOC = current_integration(initial_SOC=initial_SOC, C_rated=C_rated, I_bat=I_bat, t_start=t_start, t_end=t_end)
    
            # Update the initial_SOC for the next iteration
            initial_SOC = SOC
    
            # Store the result
            soc_values.append(SOC)
    
        # Assign computed SOC values back to the original DataFrame using loc with index slicing
        cc_soc_values[group.index] = soc_values
    
    # Finally, assign all computed SOC values to the DataFrame column in a single operation
    merge_df["CC_SOC"] = cc_soc_values
    merge_df.to_csv('results/csvs/'+cycle_regimen+'.csv',index=False)