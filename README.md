# Website

This website is built using [Docusaurus](https://docusaurus.io/), a modern static website generator.

## Installation

```bash
yarn
```

## Local Development

```bash
yarn start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

## Build

```bash
yarn build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

## Deployment

Deployment is automatic. Pushing to `main` triggers
[`.github/workflows/deploy.yml`](.github/workflows/deploy.yml), which builds the
site and publishes it to GitHub Pages:

**https://0xarmagan.github.io/eez-docs/**

The build runs with `onBrokenLinks: 'throw'`, so a broken internal link fails the
workflow instead of shipping. You can also trigger a deploy by hand from the
repository's Actions tab.

The specification pages under `docs/spec/` are generated from
[eez-core-protocol/docs](https://github.com/eez-association/eez-core-protocol/tree/main/docs)
by `project/tooling/spec-transfer.py` — edit that script and re-run it rather than
hand-editing those pages.
