# Track library

## Track description

Every track in the library is defined by a JSON file with the following
fields:

- `metadata` : a dictionary of key-value pairs with general information on the
file content. Required fields: `id`, a unique identifier of the track that should
contain only letters, numbers and underscores, and `library version` for compatibility
reasons. Optional fields: `description`, `created by` and `license`.

- `length`: the length of the track *S*, as a `unit`/`value` pair. Every
position in the file — timing points, speed limits, gradients, curvatures,
tunnels — must lie within `[0, length]`.

- `altitude`: altitude at beginning of track. This field is optional and may
be used in combination with the gradients to plot the altitude profile of the
complete track.

- `timing points` (optional): the locations on the track that a journey may
time itself against — the places where a train may start or finish, where it
may stop, and the intermediate locations whose passing time is worth
constraining. Each one is a dictionary describing a single location. **The
field may be omitted**, in which case the track has exactly two implicit timing
points, at position 0 and at `length` — this is the natural choice for a track
with no intermediate stations, where an explicit list would only restate
`length`. A timing point may additionally carry:

  - `position`: the only required key. Positions must be strictly increasing and lie within `[0, length]`.
Trajectories may be derived from any timing point in the list to any later one.

  - `name` (optional): the name of the station or location, as a string. Names
  must be unique within a track, because a journey refers to a timing point by
  name (see [journeys/README.md](../journeys/README.md)). Simply omit the key
  for a location that has no name worth recording (a purely technical or
  intermediate point, or one whose name is not known) — there is no placeholder
  value, and naming some timing points of a track but not others is allowed.

  - `coordinates` (optional): the geographic position of the timing point, as a
  pair `[longitude, latitude]` in WGS 84 (EPSG:4326) decimal degrees. Note that
  the order is longitude first, following the GeoJSON convention. Requires
  `coordinates` to be declared in `units`.

  Each attribute is stored in the timing point it belongs to and addressed by
  its key, so that adding a new one never changes how the existing ones are
  read. This is deliberately different from the `[position, value]` lists used
  by `speed limits`, `gradients` and `curvatures` below: those describe
  piecewise-constant properties of the track, where every entry has the same
  fixed shape, whereas a timing point is a place with a variable set of known
  attributes.

  **What a timing point is not**: whether the train stops at one or merely
  passes it is not a property of the track. The same location is a stopping
  point for one journey and a passing point for another, so the type — and the
  times — are given per journey, in the journey's own `timing points` field.

  For example, a track whose middle timing point is an unnamed technical point
  and whose terminus has known coordinates:

  ```json
  "length": {"unit": "m", "value": 125503.0},
  "timing points": {
      "units": {"position": "m", "coordinates": "deg"},
      "values": [
          {"position": 0.0, "name": "Luzern"},
          {"position": 10743.0},
          {"position": 16216.0, "name": "Küssnacht am Rigi",
           "coordinates": [8.4407, 47.0857]}
      ]
  }
  ```

- `speed limits`: a list of pairs - position, speed limit - indicating
the beginnings of track sections and their respective velocity restrictions.
The positions must be strictly increasing and every speed limit should be
different than its predecessor (otherwise there would be no need to add this
pair in the list). The position of the first pair should be 0 and the position
of the last pair must be smaller than the length of the track.

- `gradients` (optional): a list of pairs - position, gradient - indicating the
beginnings of track sections and their respective (approximately constant)
slope. The positions must be strictly increasing and every gradient should be
different than its predecessor. Positive and negative gradient values indicate
uphill and downhill sections respectively. The position of the first pair should
be 0 and the position of the last pair must be smaller than the length of the track.
The field can be omitted for level tracks.

- `curvatures` (optional): a list of triples - position, radius at start, and radius at end -
indicating the beginnings of track sections and the corresponding curvature specifications.
Note that the curvature of the track at a point is the reciprocal of the (signed) radius of the
osculating circle at that point. A positive radius indicates a right-hand turn while
a negative radius a left-hand turn. If the radius at start is equal to the radius at end
then the track section has constant curvature. For a straight track the two radii have value "infinity".
Different values for radius at start and radius at end denote a track section where the
curvature of the section varies linearly with the travelled distance (clothoid curve) to
interpolate between the two radii values. Note that the positions must be strictly
increasing. The position of the first triple should be 0 and the position of the
last triple must be smaller than the length of the track. The field can be omitted for straight tracks.

- `tunnels` (optional): a list of triples - position, length, and cross section - indicating the
beginnings of track sections with tunnels and their respective length and cross section.
The positions must be strictly increasing and the length must be nonnegative.
The position of a tunnel and its length must be shorter then the length of the whole track.
If a single physical tunnel has multiple cross sections along its length, split it into
multiple tunnel entries, one for each constant-cross-section section.
The field can be omitted for tracks without tunnels.

Note that the positions of speed limits, gradients, and curvatures will in general
not coincide and a preprocessing step to derive track sections with constant properties
is necessary in the context of trajectory optimization. This representation,
however, makes a clear distinction between points with a speed limit change,
points with a slope change, and points with a curvature change. In this way the
interpretation of track properties is simplified.

- `ETCS braking data` (optional): infrastructure-dependent parameters used for the calculation of ETCS braking curves.
The braking curve is computed for a "Gamma-Train" and intervention by the service brake is allways enabled.
If `ETCS braking data` is defined, all of the following subfields must be provided:

  - `M_NVAVADH`: national value defining the additional delay before the emergency brake is considered available.

  - `Kt_int`: correction factor used for the intervention braking curve.

## Content

- [This table](tracks.csv) summarizes the collected benchmark instances and some of their properties

