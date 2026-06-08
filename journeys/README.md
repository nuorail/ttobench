# Journey library

## Journey description

Every journey in the library is defined by a JSON file with the following
fields:

- `metadata` : a dictionary of key-value pairs with general information on the
file content. Required fields: `id`, a unique identifier of the train that should
contain only letters, numbers and underscores, and `library version` for compatibility
reasons. Optional fields: `description`, `created by` and `license`.

- `associated track id`: number of seats.

- `timing points`: number of seats.