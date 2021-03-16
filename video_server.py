#!/usr/bin/python3
"""
THE CODE COPIED FROM HERE AND UPDATED TO STREAM VIDEO FILES AND MODIFIED TO INCLUDE STREAMING FROM FILE/VIDEO UrL
https://gist.github.com/n3wtron/4624820


Author: Igor Maculan - n3wtron@gmail.com
A Simple mjpg stream http server
"""
import cv2
import threading
import http
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import time
import sys


class CamHandler(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        img_src = 'http://{}:{}/cam.mjpg'.format(server.server_address[0], server.server_address[1])
        self.html_page = """
            <html>
                <head></head>
                <body>
                    <img src="{}"/>
                </body>
            </html>""".format(img_src)
        self.html_404_page = """
            <html>
                <head></head>
                <body>
                    <h1>NOT FOUND</h1>
                </body>
            </html>"""
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def do_GET(self):
        if self.path.endswith('.mjpg'):
            self.send_response(http.HTTPStatus.OK)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            while True:
                try:
                    img = self.server.read_frame()
                    retval, jpg = cv2.imencode('.jpg', img)
                    if not retval:
                        raise RuntimeError('Could not encode img to JPEG')
                    jpg_bytes = jpg.tobytes()
                    self.wfile.write("--jpgboundary\r\n".encode())
                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Content-length', len(jpg_bytes))
                    self.end_headers()
                    self.wfile.write(jpg_bytes)
                    time.sleep(self.server.read_delay)
                except (IOError, ConnectionError):
                    break
        elif self.path.endswith('.html'):
            self.send_response(http.HTTPStatus.OK)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.html_page.encode())
        else:
            self.send_response(http.HTTPStatus.NOT_FOUND)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.html_404_page.encode())


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

    def __init__(self, capture_path, server_address, RequestHandlerClass, bind_and_activate=True):
        HTTPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)
        ThreadingMixIn.__init__(self)
        try:
            # verifies whether is a webcam
            capture_path = int(capture_path)
        except TypeError:
            pass
        except ValueError:
            pass
        self._capture_path = capture_path
        fps = 30
        self.read_delay = 1. / fps
        self._lock = threading.Lock()
        self._camera = cv2.VideoCapture(capture_path)

    def open_video(self):
        if not self._camera.open(self._capture_path):
            raise IOError('Could not open video {}'.format(self._capture_path))

    def read_frame(self):
        with self._lock:
            retval, img = self._camera.read()
            if not retval:
                self.open_video()
        return img

    def serve_forever(self, poll_interval=0.5):
        self.open_video()
        try:
            super().serve_forever(poll_interval)
        except KeyboardInterrupt:
            self._camera.release()


def main():
    address = "0.0.0.0"
    port = 6420
    """
    arg should be:
        int for streaming cameras. Example 0, 1, 2
        url for RTSP video: example rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov
        filepath for video. example sample.mp4
    """
    video = "sample.mp4"
    if (len(sys.argv)>1):
        video = sys.argv[1]
    print("project credit https://gist.github.com/n3wtron/4624820")
    print('{} served on http://{}:{}/cam.mjpg'.format(video, address, port))
    server = ThreadedHTTPServer(video, (address, port), CamHandler)
    server.serve_forever()


if __name__ == '__main__':
    main()
