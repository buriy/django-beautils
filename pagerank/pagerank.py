from utils.pagerank_checksum import HashURL
from utils.pagerank_checksum import CheckHash
from urllib import quote
import httplib
import urllib2

def _get_rank_request(url):
    hash = CheckHash(HashURL(url))
    return "http://www.google.com/search"+\
        "?client=navclient-auto&features=Rank:&q=info:%s&ch=%s" % (quote(url), hash)

def _get_alexa_request(url):
    if url[:7] == 'http://': url = url[7:]
    return "http://xml.alexa.com/data?cli=10&dat=nsa&"+\
           "ver=quirk-searchstatus&uid=20060820021517&url=%s" % quote(url)
    
def _parse_rank_response(response):
    if response.status == 200 and response.reason == "OK":
        pr = response.read() #Rank_1:1:4
        pr = pr.replace('\n','')
        return int(pr[9:])
    else:
        return -1

def _parse_alexa_response(response):
    if response.status == 200 and response.reason == "OK":
        pr = response.read() #
        pr = pr.replace('\n','')
        try:
            idx = pr.index('<POPULARITY URL=')
        except ValueError:
            return -1
        pos = pr[idx+16:].split('"',4)[3]
        return int(pos)
    else:
        return -1

def get_rank_urllib2(url): #accept custom proxies
    request = _get_rank_request(url)
    response = urllib2.urlopen(request)
    return _parse_rank_response(response)

def get_alexa_urllib2(url): #accept custom proxies
    request = _get_alexa_request(url)
    response = urllib2.urlopen(request)
    return _parse_alexa_response(response)

def get_rank_httplib(url): 
    request = _get_rank_request(url)
    _proto, _slash, site, doc = request.split('/',3)
    google = httplib.HTTPConnection(site)
    google.request('GET', '/'+doc)
    response = google.getresponse()
    return _parse_rank_response(response)

def get_alexa_httplib(url):
    request = _get_alexa_request(url)
    _proto, _slash, site, doc = request.split('/',3)
    alexa = httplib.HTTPConnection(site)
    alexa.request('GET', '/'+doc)
    response = alexa.getresponse()
    return _parse_alexa_response(response)

def google(self, keyword, num=50):
    # Set up connection to google
    google = urllib2.urlopen("http://www.google.com/search?q=%s&sourceid=opera&num=%s&ie=utf-8&oe=utf-8" % (keyword, num))
    #google.request("GET", "/search?q=%s&sourceid=opera&num=10&ie=utf-8&oe=utf-8" % keyword)
    response = google.getresponse()
    if response.status == 200 and response.reason == "OK":
        query_response = ''
        query_response_split = response.read().split('\n')
        for piece in query_response_split:
            query_response += piece
        # Now, parse the query_response string BY HAND (NOT using a parser)
        global domain_list
        domain_list = []
        unsanitized_domain_list = query_response.split("<h2 class=r><a href=\"http://")[1:]
        for mashed_domain in unsanitized_domain_list:
            # Try this. Essentially hoping that there is a 'www.' as prefix for all entries
            #domain_name = mashed_domain.split('/')[0].lower()
            # Just get last 2 sections
            domain_name = mashed_domain.split('/')[0].lower()
            domain_list.append(domain_name)
        #print keyword, domain_list
        return domain_list
    else:
        return None #failed

if __name__ == '__main__':
    #/search?client=navclient-auto&features=Rank:&q=info:http://www.buriy.com/&ch=751875372438
    urls= ["http://www.buriy.com/",
                "http://www.radiomyanmar.com/",
                "http://radiomyanmar.com/",
                "wn.com",
                "http://www.google.com/",
    ]
    kwds = ['test123','buriy.com','yuri baburov']
    for url in kwds: print 'google for',url,'has given',",".join(google(kwds,10)[:3])
    #for url in urls: print 'pagerank of',url,'=',get_rank_httplib(url)
    #for url in urls: print 'alexa position of ',url,'=',get_alexa_httplib(url)
