import asyncio
import asyncssh
import sqlite3
import ipaddress
import subprocess
import logging
from aiohttp import ClientSession, TCPConnector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_db():
    """
    Creates the SQLite database and the necessary table to store IP addresses
    and their statuses (active, SSH connected).
    """
    conn = sqlite3.connect('ip_addresses.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS ip_addresses (
            ip TEXT PRIMARY KEY,
            is_active INTEGER,
            is_ssh_connected INTEGER
        )
    ''')
    conn.commit()
    conn.close()


def save_ip(ip, is_active, is_ssh_connected):
    """
    Saves the IP address along with its status (active, SSH connected) in the database.

    Args:
        ip (str): The IP address to store.
        is_active (int): 1 if the IP is active, 0 if not.
        is_ssh_connected (int): 1 if SSH connection was successful, 0 if not.
    """
    conn = sqlite3.connect('ip_addresses.db')
    c = conn.cursor()
    c.execute(
        'INSERT OR REPLACE INTO ip_addresses (ip, is_active, is_ssh_connected) VALUES (?, ?, ?)',
        (ip,
         is_active,
         is_ssh_connected))
    conn.commit()
    conn.close()


async def ping_ip(ip):
    """
    Pings the specified IP address to check if it's active.

    Args:
        ip (str): The IP address to ping.

    Returns:
        bool: True if the IP is active (responds to ping), False otherwise.
    """
    try:
        result = await asyncio.to_thread(subprocess.run, ['ping', '-c', '1', ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception as e:
        logger.warning(f"Ping failed: {ip} - Error: {e}")
        return False


async def ssh_connect(ip, username='root', password='password', retries=3):
    """
    Attempts to establish an SSH connection to the given IP address.

    Args:
        ip (str): The IP address to connect to via SSH.
        username (str): The username for SSH login.
        password (str): The password for SSH login.
        retries (int): The number of retries if the connection fails.

    Returns:
        bool: True if SSH connection was successful, False otherwise.
    """
    attempt = 0
    while attempt < retries:
        try:
            async with asyncssh.connect(ip, username=username, password=password) as conn:
                logger.info(f"SSH connection successful: {ip}")
                return True
        except (asyncssh.Error, OSError) as e:
            logger.warning(
                f"SSH connection failed: {ip} - Attempt {attempt + 1}/{retries}")
            attempt += 1
            await asyncio.sleep(1)
    return False


async def process_ip(ip):
    """
    Processes a given IP address: checks if it is active via ping, and attempts
    to establish an SSH connection if it's active.

    Args:
        ip (str): The IP address to process.
    """
    is_active = await ping_ip(ip)

    if is_active:
        logger.info(f"IP is active: {ip}")
        save_ip(ip, 1, 0)
        is_ssh_connected = await ssh_connect(ip)
        save_ip(ip, 1, 1 if is_ssh_connected else 0)
    else:
        logger.info(f"IP is not active: {ip}")
        save_ip(ip, 0, 0)


async def main():
    """
    Main function that iterates over all IP addresses in the 172.29.0.0/16 network
    and processes them asynchronously (ping check and SSH connection).
    """
    network = ipaddress.IPv4Network("172.29.0.0/16")
    tasks = []

    for ip in network.hosts():
        tasks.append(process_ip(str(ip)))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    create_db()
    asyncio.run(main())
