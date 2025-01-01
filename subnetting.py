from math import log2, floor, ceil
class Subnetting:
    def __init__(self, ip, mask):
        self.ip = ip
        self.mask = int(mask)
        self.network_address = self.calculate_network_address()
        self.broadcast_address = self.calculate_broadcast_address()

    def ip_to_binary(self, ip): # Chuyển đổi IP sang dạng nhị phân        
        octets = ip.split('.')        
        binary_ip = ''

        for octet in octets:
            num = int(octet)
            binary = ''
            i = 0
            while num > 0:
                binary = str(num % 2) + binary
                num //= 2
                i += 1
            if i != 8:
                binary= '0' * (8-i) + binary
            binary_ip += binary
        return binary_ip

    def binary_to_ip(self, binary_ip):
    # Chuyển đổi nhị phân sang thập phân
        ip = ''
        for i in range(0, 32, 8):  # Chia chuỗi nhị phân thành các nhóm 8 bit
            binary_octet = binary_ip[i:i + 8]
            decimal = 0
            for bit in binary_octet:
                decimal = decimal * 2 + int(bit) 
            ip += str(decimal) + '.'        
        return ip[:-1]  
    
    def binary_to_decimal(self, binary):
        decimal = 0
        for bit in binary:
            decimal = decimal * 2 + int(bit)
        return decimal

    def decimal_to_binary(self, decimal):
        binary = ''
        i = 0
        while decimal > 0:
            binary = str(decimal % 2) + binary
            decimal //= 2
            i += 1
        if i != 32:
            binary= '0' * (32-i) + binary        
        return binary

    def calculate_network_address(self):
        ip_binary = self.ip_to_binary(self.ip)
        network_binary = ip_binary[:self.mask] + '0' * (32 - self.mask)
        return self.binary_to_ip(network_binary)

    def calculate_broadcast_address(self):
        ip_binary = self.ip_to_binary(self.ip)
        broadcast_binary = ip_binary[:self.mask] + '1' * (32 - self.mask)
        return self.binary_to_ip(broadcast_binary)

    def calculate_num_hosts(self, mask):
        return (2 ** (32 - mask)) - 2

    def get_network_details(self):
        first_host_decimal = self.binary_to_decimal(self.ip_to_binary(self.network_address)) + 1
        last_host_decimal = self.binary_to_decimal(self.ip_to_binary(self.broadcast_address)) - 1

        return {
            "Địa chỉ mạng": f"{self.network_address}/{self.mask}",
            "Dải địa chỉ": f"{self.binary_to_ip(self.decimal_to_binary(first_host_decimal))} - "
                           f"{self.binary_to_ip(self.decimal_to_binary(last_host_decimal))}",
            "Địa chỉ broadcast": self.broadcast_address,
            "Số lượng host": self.calculate_num_hosts(self.mask),
        }


class CIDR(Subnetting):
    def calculate_subnets(self, num_subnets):
        total = self.calculate_num_hosts(self.mask) + 2      
        if floor(log2(total/num_subnets)) < 2:
            raise ValueError(f"Không thể chia vì với {num_subnets} mạng con thì mỗi mạng có 0 địa chỉ khả dụng .")
        else:
            prefix_length = 32 - floor(log2(total/num_subnets))        
        subnets = []
        subnet_size = 2 ** (32 - prefix_length)

        for i in range(num_subnets):
            network_decimal = self.binary_to_decimal(self.ip_to_binary(self.network_address)) + i * subnet_size
            subnet_ip = self.binary_to_ip(self.decimal_to_binary(network_decimal))
            subnet = Subnetting(subnet_ip, prefix_length)
            subnets.append(subnet.get_network_details())
        return subnets


class VLSM(Subnetting):
    def calculate_subnets(self, host_requirements):
        host_requirements.sort(reverse=True)
        subnets = []
        available_network = self.network_address

        for i, hosts in enumerate(host_requirements):
            if i>=1:
                prefix_new = 32 - ceil(log2(hosts+2))
                prefix_old = 32 - ceil(log2(host_requirements[i-1]+2))
                if (prefix_new == prefix_old or prefix_new - prefix_old==1):
                    prefix_length = prefix_old
                else:
                    prefix_length = prefix_new 
            else:
                required_size = ceil(log2(hosts+2))
                prefix_length = 32 - required_size
            if 2**(32 - prefix_length) > 2**(32 - self.mask):
                raise ValueError("Không đủ địa chỉ để cấp phát cho yêu cầu.")            
            subnet = Subnetting(available_network, prefix_length)
            subnets.append(subnet.get_network_details())

            next_network_decimal = self.binary_to_decimal(self.ip_to_binary(subnet.broadcast_address)) + 1
            available_network = self.binary_to_ip(self.decimal_to_binary(next_network_decimal))
        return subnets


if __name__ == "__main__":
    mode = input("Chọn chế độ (CIDR/VLSM): ").strip().upper()
    ip, mask = input("Nhập địa chỉ IP và mặt nạ mạng (VD: 192.168.1.0/24): ").strip().split('/')

    if mode == "CIDR":
        num_subnets = int(input("Nhập số mạng con cần chia: ").strip())
        cidr = CIDR(ip, mask)
        subnets = cidr.calculate_subnets(num_subnets)
        print("\nKết quả chia mạng CIDR:")
        for i, subnet in enumerate(subnets):
            print(f"Mạng con {i + 1}: {subnet}")

    elif mode == "VLSM":
        host_requirements = list(map(int, input("Nhập danh sách yêu cầu host (cách nhau bởi dấu phẩy): ").strip().split(',')))
        vlsm = VLSM(ip, mask)
        subnets = vlsm.calculate_subnets(host_requirements)
        print("\nKết quả chia mạng VLSM:")
        for i, subnet in enumerate(subnets):
            print(f"Mạng con {i + 1}: {subnet}")

    else:
        print("Chế độ không hợp lệ.")
