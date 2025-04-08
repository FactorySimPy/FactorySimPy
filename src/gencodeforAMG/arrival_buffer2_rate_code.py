import scipy
loc=0.742978895003091
lamda=0.9918967934139019
num_datapoints=100
arrival_buffer2_rate=scipy.stats.expon.rvs(loc=loc,scale=lamda,size=num_datapoints)