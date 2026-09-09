# TTOBench v1.6
Open-source library for train trajectory optimization

[![Validate data](https://github.com/nuorail/ttobench/actions/workflows/validate.yml/badge.svg)](https://github.com/nuorail/ttobench/actions/workflows/validate.yml)

## Content

- [Track library with benchmark instances in JSON format](tracks/README.md)

- [Train library with benchmark instances in JSON format](trains/README.md)

- [Journey library with benchmark instances in JSON format](journeys/README.md)

- [Python utils](utils/)

## Validation

Every track, train and journey in the library is checked against the schema
documented in the READMEs above. The checks run in CI on every push and pull
request ([validate.yml](.github/workflows/validate.yml)), and can be run
locally with:

```
python utils/validate_all.py
```

This reports every file that fails rather than stopping at the first, and exits
non-zero if any did. The individual validators behind it
(`validate_tracks.py`, `validate_trains.py`, `validate_journeys.py`) can also be
run on their own, but resolve their paths relative to the working directory and
so must be started from inside `utils`. They all need only the standard
library.

## Versioning

The library version (`vX.Y`, also recorded as `library version` in every JSON
file and as a Git tag) identifies a **release snapshot** of the library, for
citation and provenance. It is not a semantic-versioning compatibility
contract: a new release may change the format of an existing field, and such
changes have gone out in minor bumps before (`stops` changed shape in v1.1 and
became `timing points` in v1.6). The `library version` recorded inside a file states the release
whose format that file conforms to, so files written for different releases can
coexist in the library.

When updating to a new release, re-read the schema in:
- [tracks/README.md](tracks/README.md)
- [trains/README.md](trains/README.md)
- [journeys/README.md](journeys/README.md)

rather than assuming your parser still applies.
The changes that require it are listed below.

### Version history

Entries marked **breaking** change the format of data that already existed, and
require updating a parser written for the previous release. Everything else is
additive: new optional fields, or new libraries a previous parser can ignore.

#### v1.6

- **breaking**: the track's `stops` field is renamed to `timing points` and
  generalized. It lists the locations a journey may time itself against — the
  places a train may start, finish or stop, and the intermediate locations
  worth constraining a passing time at — rather than stopping places alone.
  Names must be unique within a track, because journeys refer to timing points
  by name.
- **breaking**: each entry of `timing points` is now an object rather than a
  bare position — `{"position": 0.0, "name": "Luzern"}` instead of `0.0`.
  `name` and `coordinates` are optional per entry.
- **breaking**: `timing points` uses a `units` dictionary instead of the single
  `unit` key (`{"position": "m"}`, plus `"coordinates"` when entries carry
  coordinates).
- **breaking**: the track length moved to a new required `length` field. It is
  no longer the position of the last entry of `stops`.
- **breaking**: `timing points` became optional. A track without it has two
  implicit, unnamed timing points, at 0 and at `length`. The rules that the
  first entry be at position 0 and the last one equal the track length are gone
  with the length job.
- **breaking**: the optional `station names` list in `metadata`, introduced
  between releases, is removed — the names live in `timing points` instead.
- `00_reference` and `00_reference_with_tunnels` no longer declare `timing
  points`.
- **breaking**: a journey's `timing points` entries are objects rather than
  five-element lists. Each carries a `type` — `"stopping"` or `"passing"`,
  after the ERTMS/ATO Stopping Point / Passing Point — and locates itself
  either by naming a timing point of the associated track or by an explicit
  `position`, so a journey no longer restates positions the track already
  records. A stopping point carries its `arrival` and `departure` windows in a
  single entry, replacing the pair of entries at the same position, and a
  passing point carries `time` and `speed` windows. Every constraint is a
  `[lower, upper]` pair, replacing the four separate `lower`/`upper`
  `time`/`speed constraint` columns and their four unit keys.

#### v1.5

- Journey library introduced ([journeys/](journeys/README.md)), describing the
  timing constraints of a run on a track.
- Optional `ETCS braking data` added to tracks and trains.

#### v1.4

- Optional `tunnels` added to tracks, and the `00_reference_with_tunnels` track.
- `length` and `tunnel resistance` added to trains.

#### v1.3

- Train library introduced ([trains/](trains/README.md)).

#### v1.2

- Optional `curvatures` added to tracks, as triples of position, radius at
  start and radius at end, so that a section's curvature may vary linearly.
- **breaking**: the track `00_stationX_stationY` was renamed to
  `CH_StGallen_Wil`; code referring to the old id has to be updated.

#### v1.1

- **breaking**: the top-level `id` moved into a new required `metadata` object,
  which also carries the required `library version` and the optional
  `created by` and `license`.
- **breaking**: every field became a dictionary of units and values. `stops`
  went from `[0.0, 8500.0, ...]` to `{"unit": "m", "values": [0.0, 8500.0, ...]}`,
  and `speed limits` and `gradients` gained a `units` dictionary alongside their
  `values`. Before this release no units were recorded anywhere.
- Optional `altitude` added to tracks.

#### v1.0

Initial release: the track library only, as plain JSON.

## Citing this database

- Please use the following citation if you are using this library in a scientific publication:

    ```
    @article{Kouzoupis2023,
    title = {TTOBench -- an Open-Source Library for Train Trajectory Optimization},
    author = {D. Kouzoupis and I. Pendharkar and F. Corman},
    journal = {Operations Research Forum},
    year = {2023},
    number = {67},
    volume = {4},
    doi = {10.1007/s43069-023-00248-x}
    }
    ```

- It is recommended to mention the library version (Git tag) that you use in your simulations
