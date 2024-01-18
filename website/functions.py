from werkzeug.utils import secure_filename
from datetime import datetime
import os

def process_upload_file(upload_file, event_date, upload_folder):
    if upload_file:
        file_name = secure_filename(upload_file.filename)
        file_split = os.path.splitext(file_name)
        base_name, file_ext = file_split

        file_name_with_date = f"{event_date}_{base_name}_{file_ext}"

        file_url = os.path.join(upload_folder, file_name_with_date)

        upload_file.save(file_url)

        return file_name_with_date, file_url
    else:
        return None, None


def set_season(date_string):
    date_object = datetime.strptime(date_string, "%Y-%m-%d")

    # Extract the month from the datetime object
    year = date_object.year %100
    month = date_object.month

    # Define a reference month for comparison
    reference_month = 5

    # Compare the months and print the result
    if month < reference_month:
        event_season = f"{year-1}{year}"
    elif month >= reference_month:
        event_season = f"{year}{year+1}"
    return event_season