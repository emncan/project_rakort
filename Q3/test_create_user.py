import httpx
from faker import Faker
import asyncio

BASE_URL = "http://127.0.0.1:8000"

fake = Faker()


async def create_user(
        client: httpx.AsyncClient,
        username: str,
        email: str,
        full_name: str,
        address: str,
        phone: str):

    data = {
        "username": username,
        "email": email,
        "full_name": full_name,
        "address": address,
        "phone": phone
    }
    response = await client.post(f"{BASE_URL}/users/", json=data)
    return response


async def generate_and_create_users(num_users: int):
    async with httpx.AsyncClient() as client:
        tasks = []
        for _ in range(num_users):
            username = fake.user_name()
            email = fake.email()
            full_name = fake.name()
            address = fake.address()
            phone = fake.phone_number()

            task = create_user(
                client,
                username,
                email,
                full_name,
                address,
                phone)
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        for response in responses:
            if response.status_code == 200:
                print("User created successfully!")
            else:
                print(
                    f"Failed to create user: {response.status_code} - {response.text}")


async def main():
    await generate_and_create_users(100)


if __name__ == "__main__":
    asyncio.run(main())
