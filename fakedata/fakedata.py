import os
import random
import requests
from faker import Faker
from io import BytesIO

BASE_URL = "http://localhost:8000/api"

fake = Faker()

# Helper functions
def download_random_image():
    url = f'https://picsum.photos/200/300'
    response = requests.get(url)
    if response.status_code == 200:
        return BytesIO(response.content)
    return None

def upload_image(session, access_token):
    image_file = download_random_image()
    if not image_file:
        print("Failed to download image.")
        return None

    files = {'file': ('image.jpg', image_file, 'image/jpeg')}
    headers = {'Authorization': f'Bearer {access_token}'}  # Add JWT token to headers
    response = session.post(f'{BASE_URL}/image/upload/', files=files, headers=headers)

    if response.status_code == 200:
        image_id = response.json().get('imageId')
        print(f"Uploaded image with ID: {image_id}")
        return image_id
    else:
        print("Failed to upload image.", response.json())
    return None

# Register users
def register_user(session, role, email, password):
    data = {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "phone_number": fake.phone_number(),
        "email": email,
        "national_id": fake.ssn(),
        "password": password
    }
    response = session.post(f'{BASE_URL}/auth/register/{role}/', json=data)
    if response.status_code == 200:
        print(f"{role.capitalize()} registered successfully.")
    else:
        print(f"Failed to register {role}.", response.text)

# Login as a user
def login(session, phone_number, password):
    data = {"phone_number": phone_number, "password": password}
    response = session.post(f'{BASE_URL}/auth/login/', json=data)
    if response.status_code == 200:
        print("Logged in successfully.")
        return response.json().get('data', {}).get('access')  # Return the access token
    else:
        print("Failed to log in.", response.json())
        return None

# Create products
def create_products(session, access_token, num_products):
    categories = ['flight', 'train', 'bus', 'hotel', 'tourism', 'restaurant']
    for _ in range(num_products):
        image_ids = [upload_image(session, access_token) for _ in range(random.randint(1, 3))]
        image_ids = [img_id for img_id in image_ids if img_id]
        data = {
            "name": fake.company(),
            "summary": fake.catch_phrase(),
            "description": fake.text(),
            "price": round(random.uniform(10, 500), 2),
            "discount": round(random.uniform(0, 50), 2),
            "stock": random.randint(1, 100),
            "category": random.choice(categories),
            "images": image_ids,
        }
        headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json', 'Accept': 'application/json'}  # Add JWT token to headers
        response = session.post(f'{BASE_URL}/product/', json=data, headers=headers)
        if response.status_code == 201:
            print(f"Product created: {data['name']}")
        else:
            print("Failed to create product.", response.json())

# Create trip packages
def create_trip_packages(session, access_token, num_packages):
    for _ in range(num_packages):
        image_ids = [upload_image(session, access_token) for _ in range(random.randint(1, 3))]
        image_ids = [img_id for img_id in image_ids if img_id]
        data = {
            "name": fake.company(),
            "photos": image_ids,
            "flight": random.randint(1, 10),
            "hotel": random.randint(1, 10),
            "activities": [random.randint(1, 10) for _ in range(random.randint(1, 3))],
            "price": round(random.uniform(100, 2000), 2),
            "start_date": "2025-03-01",
            "end_date": "2025-03-10",
            "available_units": random.randint(1, 50),
            "published": True,
            "description": fake.text()
        }
        headers = {'Authorization': f'Bearer {access_token}'}  # Add JWT token to headers
        response = session.post(f'{BASE_URL}/package/', json=data, headers=headers)
        if response.status_code == 201:
            print(f"Trip package created: {data['name']}")
        else:
            print("Failed to create trip package.", response.json())

def send_verification_code(phone_number):
    response = requests.post(f'{BASE_URL}/auth/send-verification-code/', json={'phone_number': phone_number})
    if response.status_code == 200:
        print(f'Verification code sent to {phone_number}')
    else:
        print(f'Failed to send verification code to {phone_number}: {response.text}')
    return response

def verify_code(phone_number, code='123456'):
    response = requests.post(f'{BASE_URL}/auth/verify-code/', json={'phone_number': phone_number, 'code': code})
    if response.status_code == 200:
        print(f'Verification successful for {phone_number}')
    else:
        print(f'Failed verification for {phone_number}: {response.text}')
    return response

def register_customer(phone_number, password='password123'):
    data = {
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'phone_number': phone_number,
        'email': fake.email(),
        'national_id': str(random.randint(1000000000, 9999999999)),
        'password': password
    }
    response = requests.post(f'{BASE_URL}/auth/register/customer/', json=data)
    if response.status_code == 200:
        print(f'Customer {phone_number} registered successfully')
    else:
        print(f'Failed to register customer {phone_number}: {response.text}')
    return response

def register_provider(phone_number, password='password123'):
    data = {
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'phone_number': phone_number,
        'email': fake.email(),
        'national_id': str(random.randint(1000000000, 9999999999)),
        'password': password,
        'business_name': fake.company(),
        'business_address': fake.address(),
        'business_contact': fake.phone_number()[:15],
        'website_url': fake.url()
    }
    response = requests.post(f'{BASE_URL}/auth/register/provider/', json=data)
    if response.status_code == 200:
        print(f'Provider {phone_number} registered successfully')
    else:
        print(f'Failed to register provider {phone_number}: {response.text}')
    return response

def register_and_login_package_maker(session, email, password):
    register_user(session, "package-maker", email, password)
    access_token = login(session, email, password)
    return access_token

# Main execution
def main():
    password = "password123"
    num_providers = 3
    num_products_per_provider = 10
    num_package_makers = 2
    num_packages_per_maker = 5
    num_buyers = 3

    with requests.Session() as session:
        # Create providers and products
        for i in range(num_providers):
            phone_number = f'0912{random.randint(1000000, 9999999)}'
            send_verification_code(phone_number)
            verify_code(phone_number)
            register_provider(phone_number)
            access_token = login(session, phone_number, password)  # Get access token
            if access_token:
                create_products(session, access_token, num_products_per_provider)

            # Create package makers and trip packages
            for i in range(num_package_makers):
                email = f"packagemaker{i}@example.com"
                access_token = register_and_login_package_maker(session, email, password)
                if access_token:
                    create_trip_packages(session, access_token, num_packages_per_maker)

        # Create buyers
        for i in range(num_buyers):
            email = f"buyer{i}@example.com"
            register_user(session, "buyer", email, password)
            login(session, email, password)

if __name__ == '__main__':
    main()