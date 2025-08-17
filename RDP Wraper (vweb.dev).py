import os
import subprocess
import sys
import urllib.request
import zipfile
import time

def download_rdp_wrapper(url, destination_file):
    """Downloads RDP Wrapper to the specified destination file.

    Args:
        url (str): The URL of the RDP Wrapper download.
        destination_file (str): The destination file for the downloaded RDP Wrapper.
    """

    try:
        print("Downloading RDP Wrapper...")
        with urllib.request.urlopen(url) as response, open(destination_file, 'wb') as f:
            total_size = int(response.getheader('Content-Length'))
            downloaded_size = 0
            block_size = 1024

            while True:
                data = response.read(block_size)
                if not data:
                    break

                downloaded_size += len(data)
                f.write(data)

                progress = (downloaded_size / total_size) * 100
                print(f"Progress: {progress:.2f}%", end="\r")

        print("\nRDP Wrapper downloaded successfully")
    except Exception as e:
        print(f"Error downloading RDP Wrapper: {e}")

def extract_rdp_wrapper(zip_file, destination_dir):
    """Extracts RDP Wrapper from the specified ZIP file to the destination directory.

    Args:
        zip_file (str): The path to the ZIP file containing RDP Wrapper.
        destination_dir (str): The destination directory for extracted files.
    """

    try:
        print("Extracting RDP Wrapper...")
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(destination_dir)
        print("RDP Wrapper extracted successfully")
    except Exception as e:
        print(f"Error extracting RDP Wrapper: {e}")

def run_install_batch(install_bat_file):
    """Runs the install.bat file.

    Args:
        install_bat_file (str): The path to the install.bat file.
    """

    try:
        print("Running install.bat...")
        subprocess.run([install_bat_file], check=True)
        print("RDP Wrapper installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error running install.bat: {e}")

if __name__ == "__main__":
    # Specific version URL for RDP Wrapper v1.6.2
    rdp_wrapper_url = "https://github.com/vweb-dev/rdpwrap/releases/download/v1.6.2/rdp_wrapper.vweb.dev.zip"

    zip_file = "rdp_wrapper.zip"
    extract_dir = "rdp_wrapper (vweb.dev)"
    rdp_wrapper_file = os.path.join(extract_dir, "rdpwrap.msi")
    install_bat_file = os.path.join(extract_dir, "install.bat")

    download_rdp_wrapper(rdp_wrapper_url, zip_file)

    extract_rdp_wrapper(zip_file, extract_dir)

    # Wait for the install.bat file to be extracted
    while not os.path.exists(install_bat_file):
        time.sleep(5)

    run_install_batch(install_bat_file)

    