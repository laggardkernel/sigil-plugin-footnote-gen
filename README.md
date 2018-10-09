# Duokan Footnote Generator/Linker

[![License: MIT][license icon]][license]

Generate Duokan style footnotes, which are compatible with Kindle and iBooks (macOS only).

## Usage
1. Quote your anchor number as `[1]`. Do the same on definition number. And make sure the definition content is encapsulated with `<p>` directly as `<p>[1] This is the definition.</p>`

2. Run the plugin.

![img/preview-01.jpg](../assets/img/preview-01.jpg?raw=true)

## Setup
production
- `tkinter`
- `chardet`
- `sigil_bs4` or `beautifulsoup4`

development
- `black`, code formatter

## License

The MIT License (MIT)

Copyright (c) 2019 laggardkernel

[license icon]: https://img.shields.io/badge/License-MIT-yellow.svg
[license]: https://opensource.org/licenses/MIT
