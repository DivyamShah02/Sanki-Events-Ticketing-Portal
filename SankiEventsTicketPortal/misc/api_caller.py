import requests
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()
base_url = 'http://127.0.0.1:8000/'

def create_admin_user():
    url = base_url + 'user/user-api/'

    data = {
        'name': 'Admin',
        'password':'Admin@123',
        'contact_number': '0987654321',
        'email': 'admin@dynamiclabz.net',
        'role': 'admin',  
    }

    response = requests.post(url, data=data)

    return response

def login_admin_user():
    url = base_url + 'user/login-api/'

    data = {
        'email': 'admin@dynamiclabz.net',        
        'password':'Admin@123',
    }

    response = requests.post(url, data=data)

    return response


#############################################
def create_user(name, contact_number, email):
    url = base_url + 'user/user-api/'

    data = {
        'name': name,
        'password': '12345',
        'contact_number': contact_number,
        'email': email,
        'role': 'reseller',
    }

    response = requests.post(url, data=data)

    return response


def create_event(event_name, event_details, event_venue, event_date_range, digital_pass):
    url = base_url + 'event/event-api/'

    data = {
        'event_name': event_name,
        'event_details': event_details,
        'event_venue': event_venue,
        'event_date_range': event_date_range,
        'digital_pass': digital_pass,
    }

    response = requests.post(url, data=data)

    print(response.text)
    return response

def get_all_users():
    url = base_url + 'user/get-all-user-api/'

    response = requests.get(url)

    return response

def get_fake_users(count):
    users = []
    for _ in range(count):
        user = {
            "name": fake.name(),
            "contact_number": str(random.randint(6000000000, 9999999999)),
            "email": fake.email()
        }
        users.append(user)
    return users

def generate_event():
    start_date = fake.date_between(start_date="today", end_date="+30d")  # Event starts within 30 days
    end_date = start_date + timedelta(days=random.randint(1, 5))  # Lasts between 1 to 5 days
    return {
        "event_name": fake.catch_phrase(),  # Generates a random event name
        "event_details": fake.sentence(nb_words=10),  # Short event details
        "event_venue": fake.company(),  # Random venue name
        "event_date_range": f"{start_date} | {end_date}",  # Start and end date
        "digital_pass": random.choice([True, False])  # Randomly assign True or False
    }

def generate_sale():
    return {
        "qty": random.randint(1, 10),  # Random quantity between 1 and 10
        "amount": int(round(random.uniform(100, 5000), 0)),  # Random amount between 100 and 5000
        "sold_date": fake.date_between(start_date="-30d", end_date="today"),  # Sale date within the last 30 days
        "customer_name": fake.name(),
        "customer_email": fake.email(),
        "customer_number": str(random.randint(6000000000, 9999999999))  # 10-digit mobile number
    }

def create_sale(seller_id, event_date_id, event_id, qty, amount, sold_date, customer_name, customer_email, customer_number):
    url = base_url + 'ticket/ticket-api/'

    data = {
        'seller_id': seller_id,
        'event_date_id': event_date_id,
        'event_id': event_id,
        'qty': qty,
        'amount': amount,
        'sold_date': sold_date,
        'customer_name': customer_name,
        'customer_email': customer_email,
        'customer_number': customer_number
    }

    response = requests.post(url, data=data)

    print(response.text)
    return response

if __name__ == '__main__':
    print('Hello')

    # Create fake users
    # user_created = []
    # users = get_fake_users(count=10)
    # for user in users:
    #     created_user = create_user(name=user['name'], contact_number=user['contact_number'], email=user['email'])
    #     user_created.append(create_user)
    
    # Get all users
    # all_users = get_all_users()
    # print(all_users.text)

    # Create events
    # events = [generate_event() for _ in range(10)]
    # # Print generated events
    # for event in events:
    #     print(event['event_date_range'])
    #     create_event(event['event_name'], event['event_details'], event['event_venue'], event['event_date_range'], event['digital_pass'])


    all_user_id = ['RE8966010997', 'RE2815871606', 'RE5579018657', 'RE0578358042', 'RE1636570632', 'RE9430561279', 'RE7481137307', 'RE5919868826', 'RE6872970841', 'RE8903939796']
    
    # ('event_date_id', 'event_id')
    events_list = [('5425925566', '7549422032'), ('8049902493', '7549422032'), ('0327218706', '7549422032'), ('0451034903', '9236553342'), ('6495039018', '9236553342'), ('8911267532', '9236553342'), ('6379683612', '9236553342'), ('2764020294', '9236553342'), ('1049258962', '9236553342'), ('0359197625', '9997039449'), ('8795280032', '9997039449'), ('6650080605', '0476293028'), ('5336178800', '0476293028'), ('9254786999', '0476293028'), ('8423818089', '0476293028'), ('3415695827', '0476293028'), ('3082677954', '0476293028'), ('7980973030', '0427036336'), ('7631235867', '0427036336'), ('2868994968', '0427036336'), ('3445784380', '0427036336'), ('6856478020', '0427036336'), ('3347500935', '9432771779'), ('7608671479', '9432771779'), ('2506950228', '9432771779'), ('8961715406', '9432771779'), ('9132977168', '5135077085'), ('6434713858', '5135077085'), ('0188504258', '5135077085'), ('4982989143', '5135077085'), ('7058983232', '5135077085'), ('8866441981', '1607231641'), ('2382574386', '1607231641'), ('5771289170', '1607231641'), ('9994367082', '1607231641'), ('4677220429', '1607231641'), ('2124117078', '1607231641'), ('3278351348', '0382159439'), ('9068093877', '0382159439'), ('8716646441', '0753421909'), ('0798232465', '0753421909'), ('1727486681', '0753421909'), ('3592843088', '0753421909'), ('0804444194', '0753421909'), ('0319252091', '4958081970'), ('5990032437', '4958081970'), ('6835237337', '4958081970'), ('0850802038', '4958081970'), ('8640549204', '4958081970')]
    
    ['seller_id', 'event_date_id', 'event_id', 'qty', 'amount', 'sold_date', 'customer_name', 'customer_email', 'customer_number']
    sales = [generate_sale() for _ in range(20)]
    
    for sale in sales:
        seller_id = random.choice(all_user_id)
        print(seller_id)
        events_details = random.choice(events_list)

        event_date_id = events_details[0]
        event_id = events_details[1]

        new_sale = create_sale(seller_id, event_date_id, event_id, sale['qty'], sale['amount'], sale['sold_date'], sale['customer_name'], sale['customer_email'], sale['customer_number'])



    import pdb; pdb.set_trace()
    print('end')
    
    # create_event_respone = create_event()
    # print(create_event_respone.text)
