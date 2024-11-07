import asyncio
import asyncssh
import logging
from typing import List

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class RemoteSSHClient:
    """
    SSH client for connecting to remote servers and executing commands with optimized connection pooling.
    """

    def __init__(self, username: str, password: str, port: int = 22):
        """
        Initializes the SSH client with login credentials.

        Args:
            username (str): SSH username.
            password (str): SSH password.
            port (int): SSH port (default is 22).
        """
        self.username = username
        self.password = password
        self.port = port

    async def connect(self, host: str):
        """
        Establishes an SSH connection to a given host.

        Args:
            host (str): The IP address or hostname of the server.

        Returns:
            asyncssh.SSHClientConnection: The SSH connection object.
        """
        logger.info(f"Attempting to connect to {host}...")
        try:
            connection = await asyncssh.connect(
                host, port=self.port, username=self.username, password=self.password
            )
            logger.info(f"Successfully connected to {host}")
            return connection
        except Exception as e:
            logger.error(f"Failed to connect to {host}: {e}")
            raise

    async def execute_command(self, connection, command: str) -> str:
        """
        Executes a command on an existing SSH connection.

        Args:
            connection (asyncssh.SSHClientConnection): The SSH connection object.
            command (str): The command to execute on the server.

        Returns:
            str: The output of the command.
        """
        logger.info(f"Executing command '{command}'...")
        try:
            async with connection.create_process(command) as process:
                stdout, stderr = await process.communicate()
                if stderr:
                    logger.error(f"Error executing command: {stderr}")
                return stdout
        except Exception as e:
            logger.error(f"Error during command execution: {e}")
            return ""

    async def execute_on_network(self, hosts: List[str], command: str):
        """
        Executes a command on multiple hosts in parallel using a connection pool.

        Args:
            hosts (List[str]): List of IP addresses or hostnames.
            command (str): The command to execute on each server.
        """
        connections = {}
        try:
            for host in hosts:
                connections[host] = await self.connect(host)

            tasks = [
                self.execute_command(
                    connections[host],
                    command) for host in hosts]
            results = await asyncio.gather(*tasks)

            for host, result in zip(hosts, results):
                logger.info(f"Output from {host}:\n{result}")

        finally:
            for host, connection in connections.items():
                connection.close()
                await connection.wait_closed()
                logger.info(f"Connection to {host} closed.")


if __name__ == "__main__":
    hosts = ["192.168.1.10", "192.168.1.11", "192.168.1.12"]
    command = "uname -a"
    username = "your_username"
    password = "your_password"

    ssh_client = RemoteSSHClient(username=username, password=password)
    asyncio.run(ssh_client.execute_on_network(hosts, command))
