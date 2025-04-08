import scipy
mean=1.4609093033612908
variance=13.210716250044566
num_datapoints=100
arrival_M11_rate=scipy.stats.norm.rvs(loc=mean,scale=variance,size=num_datapoints)