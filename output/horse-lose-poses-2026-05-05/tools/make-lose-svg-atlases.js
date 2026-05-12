const fs = require("fs");
const path = require("path");

const spriteSourcePath = "D:/Work/LAMDiceBot/js/horse-race-sprites.js";
const batchRoot = path.resolve(__dirname, "..");
const outDir = path.join(batchRoot, "generated");
const sourceText = fs.readFileSync(spriteSourcePath, "utf8");

const assets = [
  { id: "car", line: 3, phase: 2, pose: "tilt", effect: "cloud", effectX: 30, effectY: 10 },
  { id: "rocket", line: 49, phase: 2, pose: "tilt", effect: "smoke", effectX: 10, effectY: 24 },
  { id: "bird", line: 91, phase: 2, pose: "tilt", effect: "feather", effectX: 18, effectY: 15 },
  { id: "boat", line: 135, phase: 3, pose: "tilt", effect: "bubbles", effectX: 47, effectY: 27 },
  { id: "bicycle", line: 169, phase: 3, pose: "tilt", effect: "tear", effectX: 40, effectY: 10 },
  { id: "rabbit", line: 217, phase: 1, pose: "kneel", effect: "tear", effectX: 52, effectY: 12 },
  { id: "turtle", line: 275, phase: 1, pose: "kneel", effect: "cloud", effectX: 27, effectY: 12 },
  { id: "eagle", line: 315, phase: 3, pose: "kneel", effect: "cloud", effectX: 23, effectY: 14 },
  { id: "scooter", line: 363, phase: 3, pose: "tilt", effect: "tear", effectX: 41, effectY: 10 },
  { id: "helicopter", line: 405, phase: 3, pose: "tilt", effect: "smoke", effectX: 14, effectY: 19 },
  { id: "horse", line: 463, phase: 1, pose: "kneel", effect: "cloud", effectX: 24, effectY: 13 },
  { id: "knight", line: 886, phase: 1, pose: "kneel", effect: "cloud", effectX: 17, effectY: 10 },
  { id: "dinosaur", line: 1267, phase: 1, pose: "kneel", effect: "cloud", effectX: 25, effectY: 10 },
  { id: "ninja", line: 1677, phase: 2, pose: "kneel", effect: "tear", effectX: 45, effectY: 10 },
  { id: "crab", line: 2027, phase: 3, pose: "kneel", effect: "bubbles", effectX: 43, effectY: 15 }
];

function escapeXml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function lineOffset(text, line) {
  let offset = 0;
  for (let current = 1; current < line; current += 1) {
    const next = text.indexOf("\n", offset);
    if (next === -1) return text.length;
    offset = next + 1;
  }
  return offset;
}

function normalizeLineEndings(text) {
  return text.replace(/\r\n/g, "\n").replace(/\r/g, "\n");
}

function svgInfo(svg) {
  const normalized = normalizeLineEndings(svg.trim());
  const openEnd = normalized.indexOf(">");
  const closeStart = normalized.lastIndexOf("</svg>");
  if (openEnd === -1 || closeStart === -1) {
    throw new Error("Invalid SVG markup");
  }
  const openTag = normalized.slice(0, openEnd + 1);
  const body = normalized.slice(openEnd + 1, closeStart).trim();
  const viewBoxMatch = openTag.match(/viewBox\s*=\s*"([^"]+)"/i);
  const widthMatch = openTag.match(/width\s*=\s*"([^"]+)"/i);
  const heightMatch = openTag.match(/height\s*=\s*"([^"]+)"/i);
  return {
    body,
    viewBox: viewBoxMatch ? viewBoxMatch[1] : `0 0 ${widthMatch ? widthMatch[1] : 60} ${heightMatch ? heightMatch[1] : 45}`,
    width: widthMatch ? widthMatch[1] : "60",
    height: heightMatch ? heightMatch[1] : "45"
  };
}

function extractFrame(asset, frameName) {
  const start = lineOffset(sourceText, asset.line);
  const slice = sourceText.slice(start, start + 130000);
  const runIndex = slice.search(/\brun\s*:\s*\{/);
  if (runIndex < 0) {
    throw new Error(`${asset.id}: run state not found near line ${asset.line}`);
  }
  const runSlice = slice.slice(runIndex, runIndex + 70000);
  const regex = new RegExp(`${frameName}\\s*:\\s*\`([\\s\\S]*?<\\/svg>)\``);
  const match = runSlice.match(regex);
  if (!match) {
    throw new Error(`${asset.id}: ${frameName} SVG not found in run state near line ${asset.line}`);
  }
  return svgInfo(match[1]);
}

function shape(name, attrs, body = "") {
  const text = Object.entries(attrs)
    .filter(([, value]) => value !== undefined && value !== null && value !== "")
    .map(([key, value]) => `${key}="${escapeXml(value)}"`)
    .join(" ");
  return body ? `<${name} ${text}>${body}</${name}>` : `<${name} ${text}/>`;
}

function circle(cx, cy, r, fill, stroke = "#24324a") {
  return shape("circle", { cx, cy, r, fill, stroke, "stroke-width": 1.1 });
}

function pathShape(d, fill, attrs = {}) {
  return shape("path", {
    d,
    fill,
    stroke: attrs.stroke || "#24324a",
    "stroke-width": attrs["stroke-width"] || 1.2,
    "stroke-linecap": attrs["stroke-linecap"] || "round",
    "stroke-linejoin": attrs["stroke-linejoin"] || "round",
    ...attrs
  });
}

function effect(asset, frameIndex) {
  const dy = frameIndex ? -1 : 0;
  const x = asset.effectX;
  const y = asset.effectY;
  if (asset.effect === "tear") {
    return [
      pathShape(`M${x},${y + dy} L${x + 3},${y + 4 + dy} L${x},${y + 8 + dy} L${x - 3},${y + 4 + dy} Z`, "#69bdf5", {
        stroke: "#1f5f92",
        "stroke-width": 0.9
      })
    ].join("");
  }
  if (asset.effect === "bubbles") {
    return [
      circle(x, y + dy, 1.7, "none", "#b9ecff"),
      circle(x + 5, y - 2 + dy, 1.3, "none", "#b9ecff"),
      circle(x + 8, y + 1 + dy, 1.8, "none", "#b9ecff")
    ].join("");
  }
  if (asset.effect === "smoke") {
    return [
      circle(x, y + dy, 2, "#8d939a", "#4e565e"),
      circle(x + 4, y - 1 + dy, 2.2, "#a5abb1", "#4e565e"),
      circle(x + 8, y + 1 + dy, 1.7, "#747b83", "#4e565e")
    ].join("");
  }
  if (asset.effect === "feather") {
    return pathShape(`M${x},${y + dy} Q${x + 5},${y + 4 + dy} ${x + 2},${y + 10 + dy} Q${x - 2},${y + 5 + dy} ${x},${y + dy} Z`, "#9fd0f0", {
      stroke: "#3d6f8c",
      "stroke-width": 0.9
    });
  }
  return [
    circle(x, y + dy, 2, "#c5c9cc", "#6c737a"),
    circle(x + 3, y - 1 + dy, 2.4, "#d6dadd", "#6c737a"),
    circle(x + 6, y + dy, 2, "#c5c9cc", "#6c737a")
  ].join("");
}

function sadEyeOverlay(asset, frameIndex) {
  const yShift = frameIndex ? 1 : 0;
  const coords = {
    horse: [47, 15],
    rabbit: [47, 19],
    turtle: [47, 24],
    dinosaur: [47, 18],
    knight: [30, 16],
    ninja: [29, 16],
    crab: [24, 17],
    eagle: [50, 20],
    bird: [50, 21],
    bicycle: [30, 13],
    scooter: [28, 13]
  };
  const point = coords[asset.id];
  if (!point) return "";
  const [x, y] = point;
  return [
    shape("rect", { x: x - 2, y: y + yShift, width: 3, height: 1.4, fill: "#24324a" }),
    shape("rect", { x: x + 3, y: y + yShift, width: 3, height: 1.4, fill: "#24324a" }),
    shape("rect", { x: x - 1, y: y + 1 + yShift, width: 1.2, height: 2.4, fill: "#24324a" }),
    shape("rect", { x: x + 4, y: y + 1 + yShift, width: 1.2, height: 2.4, fill: "#24324a" })
  ].join("");
}

function poseTransform(asset, frameIndex) {
  if (asset.pose === "tilt") {
    const degree = frameIndex ? 8 : 5;
    const down = frameIndex ? 1 : 0;
    return `translate(0 ${down}) rotate(${degree} 30 39)`;
  }
  const scale = frameIndex ? 0.91 : 0.94;
  const down = frameIndex ? 2 : 1;
  return `translate(0 ${down}) translate(0 45) scale(1 ${scale}) translate(0 -45)`;
}

function frameGroup(asset, frameSvg, frameIndex) {
  const x = frameIndex * 60;
  return [
    `<g clip-path="url(#clip-${frameIndex})">`,
    `  <g transform="translate(${x} 0)">`,
    `    <g filter="url(#muted)" transform="${poseTransform(asset, frameIndex)}">`,
    `      <svg x="0" y="0" width="60" height="45" viewBox="${escapeXml(frameSvg.viewBox)}" preserveAspectRatio="xMidYMax meet">`,
    frameSvg.body,
    "      </svg>",
    "    </g>",
    sadEyeOverlay(asset, frameIndex),
    effect(asset, frameIndex),
    "  </g>",
    "</g>"
  ].join("\n");
}

function atlas(asset) {
  const frame1 = extractFrame(asset, "frame1");
  const frame2 = extractFrame(asset, "frame2");
  return [
    `<?xml version="1.0" encoding="UTF-8"?>`,
    `<svg xmlns="http://www.w3.org/2000/svg" width="120" height="45" viewBox="0 0 120 45" shape-rendering="crispEdges">`,
    `<title>${asset.id}-lose</title>`,
    `<desc>Derived from the base svgMap vehicle in ${spriteSourcePath} ${asset.id} run.frame1 near line ${asset.line}; strict 2x1 lose atlas, 60x45 cells. Not derived from POWER_VEHICLE_VARIANT_OVERRIDES.</desc>`,
    "<defs>",
    '  <clipPath id="clip-0"><rect x="0" y="0" width="60" height="45"/></clipPath>',
    '  <clipPath id="clip-1"><rect x="60" y="0" width="60" height="45"/></clipPath>',
    '  <filter id="muted" color-interpolation-filters="sRGB">',
    '    <feColorMatrix type="saturate" values="0.78"/>',
    "  </filter>",
    "</defs>",
    "<!-- strict atlas: 2 columns x 1 row, 60x45 cells, no gutters -->",
    frameGroup(asset, frame1, 0),
    frameGroup(asset, frame2, 1),
    "</svg>"
  ].join("\n");
}

fs.mkdirSync(outDir, { recursive: true });

for (const asset of assets) {
  const outputPath = path.join(outDir, `${asset.id}-lose.svg`);
  fs.writeFileSync(outputPath, atlas(asset), "utf8");
  console.log(`${asset.id}: source line ${asset.line} -> ${path.relative(batchRoot, outputPath)}`);
}
