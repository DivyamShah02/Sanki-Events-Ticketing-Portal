import requests

base_url = 'http://127.0.0.1:8000/'

def create_user():
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

def login_user():
    url = base_url + 'user/login-api/'

    data = {
        'email': 'admin@dynamiclabz.net',        
        'password':'Admin@123',
    }

    response = requests.post(url, data=data)

    return response


if __name__ == '__main__':
    print('Hello')

    create_user_respone = create_user()
    print(create_user_respone.text)

    # login_user_respone = login_user()
    # print(login_user_respone.text)
