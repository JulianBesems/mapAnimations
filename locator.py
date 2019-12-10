from geopy.geocoders import Nominatim, Bing

locator = Nominatim(user_agent="myGeocoder")
locator2 = Bing("AtK1OJrFj36vtPbmfr-KMt-HpOX1F2zl9PkW_T4_TzFzJwBuKLUWPflZyvThWX9x")
c = "45.433944, 12.338304"
location = locator.reverse(c)
location2 = locator2.reverse(c)
print("Nominatim: " + location.address)
print("Bing:      " + location2.address)
