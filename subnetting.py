class IPAddressConvert:
    @staticmethod
    def ip_to_binary(ip): 
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
    
    @staticmethod
    def binary_to_ip(binary_ip):
        ip = ''
        for i in range(0, 32, 8):
            binary_octet = binary_ip[i:i + 8]
            decimal = 0
            for bit in binary_octet:
                decimal = decimal * 2 + int(bit) 
            ip += str(decimal) + '.'        
        return ip[:-1] 

    @staticmethod
    def binary_to_decimal(binary):
        decimal = 0
        for bit in binary:
            decimal = decimal * 2 + int(bit)
        return decimal

    @staticmethod
    def decimal_to_binary(decimal):
        binary = ''
        i = 0
        while decimal > 0:
            binary = str(decimal % 2) + binary
            decimal //= 2
            i += 1
        if i != 32:
            binary= '0' * (32-i) + binary        
        return binary

class CalculatorAddressConvert:
    @staticmethod
    def calculate_network_address(ip, mask):
        ip_binary = IPAddressConvert.ip_to_binary(ip)
        network_binary = ip_binary[:mask] + '0' * (32 - mask)
        return IPAddressConvert.binary_to_ip(network_binary)
    
    @staticmethod
    def calculate_broadcast_address(ip, mask):
        ip_binary = IPAddressConvert.ip_to_binary(ip)
        broadcast_binary = ip_binary[:mask] + '1' * (32 - mask)
        return IPAddressConvert.binary_to_ip(broadcast_binary)

class Subnetting:
    def __init__(self, ip, mask):
        self.ip = ip
        self.mask = int(mask)
        self.network_address = CalculatorAddressConvert.calculate_network_address(ip, mask)
        self.broadcast_address = CalculatorAddressConvert.calculate_broadcast_address(ip, mask)

    def floor_log2(self, x):
        k = 0
        while (1 << k) <= x:
            k += 1
        return k - 1
    
    def ceil_log2(self, x):
        k = 0
        while (1 << k) < x:
            k += 1
        return k

    def calculate_num_hosts(self, mask):
        return (2 ** (32 - mask)) - 2

    def get_network_details(self):
        first_host_decimal = IPAddressConvert.binary_to_decimal(IPAddressConvert.ip_to_binary(self.network_address)) + 1
        last_host_decimal = IPAddressConvert.binary_to_decimal(IPAddressConvert.ip_to_binary(self.broadcast_address)) - 1

        return {
            "Địa chỉ mạng": f"{self.network_address}/{self.mask}",
            "Dải địa chỉ": f"{IPAddressConvert.binary_to_ip(IPAddressConvert.decimal_to_binary(first_host_decimal))} - "
                           f"{IPAddressConvert.binary_to_ip(IPAddressConvert.decimal_to_binary(last_host_decimal))}",
            "Địa chỉ broadcast": self.broadcast_address,
            "Số lượng host": self.calculate_num_hosts(self.mask),
        }

class CIDR(Subnetting):
    def __init__(self, ip, mask):
        super().__init__(ip, mask)
        self.prefix_length = None

    def calculate_subnets(self, num_subnets):
        total = self.calculate_num_hosts(self.mask) + 2      
        if self.floor_log2(total/num_subnets) < 2:
            raise ValueError(f"Không thể chia vì với {num_subnets} mạng con thì mỗi mạng có 0 địa chỉ khả dụng .")
        else:
            self.prefix_length = 32 - self.floor_log2(total/num_subnets)        
        subnets = []
        subnet_size = 2 ** (32 - self.prefix_length)

        for i in range(num_subnets):
            network_decimal = IPAddressConvert.binary_to_decimal(IPAddressConvert.ip_to_binary(self.network_address)) + i * subnet_size
            subnet_ip = IPAddressConvert.binary_to_ip(IPAddressConvert.decimal_to_binary(network_decimal))
            subnet = Subnetting(subnet_ip, self.prefix_length)
            subnets.append(subnet.get_network_details())
        return subnets

class VLSM(Subnetting):
    def __init__(self, ip, mask):
        super().__init__(ip, mask)
        self.prefix_length = None
        self.available_network = None
        
    def calculate_subnets(self, host_requirements):
        host_requirements.sort(reverse=True)
        subnets = []
        self.available_network = self.network_address

        for i, hosts in enumerate(host_requirements):
            if i>=1:
                prefix_new = 32 - self.ceil_log2(hosts+2)
                prefix_old = self.prefix_length
                if (prefix_new == prefix_old or prefix_new - prefix_old==1):
                    self.prefix_length = prefix_old
                else:
                    self.prefix_length = prefix_new 
            else:
                required_size = self.ceil_log2(hosts+2)
                self.prefix_length = 32 - required_size
            if 2**(32 - self.prefix_length) > 2**(32 - self.mask):
                raise ValueError("Không đủ địa chỉ để cấp phát cho yêu cầu.")            
            subnet = Subnetting(self.available_network, self.prefix_length)
            subnets.append(subnet.get_network_details())

            next_network_decimal = IPAddressConvert.binary_to_decimal(IPAddressConvert.ip_to_binary(subnet.broadcast_address)) + 1
            self.available_network = IPAddressConvert.binary_to_ip(IPAddressConvert.decimal_to_binary(next_network_decimal))
        return subnets

def is_ip(ip):
    octets = ip.split('.')
    if len(octets) != 4:
        return False
    for octet in octets:
        if not (0 <= int(octet) <= 255):
            return False
    return True

def is_mask(mask):
    return 0 < int(mask) <= 32

if __name__ == "__main__":
    mode = input("Chọn chế độ (CIDR/VLSM): ").strip().upper()
    ip_mask = input("Nhập địa chỉ IP và mặt nạ mạng (VD: 192.168.1.0/24): ").strip()

    try:
        ip, mask = ip_mask.split('/')
        if not is_ip(ip):
            raise ValueError("Địa chỉ IP không hợp lệ.")
        if not is_mask(mask):
            raise ValueError("Mặt nạ mạng không hợp lệ.")
        mask = int(mask)  # Chuyển mặt nạ mạng thành số nguyên
    except ValueError as e:
        print(f"Lỗi: {e}")
        exit(1)

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
