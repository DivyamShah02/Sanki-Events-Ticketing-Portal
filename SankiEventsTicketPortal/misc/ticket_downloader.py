import requests
import datetime
import os

# DOMAIN = "http://127.0.0.1:8000"
DOMAIN = "https://www.sankievents.in"

event_date_id = '2615673316'
if not os.path.exists(event_date_id):
    os.mkdir(event_date_id)


session = requests.Session()


def get_csrf_token():
    return session.cookies.get("csrftoken")


def login(email, password):
    response = session.post(f"{DOMAIN}/user/login-api/", json={
        "email": email,
        "password": password
    })
    print(response.text)
    print("🔐 Login:", response.status_code)
    return response.json()


def set_headers():
    csrf_token = get_csrf_token()
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
    response = session.get(f"{DOMAIN}/ticket/ticket-pass-api",params={"ticket_id": ticket_id}, headers=headers)
    if response.status_code == 200:
        with open(f"{event_date_id}/{ticket_id}.png", "wb") as f:
            f.write(response.content)
        print("Image saved successfully as Event_Pass.png")
    else:
        print(f"Failed to fetch image. Status code: {response.status_code}")    
    

def logout(headers):
    response = session.post(f"{DOMAIN}/user/logout-api/", headers=headers)
    print("🔓 Logout:", response.status_code)
    # print("Response:", response.text)

if __name__ == "__main__":
    print("\n🔐 Logging in as Admin...")
    login("divyam@dynamiclabz.net", "12345")
    headers = set_headers()

    data = get_tickets_details(event_date_data=event_date_id,headers=headers)
    print(data)

    for ticket_data in data:
        get_ticket(ticket_id=ticket_data, headers=headers)

    
    print("\n🔓 Logging out...")
    logout(headers)

