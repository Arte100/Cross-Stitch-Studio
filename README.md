# The Jolly Makery

<img src="logo.png" alt="The Jolly Makery logo: an embroidery hoop with stitched roses, a needle and a heart of thread" width="160">

Free tools for people who make things. There are two tools so far: a cross stitch pattern designer that runs in the browser and installs on Android phones and tablets, and a thread colour converter.

**Website: https://thejollymakery.com/**

**Cross stitch tool: https://thejollymakery.com/stitch/**

**Thread colour converter: https://thejollymakery.com/colours/**

No account and no download are needed. Both work on phones, tablets and computers.

## Cross stitch tool

- Aida fabric in 11, 14, 16, 18, 20 and 22 count
- 489 DMC stranded cotton shades, with screen colours measured from our own DMC colour card
- 237 example designs in ten groups
- Backstitch lines, drawn from corner to corner, for outlines and details
- Lettering: type a name, a date or a message, choose a font and a height, and place it as stitches
- Outline and shadow for lettering and for any part of a design, in stitches or as a backstitch line
- Copy or move part of a design, with mirror, flip and turn, to repeat motifs and build borders
- Replace one thread colour with another across the whole design, and tidy stray single stitches
- Photo to pattern converter, and Trace a photo for stitching over a picture by hand
- Cross Stitch it: tick stitches off as you sew, with a count of what is done and what is left
- Shopping list: thread to buy for each colour, shown as the calculated length, the extra and the total, with skeins, plus the fabric size to cut
- Save as an image with or without the grid, and save a printable pattern with the finished picture, a thread key, the shopping list and charts with centre marks, on A4, A3, A5, US Letter or US Legal paper, upright or sideways
- Backup files to keep or send a design
- Six colour themes

## Thread colour converter

- Converts a thread number between DMC, Anchor, Madeira, Cosmo and Sullivans, in either direction
- Search by number, or by colour name for DMC, or browse the whole table by number or by shade
- Shows the two colours side by side, and full screen for holding real thread against
- Matches come from published conversion charts, cross-checked against each other
- Every match is checked by colour. Clear slips in the charts are left out, and where no published match is left, the closest thread by colour is offered and labelled as our own suggestion
- DMC colours are our own measurements. Anchor, Madeira and Cosmo colours are read from published colour cards and charts, so they are less exact

## Files

- `index.html`, `learn/`, `about/` and `feedback/` are the website pages, styled by `site.css`
- `stitch/index.html` is the whole cross stitch tool
- `stitch/manifest.webmanifest` and the icon files make the tool installable
- `stitch/sw.js` lets the tool open without an internet connection
- `stitch/test/index.html` is a test copy, where changes are tried before they reach the tool
- `colours/index.html` is the whole thread colour converter, and `colours/test/index.html` is its test copy
- `_build/colours/build.py` writes the converter from the page design in `template.html`, the published charts in `src/` and the colour readings in `swatches/`. `own_colours.py` brings those colour readings onto our measured DMC scale
- `_build/threads/` holds the scripts that measured the DMC colours from photographs of the colour card
- `sw.js` at the top level retires the offline helper from when the tool lived there
- `_build/build_site.py` writes the website pages and `site.css`. Change the pages there, then run `python3 _build/build_site.py . live`

## Install on Android

Open https://thejollymakery.com/stitch/ in Chrome, open the Chrome menu and choose "Add to Home screen" or "Install app". On some tablets the option is under "Save and share".

## Contributing

Ideas, bug reports and improvements are welcome. Open an issue to describe a problem or a suggestion, or send a pull request with your change.

## Licence

Copyright (C) 2026 Arturas Gulevskis

This program is free software. You can redistribute it and modify it under the terms of the GNU General Public License, version 2, as published by the Free Software Foundation. It comes with no warranty. The full text is in the `LICENSE` file.

The example designs are original drawings made for this project. They show everyday subjects, with no characters, logos or artwork taken from anyone else, and they are covered by the same licence.

The font files in the `fonts` folder are not covered by the licence above. They belong to their authors and are used under the SIL Open Font License, Version 1.1. See `fonts/README.md` and `fonts/OFL.txt`.

DMC, Anchor, Madeira, Cosmo and Sullivans are trademarks of their owners. This project is independent, and is not affiliated with or endorsed by any thread maker.
