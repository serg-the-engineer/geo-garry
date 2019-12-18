This is a package for geo services. Geocoding and distance calculations

# Distance service
**geo_garry.distance.DistanceCalculatorAbstract**
Calculates distance of 2 dimensional geopoint from certain polygon, rounding result to kilometers.
If distance closer to edge, than 1 km, rounds to 1 km.
There are 2 strategies of calculating, both using GoogleMaps

### - Using nearest exits
**geo_garry.distance.NearestExitsGoogleDistanceCalculator**
For provided polygon built KDTree, search 7 nearest polygon vertexes,
and than call google maps to find distance from 7 points.

### - Using polygon center
**geo_garry.distance.PolygonCenterGoogleDistanceCalculator**
For provided point built drivint path from polygon center, and then discard path part inside polygon.
There are situation, when some driving step crosses polygon side. for such case we:

Build line between 2 point. Using geometry difference find part of line outside polygon. Then
calculate length of part inside.

### - Caching
**geo_garry.distance.CachedDistanceCalculator**
To prevent using non-free geo services every time, we cache distance requests results.


### - Moscow and St. Petersburg
**geo_garry.distance.MkadDistanceCalculator**
**geo_garry.distance.KadDistanceCalculator**
There are predefined polygons of KAD and MKAD, and caching mechanism.
For MKAD nearest exits strategy used, for KAD - polygon center.

### - Examples
Cache storage should implement geo_garry.cache.StorageInterface. F.e. redis.StrictRedis
```
import googlemaps
from geo_garry import distance, Coordinates

client = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
cache_storage = SomeCacheStorageAsRedis()

service = distance.MkadDistanceCalculator(storage=storage_mock, api=client)
service.get_distance(Coordinates(latitude=50.4254225, longitude=36.9020654))
```

#  Geocode service
**Geocoder**
Base Interface class with ```get_address```, ```get_coordinates```, ```get_federal_code``` methods. Also there are ```get_geo``` method for getting data by address string. It's hard to parse city title from human typed string, google doing it better. 

### - Caching gmaps results
To prevent using non-free geo services every time, we cache geocode requests results. We cache both coordinates, address, city and federal_code, it helps to save requests in future, so all three methods use same cache object. ```get_geo``` uses different key.
For reverse geocoding there are some heuristic algorithm:
- We round place coordinates for 4 decimal points, and then place address into cache by that value.
- Every time then first of all we rounding coordinates, chech cache, and if empty, calculating.

**Reason and justification**:

Fot latitude every 0,0001 delta in coordinates corresponds to 10 geo meters.
For longitude every 0.0001 delta in coordinates corresponds to 0-10 geo meters depending on Cos(latitude), so for 60 degree latitude (approx. St Petersburg coordinate) it's 5 meters.

Cause of rounding math rules, averagely we lose only half of delta distance at worst.

GPS trackers by itself provide accurasy about 5 meter, plus geocoded building often larger than accurasy at times

### Service providers
For the most use cases GoogleGeocoder is waht you need, but there are openStreetMapsGeocoder for unhappiest failed cases, like Crimea. OpenStrretMapsGeocoder is wrapper around raw requests, and not support caching at the moment

### - Examples
Cache storage should implement geo_garry.cache.StorageInterface. F.e. redis.StrictRedis.

```
import googlemaps
from geo_garry.geocode import GoogleGeocoder

client = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
cache_storage = SomeCacheStorageAsRedis()

geocoder = GoogleGeocoder(storage=cache_storage, api=client)
geocoder.get_address(Coordinates(latitude=50.4254225, longitude=36.9020654)
geocoder.get_coordinates('Moscow City')
```

# Build
## Run tests
pytest tests

## Run pylint
pylint geo_garry

## Run mypy
mypy geo_garry --ignore-missing-imports

Package automatically builds on tags
