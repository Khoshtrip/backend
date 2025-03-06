import requests
import random
import time
from faker import Faker

# Configuration
BASE_URL = 'http://localhost:8000/api'  # Make this configurable
NUM_CUSTOMERS = 100  # Number of customers to create
NUM_PROVIDERS = 100  # Number of providers to create
DELAY = 0.01  # Delay between requests to avoid overloading the server

fake = Faker()

# Helper functions
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

# Main execution
for i in range(NUM_CUSTOMERS):
    phone_number = f'0912{random.randint(1000000, 9999999)}'
    send_verification_code(phone_number)
    time.sleep(DELAY)
    verify_code(phone_number)
    time.sleep(DELAY)
    register_customer(phone_number)
    time.sleep(DELAY)

for i in range(NUM_PROVIDERS):
    phone_number = f'0913{random.randint(1000000, 9999999)}'
    send_verification_code(phone_number)
    time.sleep(DELAY)
    verify_code(phone_number)
    time.sleep(DELAY)
    register_provider(phone_number)
    time.sleep(DELAY)

print('User generation completed.')
