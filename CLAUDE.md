# GigDash — notes for Claude sessions

## Encrypted songs

`songs/*.cho` (the lyrics catalog) is encrypted at rest in git using
[transcrypt](https://github.com/elasticdog/transcrypt) (vendored at
`tools/transcrypt`). In a fresh clone the files are OpenSSL ciphertext.

To unlock (requires the `GIGDASH_SONGS_KEY` secret, plus `xxd`; if `column`
is missing, shim it with `printf '#!/bin/sh\nexec cat\n'`):

```sh
tools/transcrypt -c aes-256-cbc -p "$GIGDASH_SONGS_KEY" -y
```

After unlocking, the working tree shows plaintext and commits encrypt
transparently via the git clean/smudge filters.

Rules:

- NEVER commit plaintext lyrics outside the transcrypt filter (e.g. don't
  rename the folder or change `.gitattributes` patterns without re-checking
  what gets staged; verify with `git cat-file blob $(git ls-files -s
  "songs/<file>" | awk '{print $2}')` — it must start with `U2FsdGVk`).
- Songs must never be added to the GitHub repo via the web UI — uploads
  bypass the encryption filter.
- Lyrics must never be served by the public website. Cloudflare Pages
  deploys only `display/`; keep songs out of that folder.

## Deployment

- Pushes to `main` auto-deploy `display/` to https://gigdash.pages.dev
  (Cloudflare Pages, project "gigdash").
- Work directly on `main`; do not create branches (owner preference).
