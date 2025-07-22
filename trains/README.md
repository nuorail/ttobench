# Train library

## Train description

Every train in the library is defined by a JSON file with the following
fields:

- `metadata` : a dictionary of key-value pairs with general information on the
file content. Required fields: `id`, a unique identifier of the train that should
contain only letters, numbers and underscores, and `library version` for compatibility
reasons. Optional fields: `description`, `created by` and `license`.

- `num seats` (optional): number of seats.

- `num coaches` (optional): number of coaches in train configuration, including locomotive(s).

- `mass`: the mass of the train.

- `rho` (optional): rotating mass factor. If omitted, total mass is equal to mass.

- `max traction power`: maximum traction power of all motors.

- `max reg braking power`: maximum regenerative braking power of all motors. Positive by convention.

- `max traction force`: maximum traction force of all motors.

- `max reg braking force`: maximum regenerative braking force of all motors. Positive by convention.

- `max pn braking force` (optional): maximum pneumatic braking force. Positive by convention. If omitted, maximum force is equal to 0.

- `max acceleration` (optional): maximum vehicle acceleration for passenger comfort.

- `max deceleration` (optional): maximum vehicle deceleration for passenger comfort. Positive by convention.

- `max speed`: maximum vehicle speed.

- `rolling resistance r0`: constant coefficient of rolling resistance.

- `rolling resistance r1`: linear coefficient of rolling resistance.

- `rolling resistance r2`: quadratic coefficient of rolling resistance.

NOTE: documentation of vehicle efficiency is pending.

