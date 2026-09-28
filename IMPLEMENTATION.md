# Implementation note

Working V1 scope: A portable ZIP format for reproducible agent eval cases: inputs, fixtures, assertions and provenance hashes travel together.

Verified with `python -m unittest discover -s tests -v`.

Known boundary: V1 assertion types are deliberately small; provider adapters can consume the same capsule without changing the archive contract.
