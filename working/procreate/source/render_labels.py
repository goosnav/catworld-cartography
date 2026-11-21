#!/usr/bin/env python3
"""Render registered, curved Catworld lettering from the repository font.

All coordinates and font sizes in the layout are full-resolution canvas pixels.
Each glyph retains its original outline and rotates rigidly along the baseline.
Positive ``rise`` arches a label upward: (x, y) is the baseline's centre and
the two baseline endpoints sit ``rise`` pixels below it. ``angle`` is clockwise.
``points`` optionally supplies 2, 3, or 4 global Bezier control points instead.
``reference_opacity`` (default 1) and ``reference_halo_px`` (default 0) affect
only the flattened reference; the transparent label export remains unchanged.

Dependencies: Python packages in requirements.txt, and the Inkscape CLI.
The SVG contains outlined glyphs, so subsequent rendering needs no font install.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
from xml.etree import ElementTree as ET

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageColor, ImageFilter, PngImagePlugin


REPO_ROOT = Path(__file__).resolve().parents[3]
SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


def tag(name: str) -> str:
    return f"{{{SVG_NS}}}{name}"


def resolve_repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO_ROOT / path


def num(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".") or "0"


@dataclass
class Glyph:
    name: str
    advance: float
    x_offset: float = 0.0
    y_offset: float = 0.0


class OutlinedFont:
    """Small Latin shaper supporting the supplied font's GPOS pair kerning."""

    def __init__(self, path: Path):
        self.font_path = path
        self.font = TTFont(path)
        self.glyphs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.units = self.font["head"].unitsPerEm
        self.paths: dict[str, str] = {}
        self.kern_lookups = []
        if "GPOS" in self.font:
            table = self.font["GPOS"].table
            indices = set()
            if table.FeatureList:
                for feature in table.FeatureList.FeatureRecord:
                    if feature.FeatureTag == "kern":
                        indices.update(feature.Feature.LookupListIndex)
            if table.LookupList:
                self.kern_lookups = [table.LookupList.Lookup[i] for i in sorted(indices)]

    @staticmethod
    def apply_value(glyph: Glyph, value) -> None:
        if value is not None:
            glyph.advance += getattr(value, "XAdvance", 0) or 0
            glyph.x_offset += getattr(value, "XPlacement", 0) or 0
            glyph.y_offset += getattr(value, "YPlacement", 0) or 0

    def shape(self, text: str) -> list[Glyph]:
        missing = sorted({c for c in text if ord(c) not in self.cmap})
        if missing:
            raise ValueError(f"Font lacks characters {missing!r} in {text!r}")
        result = [Glyph(self.cmap[ord(c)], self.font["hmtx"].metrics[self.cmap[ord(c)]][0]) for c in text]
        for index, (left, right) in enumerate(zip(result, result[1:])):
            if self.kern_lookups:
                for lookup in self.kern_lookups:
                    for raw_subtable in lookup.SubTable:
                        subtable = raw_subtable
                        kind = lookup.LookupType
                        if kind == 9:
                            kind = subtable.ExtensionLookupType
                            subtable = subtable.ExtSubTable
                        if kind != 2 or left.name not in subtable.Coverage.glyphs:
                            continue
                        pair = None
                        if subtable.Format == 1:
                            covered_index = subtable.Coverage.glyphs.index(left.name)
                            for record in subtable.PairSet[covered_index].PairValueRecord:
                                if record.SecondGlyph == right.name:
                                    pair = record
                                    break
                        elif subtable.Format == 2:
                            class1 = subtable.ClassDef1.classDefs.get(left.name, 0)
                            class2 = subtable.ClassDef2.classDefs.get(right.name, 0)
                            pair = subtable.Class1Record[class1].Class2Record[class2]
                        if pair is not None:
                            self.apply_value(result[index], pair.Value1)
                            self.apply_value(result[index + 1], pair.Value2)
                            break
            elif "kern" in self.font:
                for table in self.font["kern"].kernTables:
                    left.advance += table.kernTable.get((left.name, right.name), 0)
        return result

    def path(self, glyph_name: str) -> str:
        if glyph_name not in self.paths:
            pen = SVGPathPen(self.glyphs)
            self.glyphs[glyph_name].draw(pen)
            self.paths[glyph_name] = pen.getCommands()
        return self.paths[glyph_name]

    def bounds(self, glyph_name: str, transform: tuple[float, ...]):
        pen = BoundsPen(self.glyphs)
        self.glyphs[glyph_name].draw(TransformPen(pen, transform))
        return pen.bounds


def bezier(points, t: float):
    # De Casteljau handles the optional line, quadratic, and cubic paths.
    work = [(float(x), float(y)) for x, y in points]
    while len(work) > 1:
        work = [(a[0] * (1 - t) + b[0] * t, a[1] * (1 - t) + b[1] * t)
                for a, b in zip(work, work[1:])]
    return work[0]


class Baseline:
    def __init__(self, points):
        if len(points) not in (2, 3, 4):
            raise ValueError("A baseline requires 2, 3, or 4 Bezier control points")
        self.points = points
        self.samples = 4096
        self.lengths = [0.0]
        last = bezier(points, 0)
        for i in range(1, self.samples + 1):
            current = bezier(points, i / self.samples)
            self.lengths.append(self.lengths[-1] + math.hypot(current[0] - last[0], current[1] - last[1]))
            last = current
        self.length = self.lengths[-1]

    def at(self, distance: float):
        import bisect
        distance = max(0.0, min(self.length, distance))
        i = min(self.samples, max(1, bisect.bisect_left(self.lengths, distance)))
        interval = self.lengths[i] - self.lengths[i - 1]
        frac = (distance - self.lengths[i - 1]) / interval if interval else 0
        t = (i - 1 + frac) / self.samples
        position = bezier(self.points, t)
        n = len(self.points) - 1
        derivative_points = [(n * (b[0] - a[0]), n * (b[1] - a[1]))
                             for a, b in zip(self.points, self.points[1:])]
        derivative = bezier(derivative_points, t)
        return position, math.atan2(derivative[1], derivative[0])


def make_baseline(label: dict, text_width: float) -> Baseline:
    if "points" in label:
        return Baseline(label["points"])
    x, y = float(label["x"]), float(label["y"])
    rise = float(label.get("rise", 0))
    angle = math.radians(float(label.get("angle", 0)))
    span = max(text_width, float(label.get("span", text_width)))
    cs, sn = math.cos(angle), math.sin(angle)
    local = [(-span / 2, rise), (0, -rise), (span / 2, rise)]
    return Baseline([(x + px * cs - py * sn, y + px * sn + py * cs) for px, py in local])


def render_svg(layout: dict, path: Path):
    width, height = int(layout["width"]), int(layout["height"])
    font_path = resolve_repo_path(layout["font"])
    face = OutlinedFont(font_path)
    colour = layout.get("color", "#B31532")
    # Validate the colour before performing a potentially expensive render.
    ImageColor.getrgb(colour)
    root = ET.Element(tag("svg"), {
        "width": str(width), "height": str(height), "viewBox": f"0 0 {width} {height}",
        "version": "1.1", "fill": colour,
    })
    ET.SubElement(root, tag("title")).text = "Catworld crimson cartographic lettering"
    ET.SubElement(root, tag("desc")).text = (
        f"Transparent registered label layer. {width} by {height} pixels at {layout.get('dpi', 600)} DPI. "
        f"Glyph outlines from {layout['font']}; rigid glyphs follow curved baselines."
    )
    metadata = ET.SubElement(root, tag("metadata"))
    metadata.text = json.dumps({"font": layout["font"], "font_sha256": hashlib.sha256(font_path.read_bytes()).hexdigest(),
                                "layout_sha256": hashlib.sha256(json.dumps(layout, sort_keys=True).encode()).hexdigest()}, sort_keys=True)
    reports = []
    ids = set()
    for label in layout["labels"]:
        label_id = str(label["id"])
        if label_id in ids:
            raise ValueError(f"Duplicate label ID: {label_id}")
        ids.add(label_id)
        shaped = face.shape(label["text"])
        scale = float(label["size"]) / face.units
        tracking = float(label.get("tracking", 0))
        advances = [glyph.advance * scale for glyph in shaped]
        text_width = sum(advances) + tracking * max(0, len(shaped) - 1)
        if text_width <= 0:
            raise ValueError(f"Empty or zero-width label: {label_id}")
        curve = make_baseline(label, text_width)
        if curve.length + 0.01 < text_width:
            raise ValueError(f"Path for {label_id} ({curve.length:.1f}px) is shorter than the text ({text_width:.1f}px)")
        group = ET.SubElement(root, tag("g"), {"id": f"label-{label_id}", "aria-label": label["text"]})
        ET.SubElement(group, tag("title")).text = label["text"]
        cursor = (curve.length - text_width) / 2
        bounds = []
        glyphs = []
        for glyph, advance in zip(shaped, advances):
            point, theta = curve.at(cursor + advance / 2)
            cs, sn = math.cos(theta), math.sin(theta)
            x_local = glyph.x_offset * scale - advance / 2
            y_local = -glyph.y_offset * scale
            transform = (scale * cs, scale * sn, scale * sn, -scale * cs,
                         point[0] + cs * x_local - sn * y_local,
                         point[1] + sn * x_local + cs * y_local)
            outline = face.path(glyph.name)
            if outline:
                ET.SubElement(group, tag("path"), {"d": outline, "transform": "matrix(" + " ".join(num(v) for v in transform) + ")"})
                glyph_bound = face.bounds(glyph.name, transform)
                if glyph_bound:
                    bounds.append(glyph_bound)
                    glyphs.append({"glyph": glyph.name, "bounds": [round(v, 3) for v in glyph_bound]})
            cursor += advance + tracking
        if not bounds:
            raise ValueError(f"Label has no visible glyphs: {label_id}")
        box = [min(b[0] for b in bounds), min(b[1] for b in bounds), max(b[2] for b in bounds), max(b[3] for b in bounds)]
        margin = min(box[0], box[1], width - box[2], height - box[3])
        if margin < 0:
            raise ValueError(f"Label {label_id} is clipped by {-margin:.2f} pixels; bounds={box}")
        reports.append({"id": label_id, "text": label["text"], "kind": label.get("kind", ""),
                        "bounds": [round(v, 3) for v in box], "margin": round(margin, 3),
                        "baseline_length": round(curve.length, 3), "text_width": round(text_width, 3),
                        "glyphs": glyphs})
    ET.indent(root, space="  ")
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    return {"width": width, "height": height, "dpi": layout.get("dpi", 600),
            "color": colour, "font": layout["font"], "label_count": len(reports),
            "minimum_margin": min(r["margin"] for r in reports), "labels": reports}


def png_metadata(description: str) -> PngImagePlugin.PngInfo:
    info = PngImagePlugin.PngInfo()
    info.add_text("Description", description)
    info.add_text("Software", "Catworld outlined cartographic lettering renderer")
    info.add(b"sRGB", b"\x00")
    return info


def render_png(svg: Path, layout: dict, output: Path, base_path: Path | None, preview_width: int | None):
    inkscape = shutil.which("inkscape")
    if not inkscape:
        raise RuntimeError("Install Inkscape and ensure its 'inkscape' executable is on PATH")
    full_width, full_height = int(layout["width"]), int(layout["height"])
    ratio = min(1, preview_width / full_width) if preview_width else 1
    width, height = round(full_width * ratio), round(full_height * ratio)
    dpi = float(layout.get("dpi", 600)) * ratio
    reference_opacity = float(layout.get("reference_opacity", 1))
    reference_halo_px = float(layout.get("reference_halo_px", 0))
    if not 0 <= reference_opacity <= 1:
        raise ValueError("reference_opacity must be between 0 and 1")
    if reference_halo_px < 0:
        raise ValueError("reference_halo_px must be nonnegative")
    suffix = "preview" if preview_width else f"{layout.get('dpi', 600)}dpi"
    labels_path = output / f"Catworld-Crimson-Labels-{suffix}.png"
    reference_path = output / f"Catworld-Full-Reference-{suffix}.png"
    with tempfile.TemporaryDirectory(prefix="catworld-labels-") as temp:
        temp_png = Path(temp) / "labels.png"
        command = [inkscape, str(svg), "--export-type=png", "--export-area-page",
                   "--export-background-opacity=0", f"--export-width={width}", f"--export-height={height}",
                   f"--export-filename={temp_png}"]
        result = subprocess.run(command, text=True, capture_output=True)
        if result.returncode:
            raise RuntimeError(f"Inkscape failed: {result.stderr.strip()}")
        with Image.open(temp_png) as raster:
            alpha = raster.convert("RGBA").getchannel("A")
        rgb = ImageColor.getrgb(layout.get("color", "#B31532"))
        labels = Image.new("RGBA", (width, height), (*rgb, 0))
        labels.putalpha(alpha)
        # White hidden RGB keeps alpha-ignoring thumbnailers from displaying a
        # solid crimson rectangle. Every visible pixel remains exact crimson.
        labels.paste((255, 255, 255, 0), mask=alpha.point(lambda value: 255 if value == 0 else 0))
        description = f"Catworld labels only; {len(layout['labels'])} names; transparent background; {full_width}x{full_height} master canvas."
        labels.save(labels_path, dpi=(dpi, dpi), pnginfo=png_metadata(description), optimize=True)
        paths = [labels_path]
        if base_path:
            with Image.open(base_path) as source:
                if source.size != (full_width, full_height):
                    raise ValueError(f"Base is {source.size}; exact registration requires {(full_width, full_height)}")
                base = source.convert("RGBA")
            if ratio != 1:
                base = base.resize((width, height), Image.Resampling.LANCZOS)
            if reference_opacity != 1:
                # Only the reference artwork fades; label coverage stays exact.
                base.putalpha(base.getchannel("A").point(lambda a: round(a * reference_opacity)))
            composite = Image.new("RGBA", (width, height), "white")
            composite.alpha_composite(base)
            halo_radius = round(reference_halo_px * ratio)
            if halo_radius:
                halo = Image.new("RGBA", (width, height), "white")
                halo.putalpha(labels.getchannel("A").filter(ImageFilter.MaxFilter(2 * halo_radius + 1)))
                composite.alpha_composite(halo)
            composite.alpha_composite(labels)
            reference_description = (
                f"Catworld tracing underlay at {reference_opacity:g} artwork opacity with registered crimson lettering. "
                if reference_opacity != 1 else "Catworld reference base with registered crimson lettering. "
            )
            if reference_halo_px:
                reference_description += f"Reference-only white lettering halo: {reference_halo_px:g} master pixels. "
            composite.convert("RGB").save(reference_path, dpi=(dpi, dpi),
                                          pnginfo=png_metadata(reference_description +
                                              f"{len(layout['labels'])} names; {full_width}x{full_height} master canvas; white background."),
                                          optimize=True)
            paths.append(reference_path)
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--layout", type=Path, default=Path(__file__).with_name("labels.json"))
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--base", type=Path, help="Override layout base with an exact-size PNG (repo-relative or absolute)")
    parser.add_argument("--preview", type=int, nargs="?", const=1700, metavar="WIDTH", help="Render smaller preview PNGs, retaining full-resolution SVG geometry")
    parser.add_argument("--svg-only", action="store_true", help="Write outlined SVG and geometry report without rasterizing")
    args = parser.parse_args()
    layout = json.loads(args.layout.read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)
    svg_path = args.output / "Catworld-Crimson-Labels.svg"
    report = render_svg(layout, svg_path)
    report_path = args.output / "Label-Geometry.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    paths = [svg_path, report_path]
    if not args.svg_only:
        base_value = args.base or layout.get("base")
        base = resolve_repo_path(base_value) if base_value else None
        paths.extend(render_png(svg_path, layout, args.output, base, args.preview))
    print(json.dumps({"labels": report["label_count"], "minimum_margin": report["minimum_margin"],
                      "outputs": [str(path) for path in paths]}, indent=2))


if __name__ == "__main__":
    main()
