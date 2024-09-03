import json, shutil, os, sys
from cmtrace import main
index = sys.argv[1]

outputDir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "output"
)
snippetDir = os.path.join(outputDir, "snippets")
if not os.path.exists(outputDir):
    os.makedirs(outputDir)
if not os.path.exists(snippetDir):
    os.makedirs(snippetDir)
dataDir = os.path.dirname(index)

with open(index) as f:
    data = json.load(f)

for snippet in data["snippets"]:
    shutil.copyfile(
        os.path.join(dataDir, snippet),
        os.path.join(snippetDir, snippet)
    )

main(index, os.path.join(outputDir, "trace.json"))
