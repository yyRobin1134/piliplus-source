"""Refresh source.json from the newest lemonteaau/PiliPlus iOS release."""
import json, os, re, urllib.request, pathlib

REPO = "lemonteaau/PiliPlus"
ASSET = "PiliPlus-custom-ios-unsigned.ipa"
path = pathlib.Path(__file__).with_name("source.json")

req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/releases/latest")
if os.environ.get("GITHUB_TOKEN"):
    req.add_header("Authorization", "Bearer " + os.environ["GITHUB_TOKEN"])
with urllib.request.urlopen(req, timeout=30) as r:
    rel = json.load(r)
asset = next(a for a in rel["assets"] if a["name"] == ASSET)

src = json.loads(path.read_text(encoding="utf-8"))
app = src["apps"][0]
version = {
    "version": re.match(r"v?(\d+\.\d+\.\d+)", rel["tag_name"]).group(1),  # must equal the IPA's CFBundleShortVersionString
    "buildVersion": re.search(r"(\d+)$", rel["tag_name"]).group(1),  # must equal the IPA's CFBundleVersion
    "date": rel["published_at"],
    "localizedDescription": f"PiliPlus {rel['tag_name']}",
    "downloadURL": asset["browser_download_url"],
    "size": asset["size"],
    "minOSVersion": "14.0",
}
app["versions"] = [version] + [v for v in app["versions"] if v["buildVersion"] != version["buildVersion"]][:9]
# legacy fields read by older AltStore/SideStore builds
app.update(version=version["version"], versionDate=version["date"], downloadURL=version["downloadURL"],
           size=version["size"], versionDescription=version["localizedDescription"])
path.write_text(json.dumps(src, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("updated to", version["version"], version["size"])
