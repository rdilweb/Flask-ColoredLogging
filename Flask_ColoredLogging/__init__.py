"""
MIT License

Copyright (c) 2019-present Reece Dunham & rhymes

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import flask
import time
import datetime
import colors
from rfc3339 import rfc3339


class ColoredLogging(object):
    def __init__(
        self,
        app: flask.Flask,
        exclusions: list = None,
        no_log_ip: bool = False
    ) -> None:
        if app is not None:
            self.app = app
        else:
            raise ValueError("No app object was passed!")
        if exclusions is not None:
            self.exclusions = exclusions
        else:
            self.exclusions = []
        self.no_log_ip = no_log_ip

        self.app.before_request(self.before_inapp_request)
        self.app.after_request(self.after_inapp_request)

    def before_inapp_request(self):
        flask.g.start = time.time()

    def after_inapp_request(self, response) -> flask.Response:
        if flask.request.path in self.exclusions:
            return response

        now = time.time()
        duration = round(now - flask.g.start, 2)
        dt = datetime.datetime.fromtimestamp(now)
        timestamp = rfc3339(dt, utc=True)

        ip = flask.request.headers.get('X-Forwarded-For', flask.request.remote_addr)
        host: str = flask.request.host.split(':', 1)[0]
        args = dict(flask.request.args)
        log_params: dict = [
            ('method', flask.request.method, 'blue'),
            ('path', flask.request.path, 'blue'),
            ('status', response.status_code, 'yellow'),
            ('duration', duration, 'green'),
            ('time', timestamp, 'magenta'),
            ('host', host, 'red'),
            ('params', args, 'blue')
        ]
        if not self.no_log_ip:
            log_params.append(('ip', ip, 'red'))

        parts = []
        for name, value, color in log_params:
            part = colors.color(f"{name}={value}", fg=color)
            parts.append(part)
        line = " ".join(parts)

        self.app.logger.info(line)

        return response
