#!/usr/bin/env python3
"""Render registered, curved Catworld lettering from the repository font.

All coordinates and font sizes in the layout are full-resolution canvas pixels.
Each glyph retains its original outline and rotates rigidly along the baseline.
Positive ``rise`` arches a label upward: (x, y) is the baseline's centre and
the two baseline endpoints sit ``rise`` pixels below it. ``angle`` is clockwise.
``points`` optionally supplies 2, 3, or 4 global Bezier control points instead.
``align`` (start, center, end; default center) and ``offset`` (canvas pixels)
position text along that path. Positive offset advances toward the path end.
``require_individual_paths`` requires a distinct cubic and a ``path_rationale``
for every label; geometry is compared independently of position, scale, and angle.
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


def finite_number(value, name: str, *, positive: bool = False) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite number") from exc
    if isinstance(value, bool) or not math.isfinite(result):
        raise ValueError(f"{name} must be a finite number")
    if positive and result <= 0:
        raise ValueError(f"{name} must be positive")
    return result


def canvas_dimensions(layout: dict) -> tuple[int, int]:
    dimensions = [finite_number(layout[key], key, positive=True) for key in ("width", "height")]
    if any(value != int(value) for value in dimensions):
        raise ValueError("Canvas width and height must be positive whole pixels")
    return tuple(int(value) for value in dimensions)


def angle_span(angles) -> float:
    """Range of continuously unwrapped tangent angles, in degrees."""
    unwrapped = []
    previous = None
    for angle in angles:
        if previous is not None:
            angle = previous + math.atan2(math.sin(angle - previous), math.cos(angle - previous))
        unwrapped.append(angle)
        previous = angle
    return math.degrees(max(unwrapped) - min(unwrapped)) if unwrapped else 0.0


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
        if not isinstance(points, (list, tuple)) or len(points) not in (2, 3, 4):
            raise ValueError("A baseline requires 2, 3, or 4 Bezier control points")
        self.points = []
        for i, point in enumerate(points):
            if not isinstance(point, (list, tuple)) or len(point) != 2:
                raise ValueError(f"Baseline point {i} must contain exactly two coordinates")
            self.points.append(tuple(finite_number(value, f"Baseline point {i} coordinate") for value in point))
        points = self.points
        n = len(points) - 1
        self.derivative_points = [(n * (b[0] - a[0]), n * (b[1] - a[1]))
                                  for a, b in zip(points, points[1:])]
        self.samples = 4096
        self.lengths = [0.0]
        last = bezier(points, 0)
        for i in range(1, self.samples + 1):
            current = bezier(points, i / self.samples)
            self.lengths.append(self.lengths[-1] + math.hypot(current[0] - last[0], current[1] - last[1]))
            last = current
        self.length = self.lengths[-1]
        if not math.isfinite(self.length) or self.length <= 0:
            raise ValueError("A baseline must have finite, positive length")
        # Endpoint tangents must be defined; duplicate endpoint handles would
        # otherwise silently become zero-degree rotations through atan2(0, 0).
        self.tangent(0)
        self.tangent(1)

    def tangent(self, t: float) -> float:
        derivative = bezier(self.derivative_points, t)
        if math.hypot(*derivative) <= 1e-10:
            raise ValueError(f"Baseline has an undefined tangent at t={t:.6f}")
        return math.atan2(derivative[1], derivative[0])

    def normalized_points(self) -> list[list[float]]:
        """Translate, rotate, and scale by the endpoint chord; round to 0.001."""
        start, end = self.points[0], self.points[-1]
        dx, dy = end[0] - start[0], end[1] - start[1]
        chord = math.hypot(dx, dy)
        if chord <= 1e-10:
            raise ValueError("Baseline endpoints must be distinct for curve normalization")
        cs, sn = dx / chord, dy / chord
        result = []
        for x, y in self.points:
            x, y = x - start[0], y - start[1]
            result.append([round((x * cs + y * sn) / chord, 3) or 0.0,
                           round((-x * sn + y * cs) / chord, 3) or 0.0])
        return result

    def at(self, distance: float):
        import bisect
        distance = max(0.0, min(self.length, distance))
        i = min(self.samples, max(1, bisect.bisect_left(self.lengths, distance)))
        interval = self.lengths[i] - self.lengths[i - 1]
        frac = (distance - self.lengths[i - 1]) / interval if interval else 0
        t = (i - 1 + frac) / self.samples
        position = bezier(self.points, t)
        return position, self.tangent(t)

    def tangent_variation(self, start: float = 0, end: float | None = None) -> float:
        end = self.length if end is None else end
        return angle_span(self.at(start + (end - start) * i / 256)[1] for i in range(257))


def make_baseline(label: dict, text_width: float) -> Baseline:
    if "points" in label:
        return Baseline(label["points"])
    x, y = finite_number(label["x"], "x"), finite_number(label["y"], "y")
    rise = finite_number(label.get("rise", 0), "rise")
    angle = math.radians(finite_number(label.get("angle", 0), "angle"))
    span = max(text_width, finite_number(label.get("span", text_width), "span", positive=True))
    cs, sn = math.cos(angle), math.sin(angle)
    local = [(-span / 2, rise), (0, -rise), (span / 2, rise)]
    return Baseline([(x + px * cs - py * sn, y + px * sn + py * cs) for px, py in local])


def render_svg(layout: dict, path: Path):
    width, height = canvas_dimensions(layout)
    finite_number(layout.get("dpi", 600), "dpi", positive=True)
    if not isinstance(layout.get("labels"), list) or not layout["labels"]:
        raise ValueError("The layout must contain a nonempty labels list")
    require_individual_paths = layout.get("require_individual_paths", False)
    if not isinstance(require_individual_paths, bool):
        raise ValueError("require_individual_paths must be true or false")
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
    curve_owners = {}
    for label in layout["labels"]:
        label_id = str(label["id"])
        if label_id in ids:
            raise ValueError(f"Duplicate label ID: {label_id}")
        ids.add(label_id)
        if not isinstance(label.get("text"), str) or not label["text"].strip():
            raise ValueError(f"Label {label_id} requires nonempty text")
        if require_individual_paths:
            if not isinstance(label.get("points"), list) or len(label["points"]) != 4:
                raise ValueError(f"Label {label_id} ({label['text']}) requires four explicit cubic control points")
            if not isinstance(label.get("path_rationale"), str) or not label["path_rationale"].strip():
                raise ValueError(f"Label {label_id} ({label['text']}) requires a nonempty path_rationale")
        shaped = face.shape(label["text"])
        scale = finite_number(label["size"], f"Label {label_id} size", positive=True) / face.units
        tracking = finite_number(label.get("tracking", 0), f"Label {label_id} tracking")
        advances = [glyph.advance * scale for glyph in shaped]
        text_width = sum(advances) + tracking * max(0, len(shaped) - 1)
        if not math.isfinite(text_width) or text_width <= 0:
            raise ValueError(f"Empty or zero-width label: {label_id}")
        if any(not math.isfinite(advance) or advance <= 0 for advance in advances):
            raise ValueError(f"Label {label_id} has an invalid glyph advance")
        if any(advance + tracking <= 0 for advance in advances[:-1]):
            raise ValueError(f"Label {label_id} tracking must leave positive glyph progression")
        try:
            curve = make_baseline(label, text_width)
            normalized_points = curve.normalized_points()
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Label {label_id} ({label['text']}): {exc}") from exc
        curve_signature = hashlib.sha256(json.dumps(normalized_points, separators=(",", ":")).encode()).hexdigest()
        if require_individual_paths and curve_signature in curve_owners:
            raise ValueError(f"Label {label_id} ({label['text']}) repeats the normalized curve geometry of "
                             f"label {curve_owners[curve_signature]}; each path must be individually designed")
        curve_owners[curve_signature] = label_id
        if curve.length + 0.01 < text_width:
            raise ValueError(f"Path for label {label_id} ({label['text']}) is {curve.length:.1f}px long; "
                             f"text needs {text_width:.1f}px")
        align = label.get("align", "center")
        if align not in ("start", "center", "end"):
            raise ValueError(f"Label {label_id} align must be start, center, or end")
        offset = finite_number(label.get("offset", 0), f"Label {label_id} offset")
        start = {"start": 0, "center": (curve.length - text_width) / 2,
                 "end": curve.length - text_width}[align] + offset
        end = start + text_width
        if start < -0.01 or end > curve.length + 0.01:
            raise ValueError(f"Label {label_id} ({label['text']}) needs {text_width:.1f}px at "
                             f"[{start:.1f}, {end:.1f}]px, outside its {curve.length:.1f}px path; "
                             "adjust align, offset, or control points")
        group = ET.SubElement(root, tag("g"), {"id": f"label-{label_id}", "aria-label": label["text"]})
        ET.SubElement(group, tag("title")).text = label["text"]
        cursor = start
        bounds = []
        glyphs = []
        glyph_angles = []
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
                    glyph_angles.append(theta)
                    glyphs.append({"glyph": glyph.name, "bounds": [round(v, 3) for v in glyph_bound],
                                   "baseline_angle": round(math.degrees(theta), 3)})
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
                        "baseline_points": [list(point) for point in curve.points],
                        "baseline_angle_at_start": round(math.degrees(curve.at(0)[1]), 3),
                        "baseline_angle_at_end": round(math.degrees(curve.at(curve.length)[1]), 3),
                        "baseline_tangent_variation_degrees": round(curve.tangent_variation(), 3),
                        "text_tangent_variation_degrees": round(curve.tangent_variation(start, end), 3),
                        "glyph_tangent_variation_degrees": round(angle_span(glyph_angles), 3),
                        "normalized_control_points": normalized_points,
                        "curve_signature": curve_signature,
                        "path_rationale": label.get("path_rationale", ""),
                        "align": align, "offset": offset,
                        "text_start_distance": round(start, 3), "text_end_distance": round(end, 3),
                        "glyphs": glyphs})
    ET.indent(root, space="  ")
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    return {"width": width, "height": height, "dpi": layout.get("dpi", 600),
            "color": colour, "font": layout["font"], "label_count": len(reports),
            "require_individual_paths": require_individual_paths,
            "unique_curve_count": len(curve_owners),
            "geometry_units": "canvas pixels; angles in clockwise degrees; tangent variation is unwrapped angular range",
            "curve_normalization": "subtract start, rotate endpoint chord horizontal, divide by chord length, round to 0.001",
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
    full_width, full_height = canvas_dimensions(layout)
    if preview_width is not None:
        finite_number(preview_width, "preview width", positive=True)
    ratio = min(1, preview_width / full_width) if preview_width else 1
    width, height = round(full_width * ratio), round(full_height * ratio)
    if min(width, height) < 1:
        raise ValueError("Preview dimensions must each be at least one pixel")
    dpi = finite_number(layout.get("dpi", 600), "dpi", positive=True) * ratio
    reference_opacity = finite_number(layout.get("reference_opacity", 1), "reference_opacity")
    reference_halo_px = finite_number(layout.get("reference_halo_px", 0), "reference_halo_px")
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
