import requests
import datetime
import os
import random
import string


# DOMAIN = "http://127.0.0.1:8000"
DOMAIN = "https://www.sankievents.in"

START = 10
END = 100
event_date_id = '2049580382'
event_id = '8786278381'
if not os.path.exists(event_date_id):
    os.mkdir(event_date_id)


session = requests.Session()


def custom_get_csrf_token():
    return session.cookies.get("csrftoken")


def custom_login(email, password):
    response = session.post(f"{DOMAIN}/user/login-api/", json={
        "email": email,
        "password": password
    })
    print(response.text)
    print("🔐 Login:", response.status_code)
    return response.json()


def custom_set_headers():
    csrf_token = custom_get_csrf_token()
    return {
        "X-CSRFToken": csrf_token
    }

def user_details():
    response = session.get(f"{DOMAIN}/user/user-detail-api/")    
    return response.json().get("data", [])

def get_tickets_details(event_date_data, headers):
    response = session.get(f"{DOMAIN}/ticket/download-tickets-details",params={"event_date_id": event_date_data}, headers=headers)
    data = response.json().get("data", [])
    print(response.text)
    return data

def get_ticket(ticket_id, headers):
    response = session.get(f"{DOMAIN}/ticket/generate-ticket-pass-api", params={"ticket_id": ticket_id, 'event_id': event_id}, headers=headers)
    if response.status_code == 200:
        with open(f"{event_date_id}/{ticket_id}.png", "wb") as f:
            f.write(response.content)
        print("Image saved successfully as Event_Pass.png")
    else:
        print(f"Failed to fetch image. Status code: {response.status_code}")    

def get_direct_ticket(ticket_id, headers):
    response = session.get(f"{DOMAIN}/ticket/ticket-pass-api",params={"ticket_id": ticket_id}, headers=headers)
    file_path = f"{ticket_id}.png"
    print()
    if response.status_code == 200:
        with open(file_path, "wb") as f:
            f.write(response.content)
        print("Image saved successfully as Event_Pass.png")
    else:
        print(f"Failed to fetch image. Status code: {response.status_code}")    
    return file_path    

def logout(headers):
    response = session.post(f"{DOMAIN}/user/logout-api/", headers=headers)
    print("🔓 Logout:", response.status_code)
    # print("Response:", response.text)

def generate_unique_codes(start, end):
    total = end - start + 1
    codes = set()
    results = []

    # Generate unique 3-character prefixes
    while len(codes) < total:
        prefix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        if prefix not in codes:
            codes.add(prefix)

    sorted_codes = sorted(codes)  # Optional: sort for predictable output

    for i, prefix in enumerate(sorted_codes):
        number_suffix = str(start + i).zfill(3)
        full_code = prefix + number_suffix
        results.append(full_code)

    return results


if __name__ == "__main__":
    print("\n🔐 Logging in as Admin...")
    custom_login("divyam@dynamiclabz.net", "12345")
    headers = custom_set_headers()

    # data = get_tickets_details(event_date_data=event_date_id,headers=headers)
    # print(data)

    unique_codes = generate_unique_codes(START, END)
    for ticket_data in unique_codes:
        get_ticket(ticket_id=ticket_data, headers=headers)

    
    print("\n🔓 Logging out...")
    logout(headers)
