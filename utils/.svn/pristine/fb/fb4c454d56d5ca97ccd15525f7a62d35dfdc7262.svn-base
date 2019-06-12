"""
c2w Gstreamer Pipeline Module
==============================

This module contains the Gstreamer pipelines used in the server and in the
client to send and receive the video streams.
"""
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

import logging
import sys

sys.dont_write_bytecode = True
logging.basicConfig()
moduleLogger = logging.getLogger('c2w.main.gst_pipeline')


class c2wGstServerPipeline(object):

    def __init__(self, videoFilePath, dstIpAddress, basePort, noVideo=False):

        DEST_HOST = '127.0.0.1'

        moduleLogger.debug('Building pipeline for movie: %s, dstIpAddress %s',
                           videoFilePath, dstIpAddress)

        self.rtpVideoSendPort = int(basePort)
        self.rtcpVideoSendPort = int(basePort) + 1
        self.rtcpVideoRecvPort = int(basePort) + 5
        if int(dstIpAddress.split('.')[0]) == 224:
            self.multicast = True
        else:
            self.multicast = False
        self.multicastAddress = dstIpAddress
        self.noVideo = noVideo

        self.videoFileName = videoFilePath
        self.bitRate = 300
        # the pipeline to hold everything
        self.pipeline = Gst.Pipeline()
        self.streaming = False

        # create the elements before rtpbin and set the properties
        self.fileSrc = Gst.ElementFactory.make("filesrc", None)
        self.fileSrc.set_property('location', self.videoFileName)

        oggDemux = Gst.ElementFactory.make("oggdemux", None)
        q1 = Gst.ElementFactory.make("queue", None)
        theoraDec = Gst.ElementFactory.make("theoradec", None)
        q2 = Gst.ElementFactory.make("queue", None)
        videoRate = Gst.ElementFactory.make("videorate", None)
        videoConvert = Gst.ElementFactory.make("videoconvert", None)
        videoScale = Gst.ElementFactory.make("videoscale", None)

        caps = Gst.caps_from_string(
                "video/x-raw,width=854,height=480,framerate=15/1")
        capsFilter = Gst.ElementFactory.make("capsfilter", None)
        capsFilter.set_property("caps", caps)

        x264Enc = Gst.ElementFactory.make("x264enc", None)
        x264Enc.set_property("tune", 'zerolatency')
        x264Enc.set_property("byte-stream", True)
        x264Enc.set_property("byte-stream", self.bitRate)
        rtph264Pay = Gst.ElementFactory.make("rtph264pay", None)

        self.pipeline.add(self.fileSrc)
        self.pipeline.add(oggDemux)
        self.pipeline.add(q1)
        self.pipeline.add(theoraDec)
        self.pipeline.add(q2)
        self.pipeline.add(videoRate)
        self.pipeline.add(videoConvert)
        self.pipeline.add(videoScale)
        self.pipeline.add(capsFilter)
        self.pipeline.add(x264Enc)
        self.pipeline.add(rtph264Pay)

        self.fileSrc.link(oggDemux)
        oggDemux.connect("pad-added", self.onPadAdded, q1)
        q1.link(theoraDec)
        theoraDec.link(q2)
        q2.link(videoRate)
        videoRate.link(videoConvert)
        videoConvert.link(videoScale)
        videoScale.link(capsFilter)
        capsFilter.link(x264Enc)
        x264Enc.link(rtph264Pay)

        # the rtpbin element
        rtpBin = Gst.ElementFactory.make('rtpbin', None)

        self.pipeline.add(rtpBin)

        # the udp sinks and source we will use for RTP and RTCP
        udpRtpVideoSink = Gst.ElementFactory.make('udpsink', None)
        udpRtpVideoSink.set_property('port', self.rtpVideoSendPort)
        if self.multicast:
            moduleLogger.debug('Mulicast enabled, addr=%s',
                               self.multicastAddress)
            udpRtpVideoSink.set_property('host', self.multicastAddress)
            udpRtpVideoSink.set_property('auto-multicast', True)
        else:
            udpRtpVideoSink.set_property('host', DEST_HOST)
        udpRtpVideoSink.set_property('ts-offset', 0)

        udpRtcpVideoSink = Gst.ElementFactory.make('udpsink', None)
        udpRtcpVideoSink.set_property('port', self.rtcpVideoSendPort)
        if self.multicast:
            udpRtcpVideoSink.set_property('host', self.multicastAddress)
            udpRtcpVideoSink.set_property('auto-multicast', True)
        else:
            udpRtcpVideoSink.set_property('host', DEST_HOST)
        # no need for synchronisation or preroll on the RTCP sink
        udpRtcpVideoSink.set_property('async', False)
        udpRtcpVideoSink.set_property('sync', False)

        udpRtcpSrc = Gst.ElementFactory.make('udpsrc', None)
        udpRtcpSrc.set_property('port', self.rtcpVideoRecvPort)

        self.pipeline.add(udpRtpVideoSink)
        self.pipeline.add(udpRtcpVideoSink)
        self.pipeline.add(udpRtcpSrc)

        # now link all to the rtpbin, start by getting an RTP sinkpad
        # for session 0
        sinkpad = Gst.Element.get_request_pad(rtpBin, 'send_rtp_sink_0')
        srcpad = Gst.Element.get_static_pad(rtph264Pay, 'src')
        Gst.Pad.link(srcpad, sinkpad)

        # get the RTP srcpad that was created when we requested the
        # sinkpad above and link it to the rtpsink sinkpad
        srcpad = Gst.Element.get_static_pad(rtpBin, 'send_rtp_src_0')
        sinkpad = Gst.Element.get_static_pad(udpRtpVideoSink, 'sink')
        Gst.Pad.link(srcpad, sinkpad)

        # get an RTCP srcpad for sending RTCP to the receiver
        srcpad = Gst.Element.get_request_pad(rtpBin, 'send_rtcp_src_0')
        sinkpad = Gst.Element.get_static_pad(udpRtcpVideoSink, 'sink')
        Gst.Pad.link(srcpad, sinkpad)

        # we also want to receive RTCP, request an RTCP sinkpad for session 0
        # and link it to the srcpad of the udpsrc for RTCP
        srcpad = Gst.Element.get_static_pad(udpRtcpSrc, 'src')
        sinkpad = Gst.Element.get_request_pad(rtpBin, 'recv_rtcp_sink_0')
        Gst.Pad.link(srcpad, sinkpad)

        # Create bus to get events from GStreamer pipeline
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::eos', self.on_eos)
        self.bus.connect('message::error', self.on_error)

    def onPadAdded(self, src, pad, target):
        string = pad.query_caps(None).to_string()
        Gst.caps_from_string(string)
        if string.startswith('video/'):
            # we should be OK
            sinkpad = Gst.Element.get_static_pad(target, 'sink')
            Gst.Pad.link(pad, sinkpad)

    def on_error(self, bus, msg):
        moduleLogger.error('on_error(): %s', msg.parse_error())

    def on_eos(self, bus, msg):
        moduleLogger.info('Restarting video: %s (on_eos() called)',
                          self.videoFileName)
        Gst.Element.set_state(self.pipeline, Gst.State.PAUSED)
        self.pipeline.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH, 0)
        self.fileSrc.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH, 0)
        Gst.Element.set_state(self.pipeline, Gst.State.PLAYING)

    def startStreaming(self):
        if self.noVideo:
            return
        if not self.streaming:
            moduleLogger.debug('started streaming video=%s',
                               self.videoFileName)
            Gst.Element.set_state(self.pipeline, Gst.State.PLAYING)
            self.streaming = True

    def stopStreaming(self):
        pass
#         if self.noVideo:
#             return
#         if self.streaming:
#             Gst.Element.set_state(self.pipeline, Gst.State.READY)
#             self.streaming = False


class c2wGstClientPipeline(object):
    """
    The Gstreamer pipeline used in the client.
    """
    def __init__(self, dstIpAddress, rtpVideoRecvPort):

        self.rtpVideoRecvPort = rtpVideoRecvPort
        self.rtcpVideoRecvPort = self.rtpVideoRecvPort + 1
        self.rtcpSendPort = self.rtpVideoRecvPort + 5
        self.multicastAddress = dstIpAddress

        # Video related stuff
        # Create GStreamer pipeline
        self.pipeline = Gst.Pipeline()

        # Create bus to get events from GStreamer pipeline
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::error', self.on_error)

        # This is needed to make the video output in our DrawingArea:
        self.bus.enable_sync_message_emission()
        self.bus.connect('sync-message::element', self.on_sync_message)

        #Create GStreamer elements
        udpRtpSrc = Gst.ElementFactory.make('udpsrc', None)
        udpRtpSrc.set_property('port', self.rtpVideoRecvPort)
        caps = Gst.caps_from_string(
                "application/x-rtp,media=(string)video," +
                "clock-rate=(int)90000,encoding-name=(string)H264")
        udpRtpSrc.set_property('caps', caps)
        udpRtpSrc.set_property('name', "udpRtpSrc")
        udpRtcpSrc = Gst.ElementFactory.make('udpsrc', None)
        udpRtcpSrc.set_property('port', self.rtcpVideoRecvPort)
        udpRtcpSrc.set_property('name', "udpRtcpSrc")
        udpRtcpSink = Gst.ElementFactory.make('udpsink', None)
        udpRtcpSink.set_property('port', self.rtcpSendPort)
        udpRtcpSink.set_property('async', False)
        udpRtcpSink.set_property('sync', False)
        udpRtcpSink.set_property('name', "udpRtcpSink")

        self.rtph264Depay = Gst.ElementFactory.make('rtph264depay', None)
        avdecH264 = Gst.ElementFactory.make('avdec_h264', None)
        videoConvert = Gst.ElementFactory.make('videoconvert', None)
        videoScale = Gst.ElementFactory.make("videoscale", None)
        videoSink = Gst.ElementFactory.make('autovideosink', None)

        # Add elements to the pipeline
        self.pipeline.add(udpRtpSrc)
        self.pipeline.add(udpRtcpSrc)
        self.pipeline.add(udpRtcpSink)
        self.pipeline.add(self.rtph264Depay)
        self.pipeline.add(avdecH264)
        self.pipeline.add(videoConvert)
        self.pipeline.add(videoScale)
        self.pipeline.add(videoSink)

        self.rtph264Depay.link(avdecH264)
        avdecH264.link(videoConvert)
        videoConvert.link(videoScale)
        videoScale.link(videoSink)

        rtpBin = Gst.ElementFactory.make('rtpbin', None)
        rtpBin.set_property('name', 'rtpBin')
        rtpBin.set_property('latency', 100)
        self.pipeline.add(rtpBin)

        srcpad = Gst.Element.get_static_pad(udpRtpSrc, 'src')
        sinkpad = Gst.Element.get_request_pad(rtpBin, 'recv_rtp_sink_0')
        res = Gst.Pad.link(srcpad, sinkpad)

        srcpad = Gst.Element.get_static_pad(udpRtcpSrc, 'src')
        sinkpad = Gst.Element.get_request_pad(rtpBin, 'recv_rtcp_sink_0')
        Gst.Pad.link(srcpad, sinkpad)

        srcpad = Gst.Element.get_request_pad(rtpBin, 'send_rtcp_src_0')
        sinkpad = Gst.Element.get_static_pad(udpRtcpSink, 'sink')
        Gst.Pad.link(srcpad, sinkpad)
        rtpBin.connect("pad-added", self.onPadAdded)

        Gst.debug_bin_to_dot_file(self.pipeline, Gst.DebugGraphDetails.ALL,
                                  './pipeline0.dot')

    def onPadAdded(self, src, pad):
        string = pad.query_caps(None).to_string()
        Gst.caps_from_string(string)
        if string.startswith('application/x-rtp'):
            # we should be OK
            sinkpad = Gst.Element.get_static_pad(self.rtph264Depay, 'sink')
            Gst.Pad.link(pad, sinkpad)

    def on_error(self, bus, msg):
        """
        Method needed by Gst bus
        """
        moduleLogger.error('on_error():', msg.parse_error())

    def on_sync_message(self, bus, msg):
        """
        Method needed by Gst bus
        """
        if msg.get_structure().get_name() == 'prepare-window-handle':
            msg.src.set_property('force-aspect-ratio', True)
            msg.src.set_window_handle(self.xid)

    def start_video(self, videoArea):
        """
        This method MUST BE CALLED AFTER show_all() HAS BEEN CALLED
        """
        self.xid = videoArea.get_property('window').get_xid()
        self.pipeline.set_state(Gst.State.PLAYING)
        Gst.debug_bin_to_dot_file(self.pipeline, Gst.DebugGraphDetails.ALL,
                                  './pipeline1.dot')

    def stop_video(self):
        self.pipeline.set_state(Gst.State.NULL)
