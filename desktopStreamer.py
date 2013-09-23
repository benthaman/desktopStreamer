#!/usr/bin/python
# -*- coding: utf-8 -*-

import BaseHTTPServer
import os
import signal
import subprocess
import sys

# Playing from the android browser, there is awful delay (~15s). This is a
# client-side behavior. This can be confirmed by playing with "mplayer -cache
# 32" for example.

# Inspired by:
# http://moozing.wordpress.com/2011/12/29/gstreamer-and-html5/
# http://stackoverflow.com/questions/7502380/streaming-pulseaudio-to-file-possibly-with-gstreamer

# TODO
# * support multiple codecs
# * the android browser seems to retry a few times when beginning to play,
#   especially when playing silence. Investigate it...


class AudioRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/mp3":
            content_type = "audio/mpeg"
            encoder_args = ["lame", "-r", "-"]
        else:
            self.send_response(404) # http status code Not Found
            return

        self.send_response(200) # http status code OK
        self.send_header("Content-type", content_type)
        self.end_headers()

        pipe = os.pipe()
        sp_source= subprocess.Popen(["parec", "--format=s16le",
                                     "--device=alsa_output.pci-0000_00_1b.0.analog-stereo.monitor"],
                                    stdout=pipe[1], stderr=sys.stderr)
        sp_encoder= subprocess.Popen(encoder_args, stdin=pipe[0],
                                     stdout=self.wfile, stderr=sys.stderr)

        try:
            while True:
                (pid, tmp,) = os.wait()
                if pid == sp_source.pid:
                    sp_source.wait()
                    os.kill(sp_encoder.pid, signal.SIGTERM)
                elif pid == sp_encoder.pid:
                    sp_encoder.wait()
                    # source should get a sigpipe already, but it looks like
                    # parec ignores it
                    os.kill(sp_source.pid, signal.SIGTERM)
        except OSError:
            pass


if __name__ == "__main__":
    httpd = BaseHTTPServer.HTTPServer(("", 8081), AudioRequestHandler)
    httpd.serve_forever()
