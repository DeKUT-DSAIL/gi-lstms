
import os
from tqdm import tqdm
import matplotlib.pyplot as plt 
import pandas as pd

base_paths = 'results/csvs/'
original_files = [file.rstrip('.csv') for file in os.listdir(base_paths)]
os.makedirs('results/csv-summary/',exist_ok=True)
os.makedirs('results/capacity-fade-cno-plot/',exist_ok=True)
os.makedirs('results/capacity-fade-time-plot/',exist_ok=True)
os.makedirs('results/SoH-cno-plot/',exist_ok=True)
for file in tqdm(original_files):
    df_sample = pd.read_csv(base_paths+file+'.csv')
    
    cycle_data_list = []
    
    for cycle_number, group in tqdm(df_sample.groupby('Cycle number')):
        cycle_data = {
            'Time (s) cumu':group['Time (s) cumu'].max(),
            'Cycle number': cycle_number,
            'max_SOC': group['CC_SOC'].max(),
            'min_SOC': group['CC_SOC'].min(),
            'SoH' : abs(group['CC_SOC'].max()) + abs(group['CC_SOC'].min()),
            'max_voltage': group['Voltage (V)'].max(),
            'min_voltage': group['Voltage (V)'].min(),
            'mean_voltage': group['Voltage (V)'].mean(),
            'max_current': group['Current (mA)'].max(),
            'min_current': group['Current (mA)'].min(),
            'timetaken': group['Time (s)'].max() - group['Time (s)'].min(),
            'max_capacity': group['Capacity (mAh)'].max(),
            'min_capacity': group['Capacity (mAh)'].min(),
            'rul': int(group['rul'].mean()),  # Replace with your RUL calculation function
            #'Time (s) cumu':
        }
        cycle_data_list.append(cycle_data)
        
    df_cycle_data = pd.DataFrame(cycle_data_list)
    df_cycle_data['max_capacity_fade_rate'] = -(df_cycle_data['max_capacity'].diff() / df_cycle_data['Cycle number'].diff())

    df_cycle_data.to_csv('results/csv-summary/'+file+'.csv',index=False)
    
    # Create a figure with 5 vertical subplots
    plt.plot(df_cycle_data['Cycle number'], df_cycle_data['SoH'])
    
    # Add labels and title
    plt.xlabel('Cycle number')
    plt.ylabel('SoH')
    plt.title('SoH per Cycle number')
    
    # Add some spacing between plots
    plt.tight_layout()
    
    # You can also specify the DPI (dots per inch) for better resolution
    plt.savefig('results/SoH-cno-plot/'+file+'.png', dpi=300)
    # Display the plots
    plt.show()
    # Plot the line against time
    plt.plot(df_cycle_data['Cycle number'], df_cycle_data['max_SOC'])
    
    # Add labels and title
    plt.xlabel('Cycle number')
    plt.ylabel('Max % of initial capacity')
    plt.title('Max Capacity per Cycle number')
    
    # Add some spacing between plots
    plt.tight_layout()
    
    # You can also specify the DPI (dots per inch) for better resolution
    plt.savefig('results/capacity-fade-cno-plot/'+file+'.png', dpi=300)
    # Display the plots
    plt.show()

    # Create a figure with 5 vertical subplots
    # Plot the line against time
    plt.plot(df_cycle_data['Time (s) cumu'], df_cycle_data['max_SOC'])
    
    # Add labels and title
    plt.xlabel('Time (s) cumu')
    plt.ylabel('Max % of initial capacity')
    plt.title('Max Capacity per end of cycle in time')
    
    # Display the plot
    plt.show()
    # You can also specify the DPI (dots per inch) for better resolution
    plt.savefig('results/capacity-fade-time-plot/'+file+'.png', dpi=300)