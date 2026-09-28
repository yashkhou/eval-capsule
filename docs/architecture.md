# Architecture

A capsule contains manifest.json and content-addressed case files. Packing records hashes; verification checks them before assertions execute. The runner evaluates deterministic JSON assertions without contacting a model provider.

## Design constraints

- deterministic offline behavior
- explicit machine-readable inputs and outputs
- small standard-library surface area
- failures are surfaced rather than hidden

## V1 limitation

V1 assertion types are deliberately small; provider adapters can consume the same capsule without changing the archive contract.
