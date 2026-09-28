# eval-capsule

A portable ZIP format for reproducible agent eval cases: inputs, fixtures, assertions and provenance hashes travel together.

## What it does

- packs a manifest plus referenced files into one deterministic-ish capsule
- verifies SHA-256 provenance on unpack/run
- supports equality, contains and exit-code-free JSON assertions
- rejects unsafe ZIP paths during extraction

## Quick start

```bash
PYTHONPATH=src python -m eval_capsule pack examples/case capsule.zip && PYTHONPATH=src python -m eval_capsule run capsule.zip
```

No model API, network service, or third-party package is required.

## Architecture

A capsule contains manifest.json and content-addressed case files. Packing records hashes; verification checks them before assertions execute. The runner evaluates deterministic JSON assertions without contacting a model provider.

See [`docs/architecture.md`](docs/architecture.md) for the data model and trade-offs.

## V1 boundary

V1 assertion types are deliberately small; provider adapters can consume the same capsule without changing the archive contract.

## Development

```bash
python -m unittest discover -s tests -v
```

MIT licensed.
