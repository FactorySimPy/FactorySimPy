import random
import simpy
import factorysimpy


env = simpy.Environment()

#Initializing nodes
m1 = Processor(env, name="Drill-1",work_capacity=1,store_capacity=3, delay=3)   
m2 = Processor(env, name="Grind-1",work_capacity=1,store_capacity=3, delay=0.3)

#Initializing edges
belt = Conveyor(env, belt_capacity=10, delay_per_slot=1.2)            
buffer1 = Buffer(env, name="buffer-1", store_capacity=5, delay=0.5)
buffer2 = Buffer(env, name="buffer-2", store_capacity=5, delay=0.5)



# initializing source and sink
src  = Source(env, delay= 2)
sink = Sink(env)


# adding connections
buffer1.connect(src,m1)
belt.connect = (m1,m2)
buffer2.connect = (m2,sink)

#run simulation
env.run(until=100)