import urllib2, os, logging, json, re, time

logger = logging.getLogger('bender')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('bender.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

sess_id = "sess_id=sess_jcuRIDXigwxrpSsbCcAINEusFDQSpoSTpQFQfLdC"
url_mask = "http://zachet2.insane.us.to/inbox_json?last_id={}"


def do_request(url):
    opener = urllib2.build_opener()
    opener.addheaders.append(('Cookie', sess_id))
    logger.debug('requesting {}'.format(url))
    
    try:
        f = opener.open(url)
        res = f.read()
        code = f.code
    except urllib2.HTTPError, e:
        code = e.code
        res = ""

    logger.debug('status %s', code)
    return res

link_re = re.compile('http://zachet2.insane.us.to/[^ ]*')

def process_all():
    if os.path.exists('last_id'):
        with open('last_id') as f:
            try:
                last_id = int(f.read())
            except:
                last_id = 0
    else:
        last_id = 0
    logger.debug('processing, last_id = %s', last_id)
    messages = json.loads(do_request(url_mask.format(last_id)))
    for m in messages:
        last_id = m['id']
        logger.debug('processing message %s from %s', m['id'], m['from_id'])
        if m['crypted'] or m['from_id'] == 1:
            continue
        links = link_re.findall(m['text'])
        for l in links:
            do_request(l)

    with open('last_id', 'w') as f:
        f.write(str(last_id))

while True:
    try:
        process_all()
    except:
        logger.exception("bad")
    time.sleep(1)
