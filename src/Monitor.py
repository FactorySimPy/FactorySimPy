
class ProcessorMonitor:
    def __init__(self, name):
        self.name = name
        self.items_processed = 0
        self.total_processing_time = 0
        self.total_waiting_time = 0
        self.process_start_times = []

    def record_start(self, current_time):
        self.process_start_times.append(current_time)

    def record_end(self, current_time):
        start_time = self.process_start_times.pop()
        self.items_processed += 1
        self.total_processing_time += (current_time - start_time)
       

    def record_waiting_time(self, wait_time):
        self.total_waiting_time += wait_time



    def summary(self):
        return {
            "Processor": self.name,
            "Items Processed": self.items_processed,
            "Total Processing Time": self.total_processing_time,
            "Total Waiting Time": self.total_waiting_time,
            "Avg Processing Time": self.total_processing_time / self.items_processed if self.items_processed else 0
        }

class SystemMonitor:
    def __init__(self):
        self.monitors = {}

    def register_processor(self, processor):
        #Adding the monitor object created inside the processor class into system monitor
        processor_name =  processor.name
        self.monitors[processor_name] = processor.monitor



    def get_monitor(self, processor_name):
        return self.monitors[processor_name]

    def summary(self):
        return {name: monitor.summary() for name, monitor in self.monitors.items()}
