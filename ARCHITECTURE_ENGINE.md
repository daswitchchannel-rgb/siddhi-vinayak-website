# Architecture AI / GIS layer

The Siddhi Vinayak repository now includes an integrated preliminary architecture-planning core.

## Implemented
- UP 2025 residential plotted-development calculations.
- FAR bands, setbacks, height, road-width checks and residential parking calculation.
- Preliminary rectangular DXF output.
- Master Plan 2031 coordinate transform/location API.
- `/architecture` browser interface.

## Source basis
The supplied UP Model Building Construction and Development Byelaws 2025 provides residential plotted-development FAR bands in sections 3.2.2.1 and 4.1.6; plotted residential setbacks in section 3.2.4.1; single/multi-unit access and height in sections 4.1.3-4.1.4; and residential parking in section 3.3.4. Site permission remains subject to Master Plan/Zonal Plan and other statutory restrictions.

The official MVDA website publishes the Master Plan 2031 and its high-quality map.

## GIS accuracy
The supplied 2031 source is a cartographic map rather than a cadastral GIS dataset. The integrated transform is therefore explicitly labelled reference. It must not be represented as a legally verified parcel/zoning boundary.

## Safety/accuracy
This is a preliminary design and compliance aid. It does not replace cadastral survey, the authority's sanctioned zoning record, title/lease conditions, NOCs, structural/fire design, or licensed professional review.