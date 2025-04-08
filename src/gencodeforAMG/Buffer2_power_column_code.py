import numpy as np
import pickle
with open('Buffer2_power_column_kernel.pkl', 'rb') as f:
	kde_cp = pickle.load(f)
num_datapoints=100
Buffer2_power_column=kde_cp.resample(num_datapoints)[0]