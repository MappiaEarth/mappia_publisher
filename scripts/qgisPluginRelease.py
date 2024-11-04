import requests
import re
import os

# Credentials and paths
username = os.getenv("OSGEO_USERNAME")
password = os.getenv("OSGEO_PASSWORD")
project_name = "mappia_publisher"
pluginFilePath = os.getenv("PLUGIN_FILEPATH")

session = requests.Session()

tokenName = "csrfmiddlewaretoken"

login_url = "https://plugins.qgis.org/accounts/login/"
tokenResponse = session.get(login_url)
login_payload = {}
login_payload[tokenName] = re.search(r"value=\"([^\"]+)\".*", tokenResponse.text[tokenResponse.text.index(tokenName):]).group(1)
login_payload["username"] = username
login_payload["password"] = password

loginResponse = session.post(login_url, data=login_payload, headers={"Referer": login_url})

if "logout" not in loginResponse:
    print("Failed to login on OSGEO for uploading QGIS plugins")
    exit(1)

upload_url = f"https://plugins.qgis.org/plugins/{project_name}/version/add/"
files = {
    "package": open(pluginFilePath, "rb")
}
tokenResponse = session.get(upload_url)
upload_payload = {}
upload_payload[tokenName] = re.search(r"value=\"([^\"]+)\".*", tokenResponse.text[tokenResponse.text.index(tokenName):]).group(1)
upload_payload["changelog"] = ""

uploadResponse = session.post(upload_url, data=upload_payload, files=files, headers={"Referer": upload_url})

try:
    msg = uploadResponse.text[uploadResponse.text.index('alert-error'):]
    msg = msg[:msg.find('</div>')]
    print("Error message: " + msg)
    exit(1)
except:
    print(f"Success, please confirm checking on site: https://plugins.qgis.org/plugins/{project_name}/")
print("Finished")
