This is a package for geo services. Geocoding and distance calculations

# Build
## Run tests
pytest tests

## Run pylint
pylint geo_garry

## Run mypy
mypy geo_garry --ignore-missing-imports

# Distance service
Calculates distance of 2 dimensional point from certain polygon
There are 2 strategies of calculating, both using GoogleMaps

### - Using nearest exits.
For provided polygon built KDTree, search 7 nearest polygon vertexes,
and than call google maps to find distance from 7 points.

### - Using polygon center.
For provided point built drivint path from polygon center, and then discard path part inside polygon.
There are situation, when some driving step crosses polygon side. for such case we:
Build line between 2 point. Using geometry difference find part of line outside polygon. Then
calculate length of part inside

### - Moscow and St. Petersburg
There are predefined polygons of KAD and MKAD,
for MKAD nearest exits strategy used, for KAD - polygon center

...to be continued
