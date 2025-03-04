import requests

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

def create_user():
    url = base_url + 'user/user-api/'

    data = {
        'name': 'Divyam Shah',
        'password':'12345',
        'contact_number': '9054413199',
        'email': 'divyam@dynamiclabz.net',
        'role': 'hod',  
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

    # create_admin_user_respone = create_admin_user()
    # print(create_admin_user_respone.text)

    # create_user_respone = create_user()
    # print(create_user_respone.text)


    login_user_respone = login_user()
    print(login_user_respone.text)
