import asyncio
import psutil
import aiosqlite
import sqlite3
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s")

update_queue = asyncio.Queue()


async def async_update_batch():
    """
    Processes updates in batches from the update_queue to reduce database access frequency.
    """
    async with aiosqlite.connect("tasks.db", timeout=30) as conn:
        while True:
            updates = []
            # Wait until we have a batch of updates or a short timeout
            try:
                while len(updates) < 100:
                    task_update = await asyncio.wait_for(update_queue.get(), timeout=5)
                    updates.append(task_update)
                    update_queue.task_done()
            except asyncio.TimeoutError:
                pass

            if updates:
                async with conn.execute("BEGIN"):
                    for task_id, cpu_usage, memory_usage in updates:
                        await conn.execute(
                            "UPDATE tasks SET status = 'completed', cpu_usage = ?, memory_usage = ? WHERE id = ?",
                            (cpu_usage, memory_usage, task_id)
                        )
                    await conn.commit()
                logging.info(f"Batch update of {len(updates)} tasks completed")


async def process_task(task_id):
    """
    Simulates task processing, retrieves CPU and memory usage, and adds the result to update_queue.

    Args:
        task_id (int): The ID of the task to be processed.
    """
    logging.info(f"Starting task {task_id}")
    process = psutil.Process()
    await asyncio.sleep(0.1)
    cpu_usage = process.cpu_percent()
    memory_usage = process.memory_info().rss / (1024 * 1024)
    await update_queue.put((task_id, cpu_usage, memory_usage))
    logging.info(
        f"Task {task_id} completed with CPU: {cpu_usage}% and Memory: {memory_usage} MB")


def setup_database():
    """
    Sets up the SQLite database and creates the tasks table if it does not exist.
    """
    conn = sqlite3.connect("tasks.db", timeout=30)
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, status TEXT, cpu_usage REAL, memory_usage REAL)")
    conn.commit()
    conn.close()
    logging.info(
        "Database setup completed and table created if it did not exist.")


def populate_tasks():
    """
    Populates the tasks table with 1000 tasks, each initialized with 'pending' status.
    """
    conn = sqlite3.connect("tasks.db", timeout=30)
    cursor = conn.cursor()
    for i in range(1000):
        cursor.execute(
            "INSERT INTO tasks (status, cpu_usage, memory_usage) VALUES ('pending', 0, 0)")
    conn.commit()
    conn.close()
    logging.info("Database populated with 1000 tasks.")


async def main():
    """
    Sets up the database, populates tasks, and initiates asynchronous task processing and batch updating.
    """
    logging.info("Starting main process")
    setup_database()
    populate_tasks()

    batch_update_task = asyncio.create_task(async_update_batch())

    tasks = [process_task(task_id) for task_id in range(1, 1001)]
    await asyncio.gather(*tasks)

    await update_queue.join()
    batch_update_task.cancel()
    logging.info("All tasks processed and database updated.")

if __name__ == "__main__":
    logging.info("Script started")
    asyncio.run(main())
    logging.info("Script finished")
