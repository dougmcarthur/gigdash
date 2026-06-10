# Display assets

- **`photo.jpg`** — drop your photo here (square crop works best; it's shown in a
  circle). Until it exists, the display falls back to your initials.
- **`qr.svg`** — pre-generated QR code for <https://links.dougmcarthur.net>.
  To regenerate (e.g. if the URL changes):

  ```sh
  qrencode -t SVG -o qr.svg -m 2 "https://links.dougmcarthur.net"
  ```
