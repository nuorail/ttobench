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

- `length` (optional): total length of the train.

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

- `tunnel resistance` (optional): coefficients for additional aerodynamic resistance in tunnels, given for different tunnel cross-sectional areas. The field is a dictionary indexed by `cross section`.

- `ETCS braking data` (optional): train-specific parameters used for the simplified calculation of ETCS braking curves. The field contains emergency and service braking deceleration curves as functions of velocity, as well as correction factors, time delays and speed uncertainty values. Infrastructure-dependent ETCS braking parameters are defined in the Track.json.
  If `ETCS braking data` is defined, all of the following subfields must be provided:

  - `A_brake_emergency`: emergency braking deceleration curve. Each entry contains velocity and the corresponding emergency braking deceleration. Braking deceleration are positive by convention.

  - `A_brake_service`: service braking deceleration curve. Each entry contains velocity and the corresponding service braking deceleration. Braking deceleration are positive by convention.

  - `K_dry_rst`: correction factor for dry rail conditions.

  - `K_wet_rst`: correction factor for wet rail conditions.

  - `T_traction`: traction cut-off delay.

  - `T_be`: emergency brake build-up time.

  - `T_bs`: service brake build-up time.

  - `v_uncertainty`: train-related speed uncertainty.

NOTE: documentation of vehicle efficiency is pending.

