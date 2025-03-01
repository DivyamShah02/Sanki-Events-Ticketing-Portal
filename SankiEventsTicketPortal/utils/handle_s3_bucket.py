import boto3
import base64

def base64_to_text(b64_text):
    # Decode the Base64 string back to bytes, then to text
    return base64.b64decode(b64_text.encode()).decode()

def create_event_folders_s3(event_name, event_dates):
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
    event_folder = f"{event_name}/"
    
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

    return f"s3://{bucket_name}/{event_folder}"  # Return full S3 path


if __name__ == '__main__':
    # Example usage:
    bucket_name = "sankievents"
    event_name = "Nesco"
    event_dates = ["2025-12-12", "2025-12-13"]

    event_folder_path = create_event_folders_s3(event_name, event_dates)
    print(f"Event folder created at: {event_folder_path}")

