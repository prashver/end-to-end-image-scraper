import requests
import os
from bs4 import BeautifulSoup

import time
import zipfile
import streamlit as st
import base64


def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
        f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
        unsafe_allow_html=True
    )

add_bg_from_local('wallpaper.jpg')


def create_save_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def fetch_and_save_images(query, num_images_to_fetch, save_dir):
    create_save_directory(save_dir)

    # List to store downloaded image paths
    downloaded_image_paths = []

    total_images_fetched = 0

    # Loop to fetch multiple pages of images
    for start_index in range(0, num_images_to_fetch, 10):
        if start_index != 0:
            time.sleep(4)  # Add a longer delay between pages to avoid getting blocked

        if total_images_fetched >= num_images_to_fetch:
            break  # Break out of the loop if the desired count is reached

        # Constructing the Google Images search URL with the start index
        search_url = f"https://www.google.com/search?q={query}&tbm=isch&start={start_index}&tbs=iszw:1920,iszh:1080,islt:20mp"

        response = requests.get(search_url)
        soup = BeautifulSoup(response.content, "html.parser")
        all_images = soup.find_all("img")

        for i, img in enumerate(all_images):
            if total_images_fetched >= num_images_to_fetch:
                break

            if i == 0:
                continue  # Skipping the first image (Google logo)

            image_url = img['src']
            image_data = requests.get(image_url).content

            # Saving the image with a unique name based on its index
            image_path = os.path.join(save_dir, f"{query}_{start_index + i}.jpg")
            with open(image_path, "wb") as f:
                f.write(image_data)

            downloaded_image_paths.append(image_path)

            total_images_fetched += 1

            # Adding a delay to avoid overwhelming the server with requests
            time.sleep(1)

        # Adding a longer delay between pages to avoid getting blocked
        time.sleep(2)

    # Creating a zip file to store all downloaded images
    zip_file_path = os.path.join(save_dir, f"{query}_images.zip")
    with zipfile.ZipFile(zip_file_path, "w") as zipf:
        for image_path in downloaded_image_paths:
            zipf.write(image_path, os.path.basename(image_path))

    return zip_file_path



# Main function in case we are not using streamlit
# if __name__ == "__main__":
#     query = input("Enter the search query: ")
#     num_images_to_fetch = 500
#     save_dir = "scraped_images/"
#
#     zip_file_path = fetch_and_save_images(query, num_images_to_fetch, save_dir)
#     print(f"All images saved in '{zip_file_path}' as a zip folder.")


# Streamlit app
st.markdown("<h1 style='font-family: monospace, sans-serif; color: #007bff; text-align: center; font-size: 42px'>ImageHarvest Pro</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='font-family: Arial, sans-serif; color: #E2F1D1 ; text-align: center; font-size: 18px'>Effortless Image Scraping</h3>", unsafe_allow_html=True)

query = st.text_input("Enter the search query:", value="", max_chars=50)

# For now assigning only 20 as a value to this parameter because Google limits the results fetched count when lot of requests are made
num_images_to_fetch = 20

st.markdown("\n\n\n\n")

if st.button("Fetch and Download Images"):
    save_dir = "scraped_images/"        # Saving all query results in local folder
    zip_file_path = fetch_and_save_images(query, num_images_to_fetch, save_dir)
    st.success("All images saved in a zip file.")

    # Download button for the zip file
    with open(zip_file_path, "rb") as f:
        zip_file_bytes = f.read()
    st.download_button(label="Download Zip File", data=zip_file_bytes, file_name=zip_file_path)
