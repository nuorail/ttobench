# Journey library

## Journey description

Every journey in the library is defined by a JSON file. A journey describes the
timing constraints of a train run on a specific track. It consists of an ordered
list of timing points. The first timing point defines the departure and the last
timing point defines the arrival.

- `metadata` : a dictionary of key-value pairs with general information on the
file content. Required fields: `id`, a unique identifier of the journey that
should contain only letters, numbers and underscores, `associated track`, the unique identifier of the associated track JSON file,
and `library version` for compatibility
reasons. The journey `id` must start with the `associated track` followed by an underscore.
Optional fields: `description`, `created by` and `license`.

- `timing points`: a dictionary containing the units and values of the timing
points. Each timing point is defined as a list with the following order:
  - `position`: the track coordinate of the timing point.
  - `lower time constraint`: the earliest allowed time at this position.
  - `upper time constraint`: the latest allowed time at this position.
  - `lower speed constraint`: the minimum allowed speed at this position.
  - `upper speed constraint`: the maximum allowed speed at this position.

  Time is measured relative to the start of the journey. If a time or speed constraint is not defined, its value should be set to `null`.

## Timing point rules
The following rules should be fulfilled by every journey file:

- The list of timing points must contain at least two entries.
- Timing points must be ordered by increasing position.
- The first timing point represents the departure.
- The last timing point represents the arrival.
- The first and last timing point must have both speed constraints set
  to `0`, which defines departure and arrival at standstill.
- For every defined time constraint, the lower time constraint must be smaller
  than or equal to the upper time constraint.
- For every defined speed constraint, the lower speed constraint must be smaller
  than or equal to the upper speed constraint.
- A value of `null` means that the corresponding constraint is not set.