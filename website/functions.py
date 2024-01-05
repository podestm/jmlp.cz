from werkzeug.utils import secure_filename
import os

def process_upload_file(upload_file, event_date, upload_folder):
    if upload_file:
        file_name = secure_filename(upload_file.filename)
        file_split = os.path.splitext(file_name)
        base_name, file_ext = file_split

        file_name_with_date = f"{base_name}_{event_date}{file_ext}"

        file_url = os.path.join(upload_folder, file_name_with_date)

        upload_file.save(file_url)

        return file_name_with_date, file_ext, file_url
    else:
        return None, None, None
