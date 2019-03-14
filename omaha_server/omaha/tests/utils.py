# coding: utf8

"""
This software is licensed under the Apache 2 license, quoted below.

Copyright 2014 Crystalnix Limited

Licensed under the Apache License, Version 2.0 (the "License"); you may not
use this file except in compliance with the License. You may obtain a copy of
the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations under
the License.
"""

from lxml.builder import E


def create_app_xml(**kwargs):
    events = kwargs.pop('events', [])
    app = dict(**kwargs)
    app = E.app(app)
    if type(events) is not list:
        events = [events]
    for event in events:
        e = E.event(event)
        app.append(e)
    return app
