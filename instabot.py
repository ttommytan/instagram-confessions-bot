import os
from instagram_credentials import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, FILE_PATH
from instagrapi import Client

# Load Instagram account credentials from environment variables
username = INSTAGRAM_USERNAME
password = INSTAGRAM_PASSWORD

# Create an Instagrapi client
client = Client()
client.login(username, password)

# Define the caption for your post
hashtags = """
.
.
. 
.
.
.
.
.
.
.
.
.
.
.
.
"""
#collegegirls #confessions #freshman #sophomore #junior #senior 
#highschool #like4likes #instadaily #love #romance #college 
#repost #myucberkeley #ucla #ucdavis #ucsb #ucsf #uci #ucsd 
#collegelove #calstate #california #newyork 
#nevada #california


# Specify the path to the folder 'bruin_tea'
folder_path = FILE_PATH

# Get a list of all files in the folder

png_files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith('.png')],
                   key=lambda f: os.path.getmtime(os.path.join(folder_path, f)))



# Check if there are any files in the folder
if png_files:
    # Get the first file in the list
    first_file = os.path.join(folder_path, png_files[0])

    # Print the file path before uploading
    print(f"Uploading file: {first_file}")

    # Upload the image and post it with the given caption
    media = client.photo_upload(first_file, hashtags, usertags=[])

    print("Post successfully uploaded!")

    # Delete the file after posting
    os.remove(first_file)
else:
    print("No files found in the folder.")



# Logout after posting
client.logout()



