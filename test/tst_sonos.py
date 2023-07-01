import requests
import xml.etree.ElementTree as ET

# Step 4: Discover Sonos speaker (alternatively, you can manually enter the IP address)
# This example assumes you already know the IP address of your Sonos speaker
# If not, you can use a UPnP discovery script to find it on your local network
sonos_ip_address = '192.168.143.105'  # Replace with the IP address of your Sonos speaker

# Step 5: Send a DLNA command to play an audio file

# The URL of the audio file you want to play
audio_url = 'https://freetestdata.com/wp-content/uploads/2021/09/Free_Test_Data_5MB_MP3.mp3'  # Replace with your audio file URL

# SOAP request to tell the Sonos to play the audio file
soap_request = f"""<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
    <s:Body>
        <u:SetAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">
            <InstanceID>0</InstanceID>
            <CurrentURI>{audio_url}</CurrentURI>
            <CurrentURIMetaData></CurrentURIMetaData>
        </u:SetAVTransportURI>
    </s:Body>
</s:Envelope>"""

# Send the SOAP request to the Sonos speaker
headers = {
    'SOAPACTION': '"urn:schemas-upnp-org:service:AVTransport:1#SetAVTransportURI"',
    'Content-Type': 'text/xml',
}
response = requests.post(f'http://{sonos_ip_address}:1400/MediaRenderer/AVTransport/Control',
                         headers=headers, data=soap_request)

# Check if the request was successful
if response.status_code == 200:
    print('Audio is playing on the Sonos speaker')
else:
    print('Failed to play audio on the Sonos speaker')
