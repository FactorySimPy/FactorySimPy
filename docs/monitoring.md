**Monitoring and Measurement**

All components has an attribute stats that stores all the parameters that are required to analyse the performance 
of that component. The details of the parameters that are available in each of the components are below

##Source
The source component reports the following key metrics:

1. Total number of items generated
2. Number of items discarded (non-blocking mode)
3. Time spent in each state

##Machine

The Machine component reports the following key metrics:

1. Total number of items processed
2. Time spent in each state

##Buffer
The Buffer component reports the following key metrics:

1. time averaged number of items available in buffer.
2. Time spent in each state 

##Conveyor
The conveyor reports the following key metrics:

1. Time averaged number of items 
3. Time spent in each state 
