import ipaddress
from math import log2, floor, ceil

class Subnetting:
    def __init__(self, ip, mask):
        self.network = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)
        self.mask = int(mask)

    def get_network_details(self):
        hosts = list(self.network.hosts())
        return {
            "Địa chỉ mạng": f"{self.network.network_address}/{self.network.prefixlen}",
            "Dải địa chỉ": f"{hosts[0]} - {hosts[-1]}" if hosts else "No usable hosts",
            "Địa chỉ broadcast": str(self.network.broadcast_address),
            "Số lượng host": self.network.num_addresses - 2 if self.network.num_addresses > 2 else 0
        }

class CIDR(Subnetting):
    def __init__(self, ip, mask):
        super().__init__(ip, mask)
        self.prefix_length = None

    def calculate_subnets(self, num_subnets):    
        if self.network.num_addresses/num_subnets < 1:
            raise ValueError(f"Không thể chia vì với {num_subnets} mạng con thì mỗi mạng có 0 địa chỉ khả dụng .")
        else:
            self.prefix_length = 32 - floor(log2(self.network.num_addresses/num_subnets))       
        subnets = []
        subnet_networks = list(self.network.subnets(new_prefix=self.prefix_length))

        for i in range(num_subnets):
            subnet = Subnetting(
                str(subnet_networks[i].network_address),
                str(subnet_networks[i].prefixlen)
            )
            subnets.append(subnet.get_network_details())
        return subnets

class VLSM(Subnetting):
    def calculate_subnets(self, host_requirements):
        host_requirements.sort(reverse=True)
        subnets = []
        available_network = self.network
        
        for i, hosts in enumerate(host_requirements):
            if i >= 1:
                prefix_new = 32 - ceil(log2(hosts + 2))
                prefix_old = 32 - ceil(log2(host_requirements[i - 1] + 2))
                if prefix_new == prefix_old or prefix_new - prefix_old == 1:
                    prefix_length = prefix_old
                else:
                    prefix_length = prefix_new
            else:
                required_size = ceil(log2(hosts + 2))
                prefix_length = 32 - required_size
            try:
                subnet_network = next(available_network.subnets(new_prefix=prefix_length))
                subnet = Subnetting(
                    str(subnet_network.network_address),
                    str(subnet_network.prefixlen)
                )
                subnets.append(subnet.get_network_details())
                available_network = ipaddress.IPv4Network(
                    f"{subnet_network.broadcast_address + 1}/{self.mask}",
                    strict=False
                )
            except (ValueError, StopIteration):
                raise ValueError(f"Không đủ không gian địa chỉ cho subnet {i + 1}")
                
        return subnets

def main():
    try:
        mode = input("Chọn chế độ (CIDR/VLSM): ").strip().upper()
        ip_input = input("Nhập địa chỉ IP và mặt nạ mạng (VD: 192.168.1.0/24): ").strip()
        ip, mask = ip_input.split('/')

        try:
            network = ipaddress.IPv4Network(ip_input, strict=False)
            ip = str(network.network_address)
            mask = network.prefixlen
        except ValueError as e:
            print(f"Lỗi: Địa chỉ IP hoặc mặt nạ mạng không hợp lệ. {e}")
            return
        
        if mode == "CIDR":
            num_subnets = int(input("Nhập số mạng con cần chia: ").strip())
            cidr = CIDR(ip, mask)
            subnets = cidr.calculate_subnets(num_subnets)
            print("\nKết quả chia mạng CIDR:")
            for i, subnet in enumerate(subnets, 1):
                print(f"Mạng con {i}: {subnet}")

        elif mode == "VLSM":
            host_requirements = [
                int(x) for x in input("Nhập danh sách yêu cầu host (cách nhau bởi dấu phẩy): ")
                .strip().split(',')
            ]
            vlsm = VLSM(ip, mask)
            subnets = vlsm.calculate_subnets(host_requirements)
            print("\nKết quả chia mạng VLSM:")
            for i, subnet in enumerate(subnets, 1):
                print(f"Mạng con {i}: {subnet}")

        else:
            print("Chế độ không hợp lệ.")

    except ValueError as e:
        print(f"Lỗi: {e}")
    except Exception as e:
        print(f"Đã xảy ra lỗi không mong muốn: {e}")

if __name__ == "__main__":
    main()
