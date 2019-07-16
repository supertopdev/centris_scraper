import re
import json
import requests
import requests.exceptions
import pytz
import time
import traceback
from datetime import datetime

def get_first_element(elements):
    return elements[0] if isinstance(elements, list) and len(elements) > 0 else None

def utf8_str(s):
    return s.decode('utf-8') if isinstance(s, bytes) else s

def dump_json(o):
    return json.dumps(o, ensure_ascii=False) if o else None

def deep_get(d, key_str, default_value=None):
    '''
    Get the deep value from Dictionary

    :param d: dict
    :param key_str: str ex: parent.child
    :param default_value: any
    :return: any
    '''

    key_list = key_str.split('.')
    temp = d.copy()

    for k in key_list:
        try:
            temp = temp.get(k)
        except:
            return default_value

    return temp

def safe_request_text(url, headers=None):
    retries = 5
    timeout = .1
    for _ in range(retries):
        try:
            r = requests.get(url, headers=headers)
            try:
                r.content.decode('UTF-8')
            except UnicodeDecodeError:
                r.encoding = 'GB18030'

            if r.status_code == 200:
                return r.text
        except requests.exceptions.RequestException:
            pass

        # Wait 100ms for server response
        time.sleep(timeout)
        timeout *= 2

    return None

def safe_request_json(url, headers=None):
    text = safe_request_text(url, headers)
    try:
        return json.loads(text) if text else None
    except:
        pass
    return None

DEFAULT_TZ = pytz.timezone('Asia/Shanghai')

def timestamp_to_dtstring(t, tz=DEFAULT_TZ):
    if not t or not t.isdigit():
        return None

    return datetime.fromtimestamp(int(t) // 1000, tz).isoformat()

def localtime_to_dtstring():
    return datetime.now(DEFAULT_TZ).astimezone().isoformat()

def print_exception(e):
    print(e)
    traceback.print_stack()

FLOATING_POINT_RGEX = re.compile('\d{1,3}[,\.\d{3}]*\.?\d*')

def _replace_duplicated_seps(price):
    """ 1.264.67 --> # 1264.67, 1,264,67 --> # 1264,67 """
    if '.' in price:
        sep = '.'
    elif ',' in price:
        sep = ','
    else:
        return price
    left_part, reminder = price.rsplit(sep, 1)
    return left_part.replace(sep, '') + '.' + reminder

def _fix_dots_commas(price):
    if '.' and ',' in price:
        dot_index = price.find('.')
        comma_index = price.find(',')
        if dot_index < comma_index:  # 1.264,67
            price = price.replace('.', '')
        else:  # 1,264.45
            price = price.replace(',', '')
    if price.count('.') >= 2 or price.count(',') >= 2:  # something's wrong - # 1.264.67
        price = _replace_duplicated_seps(price)
    return price