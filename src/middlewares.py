import random


class FakePlatformMiddleware:
    '''
    This class is a Scrapy middleware that intercepts each request and adds additional data to it. 
    As GBC is aware that each representative has a different preference for operating systems (OS)
    and web browsers, this middleware randomly selects an OS and web browser user agent to be applied 
    to each request before it is sent. The user agent is added to the request headers and the OS is 
    added to the request metadata. This allows us to send the request to the daxiongmao.js endpoint
    and deceive GBC, who is not as intelligent as it seems.
    '''

    all_platforms = (
        {
            "os": "Win32",
            "ua": "Mozilla/5.0 (Windows NT 5.1 rv: 52.0) Gecko/20100101 Firefox/52.0"
        },
        {
            "os": "Win64",
            "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
        },
        {
            "os": "MacIntel",
            "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15"
        },
        {
            "os": "iPhone",
            "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
        },
        {
            "os": "iPad",
            "ua": "Mozilla/5.0 (iPad; CPU OS 14_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
        },
        {
            "os": "Linux i686",
            "ua": "Mozilla/5.0 (X11; Linux i686; rv:52.0) Gecko/20100101 Firefox/52.0"
        },
        {
            "os": "Linux x86_64",
            "ua": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
        },
        {
            "os": "FreeBSD i386",
            "ua": "Mozilla/5.0 (FreeBSD; U; FreeBSD i386; en-US) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36"
        },
        {
            "os": "FreeBSD amd64",
            "ua": "Mozilla/5.0 (FreeBSD; U; FreeBSD amd64; en-US) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36"
        },
        {
            "os": "OpenBSD i386",
            "ua": "Mozilla/5.0 (X11; OpenBSD i386; rv:52.0) Gecko/20100101 Firefox/52.0"
        },
        {
            "os": "OpenBSD amd64",
            "ua": "Mozilla/5.0 (X11; OpenBSD amd64; rv:52.0) Gecko/20100101 Firefox/52.0"
        },
        {
            "os": "SunOS i86pc",
            "ua": "Mozilla/5.0 (X11; SunOS i86pc) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
        },
        {
            "os": "SunOS sun4u",
            "ua": "Mozilla/5.0 (X11; SunOS sun4u) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
        },
        {
            "os": "Android",
            "ua": "Mozilla/5.0 (Android; Mobile; rv:58.0) Gecko/58.0 Firefox/58.0"
        },
    )

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def process_request(self, request, spider):
        if 'fake_platform' in request.meta:
            fake_platform = self._get_random_platform()

            fake_os = fake_platform['os']
            fake_ua = fake_platform['ua']

            request.headers.update({'user-agent': fake_ua})
            request.meta.update({'os': fake_os})

            return None

    def _get_random_platform(self):
        return random.choice(self.all_platforms)
