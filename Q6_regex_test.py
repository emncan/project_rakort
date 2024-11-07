import re

patterns = {
    "client_identifier": r'OPTION: 61 \( 7\) Client-identifier (\S+)',
    "request_ip": r'OPTION: 50 \( 4\) Request IP address (\S+)',
    "vendor_class_identifier": r'OPTION: 60 \( \d+\) Vendor class identifier (\S+)',
    "host_name": r'OPTION: 12 \( \d+\) Host name (\S+)'}


def parse_test_data(data):
    """
    Parses the given DHCP data to extract the Client-identifier,
    Request IP address, Vendor class identifier, and Host name fields.

    Args:
        data (str): The raw DHCP data containing the option fields to parse.

    Returns:
        dict: A dictionary containing the extracted fields, with None for any missing data.
    """
    parsed_data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, data)
        parsed_data[key] = match.group(1) if match else None

    return parsed_data


if __name__ == "__main__":
    test_data = """
    TIME: 2023-08-24 17:46:37.098
    IP: 0.0.0.0 (96:4e:d7:51:42:de) > 255.255.255.255 (ff:ff:ff:ff:ff:ff)
    OP: 1 (BOOTPREQUEST)
    HTYPE: 1 (Ethernet)
    HLEN: 6
    HOPS: 0
    XID: 54330ee6
    SECS: 0
    FLAGS: 0
    CIADDR: 0.0.0.0
    YIADDR: 0.0.0.0
    SIADDR: 0.0.0.0
    GIADDR: 0.0.0.0
    CHADDR: 96:4e:d7:51:42:de:00:00:00:00:00:00:00:00:00:00
    SNAME: .
    FNAME: .
    OPTION: 53 ( 1) DHCP message type 3 (DHCPREQUEST)
    OPTION: 61 ( 7) Client-identifier 01:96:4e:d7:51:42:de
    OPTION: 50 ( 4) Request IP address 10.38.1.117
    OPTION: 57 ( 2) Maximum DHCP message size 1500
    OPTION: 12 ( 12) Host name OnePlus-9-5G
    OPTION: 55 ( 12) Parameter Request List 1 (Subnet mask)
    3 (Routers)
    6 (DNS server)
    15 (Domainname)
    26 (Interface MTU)
    """

    parsed_result = parse_test_data(test_data)
    print("Parsed Results:")
    for key, value in parsed_result.items():
        print(f"{key}: {value}")
