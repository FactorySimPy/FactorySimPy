import numpy as np
import pickle
with open('Machine11_power_column_kernel.pkl', 'rb') as f:
	kde_cp = pickle.load(f)
num_datapoints=100
Machine11_power_column=kde_cp.resample(num_datapoints)[0]