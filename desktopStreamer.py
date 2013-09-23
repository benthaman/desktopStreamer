#!/usr/bin/python
# -*- coding: utf-8 -*-

import BaseHTTPServer
 

class AudioRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def send_audio_headers(self):
        self.send_response(200) # http status code OK
        self.send_header("Content-type", "audio/mpeg")
        self.end_headers()

    def do_HEAD(self):
        self.send_audio_headers()

    def do_GET(self):
        self.send_audio_headers()

        print "handling one request"
        f = open("/tmp/audio.mp3")
        data = f.read()
        self.wfile.write(data)
        print "done"

 

if __name__ == "__main__":
    server_address = ('', 8081)
    httpd = BaseHTTPServer.HTTPServer(("", 8081), AudioRequestHandler)
    httpd.serve_forever()
