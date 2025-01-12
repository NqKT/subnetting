import time
from subnetting import CIDR, VLSM

def test_execution_time_subnetting(ip, mask, num_subnets=None, host_requirements=None):
    if num_subnets:
        cidr = CIDR(ip, mask)
        start = time.perf_counter() 
        cidr.calculate_subnets(num_subnets)
        print(f"CIDR ({ip}/{mask}, {num_subnets} subnet): {time.perf_counter()  - start:.6f} seconds")
    
    if host_requirements:
        vlsm = VLSM(ip, mask)
        start = time.perf_counter() 
        vlsm.calculate_subnets(host_requirements)
        print(f"VLSM ({ip}/{mask}, host {host_requirements}): {time.perf_counter()  - start:.6f} seconds")

# Chạy thử với các đầu vào
test_execution_time_subnetting("10.10.10.0", 28, num_subnets=2)
test_execution_time_subnetting("10.10.0.0", 16, num_subnets=256)
test_execution_time_subnetting("10.0.0.0", 10, num_subnets=1000)
test_execution_time_subnetting("10.10.10.0", 20, host_requirements=[90, 60, 20, 7])
test_execution_time_subnetting("10.10.10.0", 16, host_requirements=[500, 300, 200, 100])
test_execution_time_subnetting("10.10.0.0", 10, host_requirements=[10000, 2000, 500, 90, 10])
