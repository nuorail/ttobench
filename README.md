# TTOBench v2.0
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
file and as a Git tag) identifies a release of the library, for citation and
provenance.

**The first digit changes when the format breaks**: a parser written for the
previous major release will not read the files of the new one. A minor bump is
additive — new optional fields, new instances, or a whole new library that an
existing parser can ignore.

This is not semantic versioning: there is no patch digit. The rule is a
commitment for releases from v2.0 onwards, and it also describes the history
before it, with a single exception — **v1.1**, which changed the shape of every
track file in a minor bump and is the only past release that would take a major
bump under it.

The `library version` recorded inside a file states the release whose format
that file conforms to, so files written for different releases coexist in the
library — the four train files still read `v1.3` and `v1.4` because the train
format has not changed since. It is the first digit that informs the user whether a previous parser applies.

When updating to a new release, re-read the schema in:
- [tracks/README.md](tracks/README.md)
- [trains/README.md](trains/README.md)
- [journeys/README.md](journeys/README.md)

rather than assuming your parser still applies.
The changes that require it are listed below.

### Version history

Entries marked **Breaking** change the format of data that already existed, and
require updating a parser written for the previous release. Everything else is
additive: new optional fields, or new libraries a previous parser can ignore.

#### v2.0

- **Breaking**: the track's `stops` field is renamed to `timing points`.
- **Breaking**: each entry of `timing points` is now an object rather than a
  bare position.
- **Breaking**: `timing points` uses a `units` dictionary instead of the single
  `unit` key (`{"position": "m"}`).
- **Breaking**: the track length moved to a new required `length` field. It is
  no longer the position of the last entry of `stops`.
- **Breaking**: `timing points` became optional. A track without it has two
  implicit, unnamed timing points, at 0 and at `length`. The rules that the
  first entry be at position 0 and the last one equal the track length are gone.
- `00_reference` and other basic tracks no longer declare `timing points`.
- **Breaking**: a journey's `timing points` entries are objects rather than
  five-element lists.

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
- The track `00_stationX_stationY` was renamed to `CH_StGallen_Wil`; code
  referring to the old id has to be updated.

#### v1.1

- **Breaking**: the top-level `id` moved into a new required `metadata` object,
  which also carries the required `library version` and the optional
  `created by` and `license`.
- **Breaking**: every field became a dictionary of units and values. `stops`
  went from `[0.0, 8500.0, ...]` to `{"unit": "m", "values": [0.0, 8500.0, ...]}`,
  and `speed limits` and `gradients` gained a `units` dictionary alongside their
  `values`. Before this release no units were recorded anywhere.
- Optional `altitude` added to tracks.

#### v1.0

- Initial release: the track library only, as plain JSON.

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
