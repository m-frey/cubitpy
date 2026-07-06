# The MIT License (MIT)
#
# Copyright (c) 2018-2026 CubitPy Authors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""Render exported Cubit hex meshes with matplotlib."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from cubitpy.exodus_utility import convert_exodus_to_dict

_HEX8_FACES = np.array(
    [
        [0, 1, 5, 4],
        [1, 2, 6, 5],
        [2, 3, 7, 6],
        [3, 0, 4, 7],
        [0, 3, 2, 1],
        [4, 5, 6, 7],
    ]
)


def _get_shaded_exterior_faces(
    coords: np.ndarray,
    connectivity: list,
    color: str,
    light_dir: tuple[float, float, float],
) -> tuple[np.ndarray, np.ndarray]:
    """Return exterior HEX8 faces and RGBA face colors."""
    from matplotlib.colors import to_rgb

    hexes = np.asarray(connectivity, dtype=np.int64) - 1
    faces = hexes[:, _HEX8_FACES].reshape(-1, 4)
    _, index, counts = np.unique(
        np.sort(faces, axis=1), axis=0, return_index=True, return_counts=True
    )
    quads = coords[faces[index[counts == 1]]]

    normals = np.cross(quads[:, 1] - quads[:, 0], quads[:, 2] - quads[:, 0])
    lengths = np.linalg.norm(normals, axis=1, keepdims=True)
    normals = np.divide(normals, lengths, out=np.zeros_like(normals), where=lengths > 0)
    light = np.asarray(light_dir, dtype=float)
    light /= np.linalg.norm(light)
    shade = (0.35 + 0.65 * np.abs(normals @ light))[:, None]
    rgb = np.clip(np.asarray(to_rgb(color))[None, :] * shade, 0.0, 1.0)
    facecolors = np.concatenate([rgb, np.ones((len(rgb), 1))], axis=1)
    return quads, facecolors


def render_mesh_screenshot(
    exo_path: Path | str,
    png_path: Path | str,
    *,
    skip_blocks: tuple[str | None, ...] = (),
    elev: float = 26.0,
    azim: float = 35.0,
    color: str = "#4C72B0",
    edges: bool = True,
    dpi: int = 170,
    title: str | None = None,
) -> Path:
    """Render the hex mesh of an Exodus file to ``png_path``.

    Args:
        exo_path: Exodus mesh exported from Cubit.
        png_path: Destination PNG file.
        skip_blocks: Exodus block names to ignore.
        elev, azim: View angles in degrees.
        color: Base surface color.
        edges: Draw element edges.
        dpi: Output resolution.
        title: Optional figure title.

    Returns:
        The written ``png_path``.
    """
    try:
        import matplotlib
    except ModuleNotFoundError as err:  # pragma: no cover
        raise ModuleNotFoundError(
            "render_mesh_screenshot needs matplotlib (pip install matplotlib)."
        ) from err

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    data = convert_exodus_to_dict(Path(exo_path))
    coords = np.asarray(data["coordinates"], dtype=float)
    face_blocks = [
        _get_shaded_exterior_faces(coords, connectivity, color, (0.3, 0.35, 0.9))
        for exo_id, meta in data["exo_block_id_to_info"].items()
        if meta["name"] not in skip_blocks
        and (connectivity := data[f"connect{exo_id + 1}"])
        and len(connectivity[0]) == 8
    ]
    if not face_blocks:
        raise ValueError("No 8-node hex blocks to render (check skip_blocks).")
    quads = np.concatenate([block[0] for block in face_blocks])
    facecolors = np.concatenate([block[1] for block in face_blocks])

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(projection="3d")
    ax.set_axis_off()
    if title:
        ax.set_title(title, fontsize=9)
    ax.add_collection3d(
        Poly3DCollection(
            quads,
            facecolors=facecolors,
            edgecolors="0.15" if edges else "none",
            linewidths=0.15 if edges else 0.0,
        )
    )

    points = quads.reshape(-1, 3)
    lo, hi = points.min(axis=0), points.max(axis=0)
    span = float((hi - lo).max()) or 1.0
    mid = 0.5 * (lo + hi)
    for setter, center in zip((ax.set_xlim, ax.set_ylim, ax.set_zlim), mid):
        setter(center - 0.5 * span, center + 0.5 * span)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)

    png_path = Path(png_path)
    png_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(pad=0.1)
    fig.savefig(png_path, dpi=dpi)
    plt.close(fig)
    return png_path
