# -*- coding: utf-8 -*-
import urllib2
import json

def locate(ip="",with_proxy=False):													  # fetch location based on IP
	if not with_proxy:
		proxy_handler = urllib2.ProxyHandler({})
		opener = urllib2.build_opener(proxy_handler)
		req = urllib2.Request('http://freegeoip.net/json/%s' % ip)
		r = opener.open(req)
		geo_json = r.read()
	else:
		geo_json = urllib2.urlopen('http://freegeoip.net/json/%s' % ip).read()

	geo = json.loads(geo_json)

	city = geo[u"city"].encode('utf-8')
	region = geo[u"region_name"].encode('utf-8')
	country = geo[u"country_name"].encode('utf-8')
	zipcode = geo[u"zipcode"].encode('utf-8')

	lat = geo[u"latitude"]
	lng = geo[u"longitude"]

	return [city,country,region,zipcode,lat,lng]

print("Proxied:   %s" % locate(with_proxy=True))
print("No-Proxy:  %s" % locate(with_proxy=False))
print("Specific:  %s" % locate(ip="114.201.209.80"))