import os
import matplotlib.pyplot as plt
import pickle
import scipy.integrate as integrate

DEBUG = not True
base_path = 'data/raw/'

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
os.makedirs('current-plots/',exist_ok=True)
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
    plt.savefig('current-plots/'+raw_file+'-current-plot.png', dpi=300)
    if DEBUG:
        plt.show()

#Current Integration Equation
def current_integration(initial_SOC,C_rated,I_bat,t_start,t_end):
    change_in_charge,_ = integrate.quad(lambda t:float(I_bat),float(t_start),float(t_end)) 
    #print("Change in Charge : ",change_in_charge)
    return float(initial_SOC) + 100.0/float(C_rated) * change_in_charge