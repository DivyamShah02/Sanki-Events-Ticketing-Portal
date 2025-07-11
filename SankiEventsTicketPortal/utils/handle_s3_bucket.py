import os
import re
import boto3
import base64
import smtplib
import tempfile
from email.message import EmailMessage
from botocore.exceptions import ClientError


def base64_to_text(b64_text):
    # Decode the Base64 string back to bytes, then to text
    return base64.b64decode(b64_text.encode()).decode()

def create_event_folders_s3_old(event_name, event_dates):
    """
    Creates an event folder in S3 with subfolders for each event date.
    
    :param event_name: Name of the event.
    :param event_dates: List of event dates in YYYY-MM-DD format.
    :return: Path of the created event folder.
    """
    bucket_name = "sankievents"
    s3 = boto3.client(
            's3',
            aws_access_key_id=base64_to_text('QUtJQTVJSk9YQlFVVEVFNU9NSkI='),
            aws_secret_access_key=base64_to_text('TlIwblU5T0oyQ0lkQm1nRkFXMEk4RTRiT01na3NEVXVPQnJJTU5iNQ=='),
            region_name='eu-north-1'
        )

    # Check if event folder already exists, add a counter if needed
    counter = 1
    event_folder = f"Events/{event_name}/"
    
    # List existing objects in S3 to check for duplicate event names
    existing_folders = {obj['Key'].split('/')[0] for obj in s3.list_objects_v2(Bucket=bucket_name).get('Contents', [])}
    
    original_folder = event_folder
    while event_folder.rstrip('/') in existing_folders:
        event_folder = f"{original_folder.rstrip('/')}_{counter}/"
        counter += 1

    # Create empty object to represent folder in S3
    s3.put_object(Bucket=bucket_name, Key=event_folder)

    # Create subfolders for event dates
    for date in event_dates:
        date_folder = f"{event_folder}{date}/"
        s3.put_object(Bucket=bucket_name, Key=date_folder)

        s3.put_object(Bucket=bucket_name, Key=f"{date_folder}Available Tickets/")
        s3.put_object(Bucket=bucket_name, Key=f"{date_folder}Sent Tickets/")

    return f"s3://{bucket_name}/{event_folder}"  # Return full S3 path

def slugify(text):
    """Convert event name to a safe S3 folder name."""
    return re.sub(r'[^a-zA-Z0-9_-]', '_', text.strip())

def create_event_folders_s3(event_name, event_dates):
    """
    Creates an event folder in S3 with subfolders for each event date.
    
    :param event_name: Name of the event.
    :param event_dates: List of event dates in YYYY-MM-DD format.
    :return: Path of the created event folder.
    """
    bucket_name = "sankievents"  # Set your bucket name
    aws_access_key_id = base64_to_text('QUtJQTVJSk9YQlFVVEVFNU9NSkI=')  # Set your credentials
    aws_secret_access_key = base64_to_text('TlIwblU5T0oyQ0lkQm1nRkFXMEk4RTRiT01na3NEVXVPQnJJTU5iNQ==')
    region_name = "eu-north-1"

    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )

    # Slugify the event name to make it S3-safe
    safe_event_name = slugify(event_name)
    counter = 1
    event_folder = f"Events/{safe_event_name}/"

    # List existing folder keys
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix="Events/")
    existing_folders = {
        obj['Key'].rstrip('/')
        for obj in response.get('Contents', [])
        if obj['Key'].endswith('/')
    }

    original_folder = event_folder.rstrip('/')
    while event_folder.rstrip('/') in existing_folders:
        event_folder = f"{original_folder}_{counter}/"
        counter += 1

    # Create the base event folder
    s3.put_object(Bucket=bucket_name, Key=event_folder)

    # Create date-wise subfolders
    for date in event_dates:
        date_str = str(date)  # Make sure it's a string like '2025-06-13'
        date_folder = f"{event_folder}{date_str}/"
        s3.put_object(Bucket=bucket_name, Key=date_folder)
        s3.put_object(Bucket=bucket_name, Key=f"{date_folder}Available Tickets/")
        s3.put_object(Bucket=bucket_name, Key=f"{date_folder}Sent Tickets/")

    # return f"s3://{bucket_name}/{event_folder}"
    return f"{event_folder}"

def upload_ticket_to_s3_event_folder(uploaded_files, event_folder):
    print(event_folder)
    """Uploads a file to AWS S3, renaming it if a file with the same name exists."""
    bucket_name = "sankievents"
    region_name = 'eu-north-1'
    s3 = boto3.client(
            's3',
            aws_access_key_id=base64_to_text('QUtJQTVJSk9YQlFVVEVFNU9NSkI='),
            aws_secret_access_key=base64_to_text('TlIwblU5T0oyQ0lkQm1nRkFXMEk4RTRiT01na3NEVXVPQnJJTU5iNQ=='),
            region_name=region_name
        )
    error_files = []
    total_files_uploaded = 0
    for uploaded_file in uploaded_files:
        try:
            base_name, extension = os.path.splitext(uploaded_file.name)
            file_name = uploaded_file.name
            s3_key = f"{event_folder}/{file_name}"
            counter = 1

            # Check if file exists and rename if necessary
            # while True:
            #     try:
            #         s3.head_object(Bucket=bucket_name, Key=s3_key)
            #         # If file exists, update the filename
            #         file_name = f"{base_name}({counter}){extension}"
            #         s3_key = f"{event_folder}/{file_name}"
            #         counter += 1
            #     except s3.exceptions.ClientError as ee:
            #         print('hrtrt')
            #         print(ee)
            #         break  # File does not exist, proceed with upload

            # Upload file
            s3.upload_fileobj(uploaded_file, bucket_name, s3_key)

            # Generate file URL
            file_url = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{s3_key}"

            total_files_uploaded+=1
        
        except Exception as ex:
            print(ex)
            error_files.append(uploaded_file)

    return total_files_uploaded, error_files

def get_number_of_tickets_in_event_folder(folder_name):
    bucket_name = "sankievents"
    s3 = boto3.client(
            's3',
            aws_access_key_id=base64_to_text('QUtJQTVJSk9YQlFVVEVFNU9NSkI='),
            aws_secret_access_key=base64_to_text('TlIwblU5T0oyQ0lkQm1nRkFXMEk4RTRiT01na3NEVXVPQnJJTU5iNQ=='),
            region_name='eu-north-1'
        )

    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)

    if "Contents" in response:
        return len(response["Contents"]) - 1
    else:
        return 0  # No files found

def send_ticket_and_move_single_ticket(event_name, date, recipient_email):
    """
    Sends one ticket from 'Available Tickets' in S3 via Gmail, moves it to 'Sent Tickets' if successful.

    :param event_name: Name of the event.
    :param date: Date string in YYYY-MM-DD.
    :param recipient_email: Email to send to.
    :param gmail_user: Gmail address to send from.
    :param gmail_app_password: App password (not your Gmail login).
    :return: (filename, True) if success, else (None, False, error_message)
    """

    bucket_name = "sankievents"
    s3 = boto3.client(
            's3',
            aws_access_key_id=base64_to_text('QUtJQTVJSk9YQlFVVEVFNU9NSkI='),
            aws_secret_access_key=base64_to_text('TlIwblU5T0oyQ0lkQm1nRkFXMEk4RTRiT01na3NEVXVPQnJJTU5iNQ=='),
            region_name='eu-north-1'
        )

    gmail_user = 'support@sankievents.in'
    gmail_app_password = 'jxkf hdmb hjwf yrgv'

    base_path = f"Events/{event_name}/{date}/Available Tickets/"
    try:
        # List files in 'Available Tickets'
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=base_path)
        contents = response.get("Contents", [])
        available_files = [obj['Key'] for obj in contents if not obj['Key'].endswith('/')]

        if not available_files:
            return None, False, "No files in Available Tickets"

        file_key = available_files[0]
        filename = file_key.split('/')[-1]

        # Download the file temporarily
        with tempfile.TemporaryDirectory() as tmpdirname:
            local_path = os.path.join(tmpdirname, filename)
            s3.download_file(bucket_name, file_key, local_path)

            # Send email with attachment
            msg = EmailMessage()
            msg['Subject'] = f"Your Ticket for {event_name} on {date}"
            msg['From'] = gmail_user
            msg['To'] = recipient_email
            msg.set_content(f"Please find attached your ticket for {event_name} on {date}.")

            with open(local_path, 'rb') as f:
                file_data = f.read()
                msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=filename)

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(gmail_user, gmail_app_password)
                smtp.send_message(msg)

        # Move file to 'Sent Tickets'
        sent_key = file_key.replace("Available Tickets", "Sent Tickets")
        s3.copy_object(Bucket=bucket_name, CopySource={'Bucket': bucket_name, 'Key': file_key}, Key=sent_key)
        s3.delete_object(Bucket=bucket_name, Key=file_key)

        return filename, True

    except ClientError as e:
        return None, False, str(e)
    except Exception as e:
        return None, False, str(e)

def send_ticket_and_move(event_name, date, recipient_email, qty):
    """
    Sends `qty` tickets from 'Available Tickets' in S3 via Gmail, moves them to 'Sent Tickets' if successful.

    :param event_name: Name of the event.
    :param date: Date string in YYYY-MM-DD.
    :param recipient_email: Email to send to.
    :param gmail_user: Gmail address to send from.
    :param gmail_app_password: Gmail App Password.
    :param qty: Number of tickets/files to send.
    :return: ([filenames], True) on success, or ([], False, error_message)
    """
    bucket_name = "sankievents"
    s3 = boto3.client(
            's3',
            aws_access_key_id=base64_to_text('QUtJQTVJSk9YQlFVVEVFNU9NSkI='),
            aws_secret_access_key=base64_to_text('TlIwblU5T0oyQ0lkQm1nRkFXMEk4RTRiT01na3NEVXVPQnJJTU5iNQ=='),
            region_name='eu-north-1'
        )

    gmail_user = 'support@sankievents.in'
    gmail_app_password = 'jxkf hdmb hjwf yrgv'

    base_path = f"{event_name}{date}/Available Tickets/"

    try:
        # List files in 'Available Tickets'
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=base_path)
        contents = response.get("Contents", [])
        available_files = [obj['Key'] for obj in contents if not obj['Key'].endswith('/')]

        # import pdb; pdb.set_trace()
        if not available_files:
            return [], False, "No files in Available Tickets."

        if len(available_files) < qty:
            return [], False, f"Not enough tickets. Requested {qty}, but only {len(available_files)} available."

        selected_files = available_files[:qty]
        filenames = []

        # Prepare email
        msg = EmailMessage()
        msg['Subject'] = f"Your {qty} Ticket(s) for {event_name} on {str(date).replace(' 00:00:00', '')}"
        msg['From'] = gmail_user
        msg['To'] = recipient_email
        msg.set_content(f"Attached are your {qty} ticket(s) for {event_name} on {str(date).replace(' 00:00:00', '')}.")

        with tempfile.TemporaryDirectory() as tmpdirname:
            for file_key in selected_files:
                filename = file_key.split('/')[-1]
                local_path = os.path.join(tmpdirname, filename)

                # Download the file
                s3.download_file(bucket_name, file_key, local_path)

                # Attach to email
                with open(local_path, 'rb') as f:
                    file_data = f.read()
                    msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=filename)

                filenames.append(filename)

        # Send email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(gmail_user, gmail_app_password)
            smtp.send_message(msg)

        # import pdb; pdb.set_trace()
        # Move files to 'Sent Tickets'
        for file_key in selected_files:
            sent_key = file_key.replace("Available Tickets", "Sent Tickets")
            s3.copy_object(Bucket=bucket_name, CopySource={'Bucket': bucket_name, 'Key': file_key}, Key=sent_key)
            s3.delete_object(Bucket=bucket_name, Key=file_key)

        return filenames, True

    except ClientError as e:
        return [], False, str(e)
    except Exception as e:
        return [], False, str(e)

def send_approve_mail(event_name, date, recipient_email, qty):
    """
    Sends `qty` tickets from 'Available Tickets' in S3 via Gmail, moves them to 'Sent Tickets' if successful.

    :param event_name: Name of the event.
    :param date: Date string in YYYY-MM-DD.
    :param recipient_email: Email to send to.
    :param gmail_user: Gmail address to send from.
    :param gmail_app_password: Gmail App Password.
    :param qty: Number of tickets/files to send.
    :return: ([filenames], True) on success, or ([], False, error_message)
    """
    
    gmail_user = 'support@sankievents.in'
    gmail_app_password = 'jxkf hdmb hjwf yrgv'

    try:

        # Prepare email
        msg = EmailMessage()
        msg['Subject'] = f"Your {qty} Ticket(s) for {event_name} on {str(date).replace(' 00:00:00', '')}"
        msg['From'] = gmail_user
        msg['To'] = recipient_email
        msg.set_content(f'''
Hi,

Your booking for {event_name} on {str(date).replace(' 00:00:00', '')} has been successfully confirmed!

We’ll be sending your {qty} ticket(s) shortly in a separate email.

Thank you for booking with us. Stay tuned!

Best regards,
Team, Sanki Events''')

        # Send email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(gmail_user, gmail_app_password)
            smtp.send_message(msg)

        return True

    except ClientError as e:
        print(e)
        return False
    except Exception as e:
        print(e)
        return False

def resend_ticket(event_name, date, recipient_email, qty, sent_files):
    """
    Sends `qty` tickets from 'Available Tickets' in S3 via Gmail, moves them to 'Sent Tickets' if successful.

    :param event_name: Name of the event.
    :param date: Date string in YYYY-MM-DD.
    :param recipient_email: Email to send to.
    :param gmail_user: Gmail address to send from.
    :param gmail_app_password: Gmail App Password.
    :param qty: Number of tickets/files to send.
    :return: ([filenames], True) on success, or ([], False, error_message)
    """
    bucket_name = "sankievents"
    s3 = boto3.client(
            's3',
            aws_access_key_id=base64_to_text('QUtJQTVJSk9YQlFVVEVFNU9NSkI='),
            aws_secret_access_key=base64_to_text('TlIwblU5T0oyQ0lkQm1nRkFXMEk4RTRiT01na3NEVXVPQnJJTU5iNQ=='),
            region_name='eu-north-1'
        )

    gmail_user = 'support@sankievents.in'
    gmail_app_password = 'jxkf hdmb hjwf yrgv'

    base_path = f"Events/{event_name}/{date}/Sent Tickets/"

    try:
        # List files in 'Available Tickets'
        # response = s3.list_objects_v2(Bucket=bucket_name, Prefix=base_path)
        # contents = response.get("Contents", [])
        available_files = [f"{base_path}{sent_file}" for sent_file in sent_files]

        selected_files = available_files[:qty]
        filenames = []

        # Prepare email
        msg = EmailMessage()
        msg['Subject'] = f"Your {qty} Ticket(s) for {event_name} on {date}"
        msg['From'] = gmail_user
        msg['To'] = recipient_email
        msg.set_content(f"Attached are your {qty} ticket(s) for {event_name} on {date}.")

        with tempfile.TemporaryDirectory() as tmpdirname:
            for file_key in selected_files:
                filename = file_key.split('/')[-1]
                local_path = os.path.join(tmpdirname, filename)

                # Download the file
                s3.download_file(bucket_name, file_key, local_path)

                # Attach to email
                with open(local_path, 'rb') as f:
                    file_data = f.read()
                    msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=filename)

                filenames.append(filename)

        # Send email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(gmail_user, gmail_app_password)
            smtp.send_message(msg)

        # Move files to 'Sent Tickets'
        # for file_key in selected_files:
        #     sent_key = file_key.replace("Available Tickets", "Sent Tickets")
        #     s3.copy_object(Bucket=bucket_name, CopySource={'Bucket': bucket_name, 'Key': file_key}, Key=sent_key)
        #     s3.delete_object(Bucket=bucket_name, Key=file_key)

        return filenames, True

    except ClientError as e:
        return [], False, str(e)
    except Exception as e:
        return [], False, str(e)


import boto3

def count_files_in_s3_folder(folder_path):
    """
    Counts the number of files in the given S3 folder (prefix).
    
    :param bucket_name: S3 bucket name.
    :param folder_path: Folder path (prefix), e.g., 'Events/Test_Event/2025-06-14/Available_Tickets/'.
    :return: Number of files in the folder.
    """
    # Ensure folder_path ends with '/'
    bucket_name = "sankievents"

    if not folder_path.endswith('/'):
        folder_path += '/'

    s3 = boto3.client(
            's3',
            aws_access_key_id=base64_to_text('QUtJQTVJSk9YQlFVVEVFNU9NSkI='),
            aws_secret_access_key=base64_to_text('TlIwblU5T0oyQ0lkQm1nRkFXMEk4RTRiT01na3NEVXVPQnJJTU5iNQ=='),
            region_name='eu-north-1'
        )

    paginator = s3.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=folder_path)

    file_count = 0
    for page in page_iterator:
        for obj in page.get('Contents', []):
            key = obj['Key']
            if not key.endswith('/'):  # Skip folder markers
                file_count += 1

    return file_count


if __name__ == '__main__':
    # Example usage:
    # bucket_name = "sankievents"
    # event_name = "Nesco"
    # event_dates = ["2025-12-12", "2025-12-13"]

    # event_folder_path = create_event_folders_s3(event_name, event_dates)
    # print(f"Event folder created at: {event_folder_path}")


    # filename, success, *error = send_ticket_and_move(
    #     event_name="Aditya ghadvi",
    #     date="2025-05-20 00:00:00",
    #     recipient_email="divyamshah1234@gmail.com"
    # )

    # if success:
    #     print(f"Sent and moved file: {filename}")
    # else:
    #     print("Failed:", error[0])

    files, success, *error = send_ticket_and_move(
        event_name="Aditya ghadvi",
        date="2025-05-20 00:00:00",
        recipient_email="divyamshah1234@gmail.com",
        qty=3
    )

    if success:
        print("Sent files:", files)
    else:
        print("Failed:", error[0])
