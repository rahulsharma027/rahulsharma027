"""Build the local technology-logo strip. --fetch downloads its source icons."""

from __future__ import annotations

import argparse
from copy import deepcopy
from html import escape
from pathlib import Path
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
LOGOS = ROOT / "assets" / "logos"
SIMPLE = "https://cdn.jsdelivr.net/npm/simple-icons@16.0.0/icons/"
DEVICON = "https://raw.githubusercontent.com/devicons/devicon/v2.17.0/icons/"
ICONS = [
    ("go", "GO", SIMPLE + "go.svg"),
    ("java", "JAVA", DEVICON + "java/java-original.svg"),
    ("python", "PYTHON", SIMPLE + "python.svg"),
    ("spring", "SPRING BOOT", SIMPLE + "spring.svg"),
    ("kubernetes", "KUBERNETES", SIMPLE + "kubernetes.svg"),
    ("docker", "DOCKER", SIMPLE + "docker.svg"),
    ("aws", "AWS", DEVICON + "amazonwebservices/amazonwebservices-original-wordmark.svg"),
    ("jenkins", "JENKINS", SIMPLE + "jenkins.svg"),
    ("graphql", "GRAPHQL", SIMPLE + "graphql.svg"),
    ("grafana", "GRAFANA", SIMPLE + "grafana.svg"),
    ("react", "REACT", SIMPLE + "react.svg"),
    ("linux", "LINUX", SIMPLE + "linux.svg"),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true")
    args = parser.parse_args()
    LOGOS.mkdir(parents=True, exist_ok=True)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="260" viewBox="0 0 1000 260" role="img" aria-labelledby="title description">',
        '<title id="title">Rahul Sharma technology loadout</title>',
        '<desc id="description">Go, Java, Python, Spring Boot, Kubernetes, Docker, AWS, Jenkins, GraphQL, Grafana, React, and Linux.</desc>',
        '<rect x="1" y="1" width="998" height="258" rx="12" fill="#0d1117" stroke="#30363d"/>',
        '<text x="32" y="38" fill="#58a6ff" font-family="Consolas, Liberation Mono, monospace" font-size="13" letter-spacing="2">TECH / EQUIPPED</text>',
    ]
    for index, (slug, label, source) in enumerate(ICONS):
        target = LOGOS / f"{slug}.svg"
        if args.fetch:
            request = Request(source, headers={"User-Agent": "rahulsharma027-profile-assets"})
            with urlopen(request, timeout=30) as response:
                content = response.read()
            ET.fromstring(content)
            target.write_bytes(content)
        original = ET.parse(target).getroot()
        if any(element.tag.split('}')[-1] in ("script", "foreignObject", "image") for element in original.iter()):
            raise ValueError(f"Unexpected non-vector content in {target.name}")
        col, row = index % 6, index // 6
        center, y = 112 + col * 155, 66 + row * 91
        nested = ET.Element("svg", {"x": str(center - 20), "y": str(y), "width": "40", "height": "40", "viewBox": original.get("viewBox", "0 0 24 24"), "fill": "#c9d1d9"})
        for child in original:
            if child.tag.split('}')[-1] not in ("title", "desc", "metadata"):
                nested.append(deepcopy(child))
        # Use the light wordmark lettering for AWS against the dark strip.
        for element in nested.iter():
            if element.get("fill", "").lower() == "#252f3e":
                element.set("fill", "#e6edf3")
        parts.append(ET.tostring(nested, encoding="unicode"))
        parts.append(f'<text x="{center}" y="{y + 63}" text-anchor="middle" fill="#8b949e" font-size="12" font-family="Consolas, Liberation Mono, monospace">{escape(label)}</text>')
    parts.append("</svg>\n")
    output = "".join(parts)
    ET.fromstring(output)
    (ROOT / "assets" / "tech-loadout.svg").write_text(output, encoding="utf-8", newline="\n")
    mobile = ET.fromstring(output)
    mobile.set("width", "600")
    mobile.set("height", "480")
    mobile.set("viewBox", "0 0 600 480")
    mobile.find("{http://www.w3.org/2000/svg}rect").set("width", "598")
    mobile.find("{http://www.w3.org/2000/svg}rect").set("height", "478")
    title = mobile.find("{http://www.w3.org/2000/svg}text")
    title.set("font-size", "18")
    nested_icons = [element for element in mobile if element.tag.split('}')[-1] == 'svg']
    labels = [element for element in mobile if element.tag.split('}')[-1] == 'text'][1:]
    for index, (icon, label) in enumerate(zip(nested_icons, labels)):
        center, y = 104 + index % 3 * 196, 70 + index // 3 * 98
        icon.set("x", str(center - 22))
        icon.set("y", str(y))
        icon.set("width", "44")
        icon.set("height", "44")
        label.set("x", str(center))
        label.set("y", str(y + 70))
        label.set("font-size", "17")
    (ROOT / "assets" / "tech-loadout-mobile.svg").write_text(ET.tostring(mobile, encoding="unicode") + "\n", encoding="utf-8")
    print("Built desktop and mobile technology strips with 12 locally embedded logos.")


if __name__ == "__main__":
    main()
