import json, shutil, os, sys
from cmtrace import main
index = sys.argv[1]

outputDir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "output"
)
snippetDir = os.path.join(outputDir, "snippets")
indexDir = os.path.join(outputDir, "indexes")
for d in [outputDir, snippetDir, indexDir]:
    if not os.path.exists(d):
        os.makedirs(d)
dataDir = os.path.dirname(index)

with open(index) as f:
    data = json.load(f)

for snippet in data["snippets"]:
    shutil.copyfile(
        os.path.join(dataDir, snippet),
        os.path.join(snippetDir, snippet)
    )
shutil.copyfile(
    index,
    os.path.join(indexDir, os.path.basename(index))
)

main(index, os.path.join(outputDir, "trace.json"))
