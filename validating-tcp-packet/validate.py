def main():
    for i in range(10):
        with open(f"tcp_addrs_{i}.txt") as f:
            text = f.read()

        src_ip, dst_ip = text.split()
        src_ip_bytestring = convert_ip_to_bytestring(src_ip)
        dst_ip_bytestring = convert_ip_to_bytestring(dst_ip)

        with open(f"tcp_data_{i}.dat", "rb") as f:
            tcp_data = f.read()
    
        pseudo_header = create_pseudo_header(src_ip_bytestring, dst_ip_bytestring, tcp_data)
        tcp_checksum = int.from_bytes(tcp_data[16:18], "big")
        tcp_zero_checksum = tcp_data[:16] + b"\x00\x00" + tcp_data[18:]

        if len(tcp_zero_checksum) % 2 == 1:
            tcp_zero_checksum += b"\x00"
        
        checksum = calculate_checksum(pseudo_header, tcp_zero_checksum)
        print("PASS") if checksum == tcp_checksum else print("FAIL")
    

def convert_ip_to_bytestring(ip):
    octets = ip.split(".")
    bytestring = b""

    for octet in octets:
        bytestring += int(octet).to_bytes()
        
    return bytestring


def create_pseudo_header(src_ip, dst_ip, tcp_data):
    z = b"\x00"
    p = b"\x06"
    tcp_length = len(tcp_data).to_bytes(2, "big")
    return src_ip + dst_ip + z + p + tcp_length


def calculate_checksum(pseudo_header, tcp_data):
    data = pseudo_header + tcp_data 
    offset = 0
    total = 0
    
    while offset < len(data):
        word = int.from_bytes(data[offset:offset + 2], "big")

        total += word
        total = (total & 0xffff) + (total >> 16)

        offset += 2

    return (~total) & 0xffff


if __name__ == "__main__":
    main()
