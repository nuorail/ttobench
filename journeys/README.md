# Journey library

## Journey description

Every journey in the library is defined by a JSON file. A journey describes the
timing constraints of a train run on a specific track. It consists of an ordered
list of timing points.

A journey file may contain one or more consecutive `journey sections`.
A `journey section` is the part of the journey between two `stopping points`.

There are two types of timing points:

- `stopping`: the train is planned to stop there, within a given time window.
- `passing`: the train is planned to pass there, within a given time window.

**Where a timing point is belongs to the track; what the train does there
belongs to the journey.** A journey timing point therefore does not restate a
position the track already records — it refers to a timing point of the
associated track by `name`, and the position comes from the track file. Only a
location the track does not name is given by an explicit `position`. The type
lives here rather than in the track because the same location is a stopping
point on one journey and a passing point on another.

This split follows the ERTMS/ATO definition of a Timing Point — *"a location
and stopping accuracy defined in the Segment Profile for which a type (Stopping
or Passing Point) and specific time is identified in the Journey Profile"*
(ERTMS/ATO Glossary v2, §3.33) — with the track file in the role of the Segment
Profile and the journey file in that of the Journey Profile.

## Fields

- `metadata` : a dictionary of key-value pairs with general information on the
file content. Required fields: `id`, a unique identifier of the journey that
should contain only letters, numbers and underscores, `associated track`, the unique identifier of the associated track JSON file,
and `library version` for compatibility
reasons. The journey `id` must start with the `associated track` followed by an underscore.
Optional fields: `description`, `created by` and `license`.

- `timing points`: a dictionary with `units` and `values`.

  - `units`: `position` (`m` or `km`), `time` (`s`) and `speed` (`km/h` or
  `m/s`). The position unit applies only to timing points that carry an
  explicit `position`; one that refers to the track by name inherits the
  track's own unit.

  - `values`: the ordered list of timing points, each one a dictionary:

    - `type` (required): `"stopping"` or `"passing"`.

    - `name` **or** `position` (exactly one is required): where the timing
    point is. `name` refers to a named timing point of the associated track and
    is the normal case. `position` gives a track coordinate directly, for a
    location the track does not name — a benchmark waypoint, or an endpoint of
    a track that omits `timing points` and so has two unnamed implicit ones.
    The exact rule, in the order it is applied:

      | entry | condition | outcome |
      | --- | --- | --- |
      | `name` | matches a named timing point of the track | resolved to its position |
      | `name` | no such name | rejected, listing the known names |
      | `position` | outside `[0, length]` | rejected |
      | `position` | within 1e-6 m of a **named** timing point | rejected — refer to it by name |
      | `position` | anything else | accepted as given |

      The fourth row is what stops a journey from restating a position the
      track already records. It fires only against *named* timing points: a
      position landing on an unnamed one is accepted, there being no name to
      redirect to. An explicit position is a location in its own right rather
      than a reference to one, so nothing keeps it in step with the track when
      the track is regenerated — if a journey should survive that, give the
      location a name in the track.

    - the time and speed constraints, each a `[lower, upper]` pair in which
    either bound may be `null`, meaning that side is unconstrained:

      | key | type | meaning |
      | --- | --- | --- |
      | `arrival` | `stopping` | time window for arriving |
      | `departure` | `stopping` | time window for departing |
      | `time` | `passing` | time window for passing |
      | `speed` | `passing` | speed window while passing |

      A `stopping` point takes no `speed`: the speed at a stop is zero by
      definition. The dwell time at an intermediate stopping point is the
      difference between its `departure` and its `arrival`.

  Time is measured relative to the start of the journey.

## Timing point rules

The following rules should be fulfilled by every journey file:

- The list of timing points must contain at least two entries.
- Every `name` must be a named timing point of the associated track.
- Every explicit `position` must lie within `[0, length]`, and must not be
  the position of a named timing point of the track.
- Resolved positions must be strictly increasing.
- The first and last timing point must be of type `stopping`.
- The first timing point has a `departure` and no `arrival`; the last has an
  `arrival` and no `departure`. They are the departure of the first journey
  section and the arrival of the last.
- Every intermediate `stopping` point has both an `arrival` and a `departure`,
  and neither departure bound may be earlier than the corresponding arrival
  bound (no negative dwell time).
- A `passing` point may be neither first nor last, and must not have both speed
  bounds set to zero — that describes a stop, which should say so with
  `"type": "stopping"`.
- For every defined constraint pair, the lower bound must be smaller than or
  equal to the upper bound.
- Every journey section runs from one stopping point to the next, and a journey
  has at least one.

## Example

```json
"timing points": {
    "units": {"position": "m", "time": "s", "speed": "km/h"},
    "values": [
        {"type": "stopping", "name": "St. Gallen", "departure": [0, 0]},
        {"type": "passing", "position": 12500, "time": [480, 540], "speed": [10, null]},
        {"type": "stopping", "position": 15000, "arrival": [620, 680], "departure": [800, 840]},
        {"type": "passing", "position": 20000, "time": [1200, 1250]},
        {"type": "stopping", "name": "Wil SG", "arrival": [1400, 1450]}
    ]
}
```

Two journey sections, delimited by the three stopping points. The termini are
named timing points of `CH_StGallen_Wil`, so their positions are not repeated
here; the other three are locations that track does not declare, and give their
position directly.
