import asyncio
import subprocess
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def ping_ip(ip, timeout=2):
    """
    Pings the specified IP address to check if it's reachable.
    The ping will timeout if no response is received within the given time.

    Args:
        ip (str): The IP address to ping.
        timeout (int): Timeout duration in seconds for the ping.

    Returns:
        bool: True if the IP is reachable, False if not (including timeout).
    """
    try:
        result = await asyncio.to_thread(subprocess.run, ['ping', '-c', '1', '-W', str(timeout), ip],
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception as e:
        logger.warning(f"Ping failed for {ip}: {e}")
        return False


async def check_ips(ips):
    """
    Checks the reachability of a list of IP addresses by pinging each one.
    Prints the IPs that are not reachable.

    Args:
        ips (list): List of IP addresses to check.
    """
    unreachable_ips = []
    tasks = []

    for ip in ips:
        tasks.append(check_single_ip(ip, unreachable_ips))

    await asyncio.gather(*tasks)

    if unreachable_ips:
        logger.info("Unreachable IPs:")
        for ip in unreachable_ips:
            logger.info(f"- {ip}")
    else:
        logger.info("All IPs are reachable!")


async def check_single_ip(ip, unreachable_ips):
    """
    Pings a single IP address and adds it to the unreachable_ips list if it's not reachable.

    Args:
        ip (str): The IP address to ping.
        unreachable_ips (list): List to store unreachable IPs.
    """
    if not await ping_ip(ip):
        unreachable_ips.append(ip)


async def monitor_ips():
    """
    Continuously monitors a list of IP addresses by pinging them at regular intervals.
    """

    ips = [f"172.29.0.{i}" for i in range(1, 513)]

    while True:
        logger.info("Starting new round of IP checks...")
        await check_ips(ips)
        logger.info("Waiting for next round...\n")

        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(monitor_ips())
