# Catworld — Procreate lettering and tracing reference

Two aligned **11 × 8.5-inch landscape PNGs at 600 DPI**, both **6600 × 5100 pixels**:

| File | Contents |
| --- | --- |
| [Catworld-Crimson-Labels-600dpi.png](Catworld-Crimson-Labels-600dpi.png) | 64 names in crimson `#DC143C`; transparent everywhere outside the lettering. |
| [Catworld-Full-Reference-600dpi.png](Catworld-Full-Reference-600dpi.png) | Registered original map artwork, softened to 60% ink opacity, with the identical crimson lettering. White clearance around text makes the heavy reference lines easier to read. |

## Use in Procreate

1. Import the full reference PNG as a new canvas. It establishes the exact canvas dimensions and crop.
2. Add a blank drawing layer above the reference. Reduce the reference layer opacity further if useful.
3. Use **Actions → Add → Insert a file** to add the crimson-label PNG above the drawing layer. Keep the same 6600 × 5100 canvas and original size; avoid cropping or manually fitting the text layer to its visible contents.
4. Draw the new coastline, terrain and settlements around the labels. Hide the reference layer when the new drawing is complete; keep the crimson lettering visible.

Both PNGs retain the full canvas, including transparent margins. The lettering layer contains no guide numbers, city symbols, map strokes, white halos or opaque background. Halos appear only in the full reference.

## Lettering and placement

All visible lettering comes from the repository's [catword-3-Regular.ttf](../../fonts/catword-3-Regular.ttf). Glyphs are converted directly to vector outlines, kerned, spaced by arc length, and rotated along smooth curved baselines. The glyph shapes are not stretched or bent. The font's original hand-drawn character remains intact.

The 64 names cover Panterra, the three provinces, cities and settlements, mountains and passes, woods, mines, monuments, rivers, lakes and seas. Broad names use generous arcs; small settlements use subtler curves. The dense Vaur corridor is arranged to keep the correct upper-to-lower river sequence without colliding letters. Some minor settlement labels are approximately 6–7 points at print size; use the full-resolution image when tracing digitally.

Names and feature anchors follow `working/Catworld-Full-Map-Drawing-Guide.pdf` and the pitch deck's regional gazetteer. Coordinates in that guide are drawing proposals. Label positions sit beside the proposed sites; they are not replacements for survey coordinates or final city icons. Province labels use broad display offsets, following the convention in the working base, rather than defining borders.

- **Marenveld** follows the latest working name. Eastervael and Highveld are alternate names for the same province, not added regions.
- **Aurelmark**, **Stilwater**, **Maréhaven**, **Urkronen Alps**, and **Oerkrone** preserve the resolved source spellings.
- The two generic guide descriptions “Veldemaar lake” and “Veldemaar outlet” were omitted because those features have no established proper names.
- Old London / Rome / Seattle / Milan placeholders were not reintroduced.

## Registration and original artwork

The original `working/catworld_working_base.png` and `.xcf` remain untouched. Their canvas is already Letter landscape at 600 DPI. The XCF contains a numbered guide layered over clean artwork with a slightly different scale and offset.

The clean reference here uses `CATWORLD_drawn_Maps/panterra_v1.PNG`, confirmed identical to the drawing embedded in the full guide, and registers it to ten visible working-base guide anchors. The fitted transform has residuals below 0.51 output pixels at those anchors. Both exported PNGs use the same registration. The small northeast seam between the differently scaled original layers is removed by using one consistent transform across the new reference.

Guide numbers, colored priority markers and the experimental Aurelmark text are removed by returning to the clean source artwork. No new coastline, terrain, river, city drawing or line thinning is introduced. The reference remains an enlarged source drawing for tracing; the new typography is rendered directly at the full requested pixel resolution.

## Editable sources and regeneration

- `source/labels.json`: all text, font sizes, baseline curves, positions and original feature anchors.
- `Catworld-Crimson-Labels.svg`: font-independent vector outlines, grouped and named by label.
- `Label-Geometry.json`: exact label and glyph bounds.
- `source/Registration.json`: source image hash, registration transform and fitted anchor measurements.
- `source/reference-base.png`: the registered clean artwork used for the composite.
- `source/render_labels.py`: deterministic export script.

Install Python dependencies from `source/requirements.txt` and make the Inkscape CLI available on your PATH. From the repository root:

```bash
python -m pip install -r working/procreate/source/requirements.txt
python working/procreate/source/render_labels.py
```

The optional preview command renders small inspection copies without changing the final PNGs:

```bash
python working/procreate/source/render_labels.py --output /tmp/catworld-preview --preview 2200
```

In `labels.json`, `x` and `y` mark the centre of a label's baseline in output pixels. Positive `rise` arches its middle upward; `angle` rotates clockwise. `tracking` adds spacing between letters. A `points` array can supply a custom quadratic or cubic Bézier baseline. `reference_opacity` and `reference_halo_px` affect only the reference composite.

Final checks include full-resolution dimensions, PNG resolution metadata, transparency, exact visible crimson RGB, all 64 names, glyph clipping, glyph collisions and visual inspection. PNG's integer pixels-per-metre field represents 600 DPI as approximately 599.9988 DPI.
