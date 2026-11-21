# Catworld — Procreate lettering and tracing reference

Two aligned **11 × 8.5-inch landscape PNGs at 600 DPI**, both **6600 × 5100 pixels**:

| File | Contents |
| --- | --- |
| [Catworld-Crimson-Labels-600dpi.png](Catworld-Crimson-Labels-600dpi.png) | 41 labels in crimson `#DC143C`; transparent everywhere outside the lettering. |
| [Catworld-Full-Reference-600dpi.png](Catworld-Full-Reference-600dpi.png) | Registered original map artwork at 50% ink opacity, with the identical crimson lettering and 5-pixel white clearance around the text. |

Revision 2 displays **41 of the original 64 labels: 23 fewer, a 35.9375% reduction**. The complete inventory, including omitted labels, canonical full names, proposed feature anchors and omission reasons, remains in [source/Label-Inventory.json](source/Label-Inventory.json). The font, canvas dimensions and geographic registration are unchanged.

## Use in Procreate

1. Import the full reference PNG as a new canvas. It establishes the exact canvas dimensions and crop.
2. Add a blank drawing layer above the reference. Reduce the reference layer opacity further if useful.
3. Use **Actions → Add → Insert a file** to add the crimson-label PNG above the drawing layer. Keep the same 6600 × 5100 canvas and original size; avoid cropping or manually fitting the text layer to its visible contents.
4. Draw the new coastline, terrain and settlements around the labels. Hide the reference layer when the new drawing is complete; keep the crimson lettering visible.

Both PNGs retain the full canvas, including transparent margins. The lettering layer contains no guide numbers, city symbols, map strokes, white halos or opaque background. Halos appear only in the full reference.

## Lettering and placement

All visible lettering comes from the repository's [catword-3-Regular.ttf](../../fonts/catword-3-Regular.ttf). Glyphs are converted directly to vector outlines, kerned, spaced by arc length, and rotated along smooth curved baselines. The glyph shapes are not stretched or bent. The font's original hand-drawn character remains intact.

The 41 displayed labels retain Panterra, the three provinces, major cities and settlements, mountains and passes, woods, mines, monuments and principal waters. Each has an individually composed cubic Bézier baseline and a written `path_rationale`. Lake, river, forest and mountain-range curves follow their landforms; city and settlement curves remain compact and restrained. The editorial reduction removes minor villages, overlapping regional descriptions and secondary features to create more room around the retained names. Use the full-resolution image when tracing digitally.

Names and feature anchors follow `working/Catworld-Full-Map-Drawing-Guide.pdf` and the pitch deck's regional gazetteer. Coordinates in that guide are drawing proposals. Label positions sit beside the proposed sites; they are not replacements for survey coordinates or final city icons. Province names now sit inland over their corresponding mainland regions: Monteheim across the western uplands, Aurelmark along the central Oudmeer–Vaur–Heilig corridor, and Marenveld across the eastern interior. Their lettering describes broad regions without defining precise borders.

- **Marenveld** follows the latest working name. Eastervael and Highveld are alternate names for the same province, not added regions.
- **Aurelmark**, **Maréhaven**, **Urkronen Alps**, and **Oerkrone** preserve the resolved source spellings. Omitted names, including **Stilwater**, retain their source spellings in the inventory.
- The two generic guide descriptions “Veldemaar lake” and “Veldemaar outlet” were omitted because those features have no established proper names.
- Old London / Rome / Seattle / Milan placeholders were not reintroduced.

Four short display labels keep longer landmark names legible. The inventory preserves their canonical names and anchors:

| Display label | Canonical name |
| --- | --- |
| Windnek Tower | Tower at Windnek |
| Stormhoek | Beacon at Stormhoek |
| Diepe Kuil | Temple at Diepe Kuil |
| Urwald Arch | Arch of Urwald |

## Registration and original artwork

The original `working/catworld_working_base.png` and `.xcf` remain untouched. Their canvas is already Letter landscape at 600 DPI. The XCF contains a numbered guide layered over clean artwork with a slightly different scale and offset.

The clean reference here uses `CATWORLD_drawn_Maps/panterra_v1.PNG`, confirmed identical to the drawing embedded in the full guide, and registers it to ten visible working-base guide anchors. The fitted transform has residuals below 0.51 output pixels at those anchors. Both exported PNGs use the same registration. The small northeast seam between the differently scaled original layers is removed by using one consistent transform across the new reference.

Guide numbers, colored priority markers and the experimental Aurelmark text are removed by returning to the clean source artwork. No new coastline, terrain, river, city drawing or line thinning is introduced. The reference remains an enlarged source drawing for tracing; the new typography is rendered directly at the full requested pixel resolution.

## Editable sources and regeneration

- `source/labels.json`: the 41 displayed labels, font sizes, explicit cubic baseline points, geographic path rationales and original feature anchors.
- `source/Label-Inventory.json`: all 64 canonical names and proposed anchors, with display status and reasons for the 23 omissions.
- `Catworld-Crimson-Labels.svg`: font-independent vector outlines, grouped and named by label.
- `Label-Geometry.json`: exact label and glyph bounds, path measurements, normalized curve geometry and the unique-curve count.
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

Every label in this pack uses a four-point `points` array in output-canvas pixels: `[[start_x, start_y], [control_1_x, control_1_y], [control_2_x, control_2_y], [end_x, end_y]]`. The first and last points set the baseline endpoints; the two middle points control the cubic curve. Edit these points to reposition or reshape a label, and update its `path_rationale` to describe its relationship to the geography.

Optional `align` places the text at the `start`, `center` or `end` of the curve; the default is `center`. Optional `offset` shifts that placement along the path in canvas pixels, with positive values moving toward the path end. The text must fit entirely within the path. `tracking` adds spacing between letters. The renderer retains compatibility with older `x`, `y`, `rise` and `angle` layouts, but this revision uses explicit points for all 41 labels.

`require_individual_paths` is `true`: rendering requires four cubic control points and a nonempty `path_rationale` for every label, and rejects duplicate curve shapes after normalizing position, rotation and scale. `Label-Geometry.json` records the normalized geometry and uniqueness count for inspection. This check supports the individual path designs; their geographic fit is also reviewed visually.

`reference_opacity` is `0.5` and `reference_halo_px` is `5`. These settings affect only the reference composite; the lettering export remains crimson on transparency.

Final checks cover full-resolution dimensions, PNG resolution metadata, transparency, exact visible crimson RGB, all 41 displayed labels, the preserved 64-name inventory, 41 distinct cubic curves, glyph clipping, glyph collisions and visual inspection. PNG's integer pixels-per-metre field represents 600 DPI as approximately 599.9988 DPI.
