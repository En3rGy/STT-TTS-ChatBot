import requests
import xml.etree.ElementTree as ET


class DlnaHelper:

    def __init__(self, ip: str, vol=25):
        self.sonos_ip = ip

        # Desired volume level (0 to 100)
        self.volume_level = vol

    def play_uri(self, url: str):
        # SOAP request to set the volume
        set_volume_soap_request = f"""<?xml version="1.0" encoding="utf-8"?>
        <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
            <s:Body>
                <u:SetVolume xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1">
                    <InstanceID>0</InstanceID>
                    <Channel>Master</Channel>
                    <DesiredVolume>{self.volume_level}</DesiredVolume>
                </u:SetVolume>
            </s:Body>
        </s:Envelope>"""

        # SOAP request to tell the Sonos to play the audio file
        set_uri_soap_request = f"""<?xml version="1.0" encoding="utf-8"?>
        <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
            <s:Body>
                <u:SetAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">
                    <InstanceID>0</InstanceID>
                    <CurrentURI>{url}</CurrentURI>
                    <CurrentURIMetaData></CurrentURIMetaData>
                </u:SetAVTransportURI>
            </s:Body>
        </s:Envelope>"""

        # SOAP request to tell the Sonos to start playing
        play_soap_request = """<?xml version="1.0" encoding="utf-8"?>
        <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
            <s:Body>
                <u:Play xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">
                    <InstanceID>0</InstanceID>
                    <Speed>1</Speed>
                </u:Play>
            </s:Body>
        </s:Envelope>"""

        # Send the SOAP request to the Sonos speaker
        # Headers for sending the SOAP requests
        headers = {
            'Content-Type': 'text/xml',
        }

        # Send the SOAP request to set the AVTransportURI
        set_uri_response = requests.post(
            f'http://{self.sonos_ip}:1400/MediaRenderer/AVTransport/Control',
            headers={**headers, 'SOAPACTION': '"urn:schemas-upnp-org:service:AVTransport:1#SetAVTransportURI"'},
            data=set_uri_soap_request
        )

        # Send the SOAP request to set the volume
        set_volume_response = requests.post(
            f'http://{self.sonos_ip}:1400/MediaRenderer/RenderingControl/Control',
            headers={**headers, 'SOAPACTION': '"urn:schemas-upnp-org:service:RenderingControl:1#SetVolume"'},
            data=set_volume_soap_request
        )

        # Send the SOAP request to start the playback
        play_response = requests.post(
            f'http://{self.sonos_ip}:1400/MediaRenderer/AVTransport/Control',
            headers={**headers, 'SOAPACTION': '"urn:schemas-upnp-org:service:AVTransport:1#Play"'},
            data=play_soap_request
        )

        # Check if the request was successful
        if play_response.status_code == 200:
            print('Audio is playing on the Sonos speaker')
        else:
            print('Failed to play audio on the Sonos speaker')
