from io import BytesIO
import pycurl
import random
import urllib.parse as urlparse

# Base search url
SEARCH_URL = 'https://www.google.com/search?gbv=1&q='

MOBILE_UA = '{}/5.0 (Android 0; Mobile; rv:54.0) Gecko/54.0 {}/59.0'
DESKTOP_UA = '{}/5.0 (X11; {} x86_64; rv:75.0) Gecko/20100101 {}/75.0'

# Valid query params
VALID_PARAMS = ['tbs', 'tbm', 'start', 'near']


def gen_user_agent(normal_ua):
    is_mobile = 'Android' in normal_ua or 'iPhone' in normal_ua

    mozilla = random.choice(['Moo', 'Woah', 'Bro', 'Slow']) + 'zilla'
    firefox = random.choice(['Choir', 'Squier', 'Higher', 'Wire']) + 'fox'
    linux = random.choice(['Win', 'Sin', 'Gin', 'Fin', 'Kin']) + 'ux'

    if is_mobile:
        return MOBILE_UA.format(mozilla, firefox)
    else:
        return DESKTOP_UA.format(mozilla, linux, firefox)


def gen_query(query, args, near_city=None, language='lang_en'):
    param_dict = {key: '' for key in VALID_PARAMS}
    # Use :past(hour/day/week/month/year) if available
    # example search "new restaurants :past month"
    if ':past' in query:
        time_range = str.strip(query.split(':past', 1)[-1])
        param_dict['tbs'] = '&tbs=qdr:' + str.lower(time_range[0])

    # Ensure search query is parsable
    query = urlparse.quote(query)

    # Pass along type of results (news, images, books, etc)
    if 'tbm' in args:
        param_dict['tbm'] = '&tbm=' + args.get('tbm')

    # Get results page start value (10 per page, ie page 2 start val = 20)
    if 'start' in args:
        param_dict['start'] = '&start=' + args.get('start')

    # Search for results near a particular city, if available
    if near_city is not None:
        param_dict['near'] = '&near=' + urlparse.quote(near_city)

    # Set language for results (lr) and interface (hl)
    param_dict['lr'] = '&lr=' + language + '&hl=' + language.replace('lang_', '')

    for val in param_dict.values():
        if not val or val is None:
            continue
        query += val

    return query


class Request:
    def __init__(self, normal_ua, language='lang_en'):
        self.modified_user_agent = gen_user_agent(normal_ua)
        self.language = language

    def __getitem__(self, name):
        return getattr(self, name)

    def get_decode_value(self):
        if 'lang_zh' in self.language:
            return 'gb2312'
        else:
            return 'unicode-escape'

    def send(self, base_url=SEARCH_URL, query='', return_bytes=False):
        response_header = []

        b_obj = BytesIO()
        crl = pycurl.Curl()
        crl.setopt(crl.URL, base_url + query)
        crl.setopt(crl.USERAGENT, self.modified_user_agent)
        crl.setopt(crl.WRITEDATA, b_obj)
        crl.setopt(crl.HEADERFUNCTION, response_header.append)
        crl.setopt(pycurl.FOLLOWLOCATION, 1)
        crl.perform()
        crl.close()

        if return_bytes:
            return b_obj.getvalue()
        else:
            return b_obj.getvalue().decode(self.get_decode_value(), 'ignore')
