import os
import random

import requests
from faker import Faker

BASE_URL = "http://localhost:8000/api"
IMAGES_FOLDER = 'images'  # Path to the folder containing images

fake = Faker()

# Global lists to store product IDs
flight_ids = []
hotel_ids = []
activity_ids = []

# Global lists to store image IDs
flight_image_ids = []
hotel_image_ids = []
activity_image_ids = []
restaurant_image_ids = []

# Helper functions
def upload_image(session, access_token, image_path):
    """Upload an image and return its ID."""
    with open(image_path, 'rb') as f:
        files = {'file': ('image.jpg', f, 'image/jpeg')}
        headers = {'Authorization': f'Bearer {access_token}'}
        response = session.post(f'{BASE_URL}/image/upload/', files=files, headers=headers)

    if response.status_code == 200:
        image_id = response.json().get('imageId')
        print(f"Uploaded image: {image_path} (ID: {image_id})")
        return image_id
    else:
        print(f"Failed to upload image: {image_path}", response.json())
        return None

def upload_all_images(session, access_token):
    """Upload all images from the folders and store their IDs."""
    global flight_image_ids, hotel_image_ids, activity_image_ids, restaurant_image_ids

    # Upload flight images
    flight_folder = os.path.join(IMAGES_FOLDER, 'flights')
    if os.path.exists(flight_folder):
        for image_file in os.listdir(flight_folder):
            if image_file.endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(flight_folder, image_file)
                image_id = upload_image(session, access_token, image_path)
                if image_id:
                    flight_image_ids.append(image_id)

    # Upload hotel images
    hotel_folder = os.path.join(IMAGES_FOLDER, 'hotels')
    if os.path.exists(hotel_folder):
        for image_file in os.listdir(hotel_folder):
            if image_file.endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(hotel_folder, image_file)
                image_id = upload_image(session, access_token, image_path)
                if image_id:
                    hotel_image_ids.append(image_id)

    # Upload activity images
    tourism_folder = os.path.join(IMAGES_FOLDER, 'tourism')
    if os.path.exists(tourism_folder):
        for image_file in os.listdir(tourism_folder):
            if image_file.endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(tourism_folder, image_file)
                image_id = upload_image(session, access_token, image_path)
                if image_id:
                    activity_image_ids.append(image_id)

    # Upload restaurant images
    restaurant_folder = os.path.join(IMAGES_FOLDER, 'restaurants')
    if os.path.exists(restaurant_folder):
        for image_file in os.listdir(restaurant_folder):
            if image_file.endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(restaurant_folder, image_file)
                image_id = upload_image(session, access_token, image_path)
                if image_id:
                    restaurant_image_ids.append(image_id)

    print("All images uploaded successfully.")

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

def create_products(session, access_token, num_products, category):
    global flight_image_ids, hotel_image_ids, activity_image_ids, restaurant_image_ids

    for _ in range(num_products):
        # Select image IDs based on the category
        if category == 'flight':
            image_ids = random.sample(flight_image_ids, min(len(flight_image_ids), 3))
        elif category == 'hotel':
            image_ids = random.sample(hotel_image_ids, min(len(hotel_image_ids), 3))
        elif category == 'tourism':
            image_ids = random.sample(activity_image_ids, min(len(activity_image_ids), 3))
        elif category == 'restaurant':
            image_ids = random.sample(restaurant_image_ids, min(len(restaurant_image_ids), 3))
        else:
            image_ids = []

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
        headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json', 'Accept': 'application/json'}
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
        image_ids = random.sample(activity_image_ids, min(len(activity_image_ids), 3))
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
    global flight_image_ids, hotel_image_ids, activity_image_ids, restaurant_image_ids

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
                # Upload all images for this provider
                if i == 0:
                    upload_all_images(session, access_token)

                # Create products for this provider
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