#from onvif import ONVIFCamera
#mycam = ONVIFCamera('192.168.1.250', 80, 'admin', 'admin123', '/usr/local/lib/python3.7/site-packages/wsdl/')
#resp = mycam.devicemgmt.GetHostname()
#print( 'My camera`s hostname: ' + str(resp))
#import cv2
#
#capture = cv2.VideoCapture('rtsp://admin:admin123@192.168.1.250')
#print(capture)

from wsdiscovery.discovery import ThreadedWSDiscovery as WSDiscovery
from wsdiscovery.publishing import ThreadedWSPublishing as WSPublishing
from wsdiscovery import QName, Scope


# Discover it (along with any other service out there)
# wsd = WSDiscovery()
# wsd.start()
# services = wsd.searchServices()
# for service in services:
#    print(service.getEPR() + ":" + service.getXAddrs()[0])
# wsd.stop()

# -----------------------------------------------------------------------------
from onvif import ONVIFCamera
from onvif import ONVIFService

def media_profile_configuration():
    '''
    A media profile consists of configuration entities such as video/audio
    source configuration, video/audio encoder configuration,
    or PTZ configuration. This use case describes how to change one
    configuration entity which has been already added to the media profile.
    '''

    # Create the media service
    mycam = ONVIFCamera('192.168.1.250', 80, 'admin', 'admin123')
    media_service = mycam.create_media_service()
    image_service = mycam.create_devicemgmt_service()
    print(image_service.GetHostname())
   #  device_service = ONVIFService('http://192.168.1.1/onvif/device_service','admin', 'admin','/usr/local/lib/python3.7/site-packages/wsdl/devicemgmt.wsdl')
#    image_service = mycam.create_pullpoint_service()
#    print(image_service.PullMessages({"Timeout":1222,"MessageLimit":20}))
    

    profiles = media_service.GetProfiles()

    # Use the first profile and Profiles have at least one
    token = profiles[0].token
    
    # create stream uri
    stream_setup = media_service.create_type('GetStreamUri')
    stream_setup.StreamSetup = {'Stream': 'RTP_unicast', 'Transport' : {'Protocol': 'RTSP'}}
    stream_setup.ProfileToken = token
    stream_uri = media_service.GetStreamUri(stream_setup)
    print(stream_uri)
#    import cv2
#    cap = cv2.VideoCapture('rtsp://admin:admin123@192.168.1.250:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')
#    print(cap)


    # Get all video encoder configurations
    configurations_list = media_service.GetVideoEncoderConfigurations()

    # Use the first profile and Profiles have at least one
    video_encoder_configuration = configurations_list[0]

    # Get video encoder configuration options
    options = media_service.GetVideoEncoderConfigurationOptions({'ProfileToken':token})

    # Setup stream configuration
    video_encoder_configuration.Encoding = 'H264'
    # Setup Resolution
    video_encoder_configuration.Resolution.Width = \
                    options.H264.ResolutionsAvailable[0].Width
    video_encoder_configuration.Resolution.Height = \
                    options.H264.ResolutionsAvailable[0].Height
    # Setup Quality
    video_encoder_configuration.Quality = options.QualityRange.Min
    # Setup FramRate
    video_encoder_configuration.RateControl.FrameRateLimit = \
                                    options.H264.FrameRateRange.Min
    # Setup EncodingInterval
    video_encoder_configuration.RateControl.EncodingInterval = \
                                    options.H264.EncodingIntervalRange.Min
    # Setup Bitrate
#    video_encoder_configuration.RateControl.BitrateLimit = \
#                            options.Extension.H264.BitrateRange[0].Min[0]

    # Create request type instance
    request = media_service.create_type('SetVideoEncoderConfiguration')
    request.Configuration = video_encoder_configuration
    # ForcePersistence is obsolete and should always be assumed to be True
    request.ForcePersistence = True

    # Set the video encoder configuration
    media_service.SetVideoEncoderConfiguration(request)
#    print(media_service)
    return token, media_service

if __name__ == '__main__':
    token, media_service = media_profile_configuration()
    print(token)
    media_service.StartMulticastStreaming(token)
