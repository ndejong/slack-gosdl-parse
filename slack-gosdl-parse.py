#!//usr/bin/env python3

import os
import glob
import json
import argparse
import datetime

import dominate
from dominate.tags import *


class SlackGoSDLParseException(Exception):
    pass


class SlackGoSDLParse:

    args = None
    debug = None
    name = 'Slack - Security Development Lifecycle Checklist'

    def __init__(self):
        parser = argparse.ArgumentParser(description=self.name)
        parser.add_argument('--path', '-p', type=str, metavar='<path>', required=True,
                            help='Base JSON modules path to walk for documentation content.')
        parser.add_argument('--debug', '-d', action='store_true',
                            help='No debug there is Luke')
        self.args = parser.parse_args()
        self.debug = self.args.debug

    def main(self):
        content = self.collect_content(path=self.args.path)
        document = self.render_document(content)
        print(document)

    def render_document(self, content):
        document = dominate.document(title=self.name)
        with document.head:
            link(rel='stylesheet', href='https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.1.3/css/bootstrap.css')
            script(type='text/javascript', src='https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.1.3/js/bootstrap.js')
            style(self.__stylesheet())

        with document:
            with div(cls='container'):
                with div(cls='row'):
                    with div(cls='col-12'):
                        h1(self.name, cls='heading')

                for key in sorted(content.keys()):
                    with div(cls='row'):
                        with div(cls='col-12'):
                            with div(cls='section-head'):
                                h2('{}'.format(key), cls='title')
                                p('{}'.format(content[key]['description']), cls='description')

                            for question_category in content[key]['questions']:
                                h3('{}'.format(question_category), cls='question_category')
                                with ul():
                                    for question in content[key]['questions'][question_category]:
                                        li('{}'.format(question), cls='question')
                    hr()
                p('Generated: {}'.format(datetime.datetime.now()))
        return str(document).replace("’","'") # haters

    def collect_content(self, path, extension='json'):
        if not os.path.isdir(path):
            raise SlackGoSDLParseException('Source modules content path not found', path)
        content = {}
        for filename in glob.iglob(os.path.join(path, '**', '*.{}'.format(extension)), recursive=True):
            content = {**content, **self.parse_content_file(filename)}
        return content

    def parse_content_file(self, filename):
        if not os.path.isfile(filename):
            raise SlackGoSDLParseException('Source content file not found', filename)
        with open(filename, 'r') as f:
            content = json.load(f)
        if 'category' in content.keys():
            return {'{} - {}'.format(content['category'], content['title']): content}
        return {'{}'.format(content['title']): content}

    def __stylesheet(self):
        return """
            .heading { 
                font-weight: bold;
                border-bottom: 1px solid #555;
                margin-bottom: 25px;
            }
            .section-head {
                background-color: #ddd;
                padding: 10px 10px 1px 10px;
            };
        """

SlackGoSDLParse().main()

