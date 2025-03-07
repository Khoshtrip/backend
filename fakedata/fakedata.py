import os
import random
import requests
from faker import Faker
from io import BytesIO

BASE_URL = "http://localhost:8000/api"

fake = Faker()

# Global lists to store product IDs
flight_ids = []
hotel_ids = []
activity_ids = []

# Helper functions
def download_random_image():
    url = f'https://picsum.photos/100/100'
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
def create_products(session, access_token, num_products, category):
    global flight_ids, hotel_ids, activity_ids

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
            "category": category,
            "images": image_ids,
        }
        headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json', 'Accept': 'application/json'}  # Add JWT token to headers
        response = session.post(f'{BASE_URL}/product/', json=data, headers=headers)
        if response.status_code == 201:
            product_id = response.json().get('data').get('id')
            print(f"Product created: {data['name']} (ID: {product_id})")

            # Store the product ID in the appropriate global list
            if category == 'flight':
                flight_ids.append(product_id)
            elif category == 'hotel':
                hotel_ids.append(product_id)
            elif category == 'tourism':
                activity_ids.append(product_id)
            elif category == 'restaurant':
                activity_ids.append(product_id)
        else:
            print("Failed to create product.", response.json())

# Create trip packages
def create_trip_packages(session, access_token, num_packages):
    global flight_ids, hotel_ids, activity_ids

    for _ in range(num_packages):
        image_ids = [upload_image(session, access_token) for _ in range(random.randint(1, 3))]
        image_ids = [img_id for img_id in image_ids if img_id]
        data = {
            "name": fake.company(),
            "photos": image_ids,
            "flight": random.choice(flight_ids),  # Use a valid flight ID
            "hotel": random.choice(hotel_ids),    # Use a valid hotel ID
            "activities": random.sample(activity_ids, random.randint(1, 3)),  # Use valid activity IDs
            "price": round(random.uniform(100, 2000), 2),
            "start_date": "2025-03-01",
            "end_date": "2025-03-10",
            "available_units": random.randint(1, 50),
            "published": True,
            "description": fake.text()
        }
        headers = {'Authorization': f'Bearer {access_token}'}
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

def register_package_maker(phone_number, password='password123'):
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
    response = requests.post(f'{BASE_URL}/auth/register/package-maker/', json=data)
    if response.status_code == 200:
        print(f'Package Maker {phone_number} registered successfully')
    else:
        print(f'Failed to register package maker {phone_number}: {response.text}')
    return response

# Main execution
def main():
    global flight_ids, hotel_ids, activity_ids

    password = "password123"
    num_providers = 3
    num_products_per_provider = 1
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
                # Create flights, hotels, and activities
                create_products(session, access_token, num_products_per_provider, 'flight')
                create_products(session, access_token, num_products_per_provider, 'hotel')
                create_products(session, access_token, num_products_per_provider, 'tourism')
                create_products(session, access_token, num_products_per_provider, 'restaurant')

        # Create package makers and trip packages
        for i in range(num_package_makers):
            phone_number = f'0913{random.randint(1000000, 9999999)}'
            send_verification_code(phone_number)
            verify_code(phone_number)
            register_package_maker(phone_number)
            access_token = login(session, phone_number, password)  # Get access token
            if access_token:
                create_trip_packages(session, access_token, num_packages_per_maker)

        # Create buyers
        for i in range(num_buyers):
            phone_number = f'0914{random.randint(1000000, 9999999)}'
            send_verification_code(phone_number)
            verify_code(phone_number)
            register_customer(phone_number)

if __name__ == '__main__':
    main()