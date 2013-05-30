# -*- coding: utf-8 -*-

def geo_locate(ip="",with_proxy=False):                                                   # fetch location based on IP
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(5)
    try:
        if with_proxy:
            geo_json = urllib2.urlopen('http://freegeoip.net/json/').read()
        else:
            proxy_handler = urllib2.ProxyHandler({})
            opener = urllib2.build_opener(proxy_handler)
            req = urllib2.Request('http://freegeoip.net/json/%s' % ip)
            r = opener.open(req)
            geo_json = r.read()
    except Exception as e:
        signal.alarm(0)
        if str(e).find("404") != -1:
            return ["No location info available for IP","","","","",""]
        return ["failed: %s" % e,"","","","",""]
    signal.alarm(0)

    geo = json.loads(geo_json)

    city = geo[u"city"].encode('utf-8')
    region = geo[u"region_name"].encode('utf-8')
    country = geo[u"country_name"].encode('utf-8')
    zipcode = geo[u"zipcode"].encode('utf-8')

    lat = geo[u"latitude"]
    lng = geo[u"longitude"]

    return [city,country,region,zipcode,lat,lng]