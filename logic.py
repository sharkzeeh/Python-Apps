import urllib.request
import re
import json


class InstaLoad:

    def __init__(self, inst_url):
        self.url = inst_url
        self.sidecar = []
        self.image = None
        self.video = None

    def download_content(self):
        shared_data = re.compile(r'window._sharedData = ({[^\n]*});')
        contents = urllib.request.urlopen(self.url)
        html = contents.read().decode("utf-8")
        match = re.search(shared_data, html)
        media = json.loads(match.group(1))['entry_data']['PostPage'][0]['graphql']['shortcode_media']
        if media['__typename'] == "GraphSidecar":
            for slide in media['edge_sidecar_to_children']['edges']:
                display_url = slide['node']['display_url']
                self.sidecar.append(display_url)
        elif media['__typename'] == "GraphVideo":
            self.video = media['video_url']
        else:
            self.image = media['display_url']
        return self.image, self.sidecar, self.video
