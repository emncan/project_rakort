import paramiko
import time
import re
import logging

logging.basicConfig(filename='dhcp_request_parser.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

ssh_host = 'your_ssh_host'
ssh_port = 22
ssh_user = 'your_username'
ssh_password = 'your_password'
ssh_command = 'your_ssh_command_to_get_data'


def parse_dhcp_request(data):
    """
    Parses the given DHCP data to extract the Client-identifier,
    Request IP address, Vendor class identifier, and Host name fields.

    Args:
        data (str): The raw DHCP data containing the option fields to parse.

    Returns:
        dict: A dictionary containing the extracted fields, with None for any missing data.
    """
    patterns = {
        "client_identifier": r'OPTION: 61 \( 7\) Client-identifier (\S+)',
        "request_ip": r'OPTION: 50 \( 4\) Request IP address (\S+)',
        "vendor_class_identifier": r'OPTION: 60 \( \d+\) Vendor class identifier (\S+)',
        "host_name": r'OPTION: 12 \( \d+\) Host name (\S+)'}

    parsed_data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, data)
        parsed_data[key] = match.group(1) if match else None

    return parsed_data


def listen_ssh_command():
    """
    Connects to the SSH server, listens for the specified data stream for 300 seconds,
    and parses DHCPREQUEST messages to extract relevant fields.

    The extracted data is written to a text file and logged for monitoring purposes.
    Any errors encountered during the process are also logged.

    Returns:
        None
    """
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            ssh_host,
            port=ssh_port,
            username=ssh_user,
            password=ssh_password)

        logging.info(
            f"SSH connection successfully established. Listening for data from {ssh_host}.")

        stdin, stdout, stderr = client.exec_command(ssh_command)

        start_time = time.time()
        with open("parsed_dhcp_requests.txt", "w") as file:
            while time.time() - start_time < 300:
                data = stdout.readline()
                if not data:
                    break

                if "OPTION: 53 ( 1) DHCP message type 3 (DHCPREQUEST)" in data:
                    parsed_data = parse_dhcp_request(data)

                    file.write(
                        f"Client Identifier: {
                            parsed_data['client_identifier']}\n")
                    file.write(
                        f"Request IP Address: {
                            parsed_data['request_ip']}\n")
                    file.write(
                        f"Vendor Class Identifier: {
                            parsed_data['vendor_class_identifier']}\n")
                    file.write(f"Host Name: {parsed_data['host_name']}\n")
                    file.write("-" * 40 + "\n")

                    logging.info(f"Data successfully parsed: {parsed_data}")

        logging.info("Data listening completed after 5 minutes.")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

    finally:
        client.close()
        logging.info("SSH connection closed.")


if __name__ == "__main__":
    listen_ssh_command()
