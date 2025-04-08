from cmaketracing import main
import json
import os
import shutil
import sys

if __name__ == "__main__":
    index = sys.argv[1]

    with open(index) as f:
        data = json.load(f)
        buildDir = data["buildDir"]
        dataDir = data["dataDir"]

    indexName = os.path.basename(index).split(".")[0]

    outputDir = os.path.join(buildDir, "instrumentation")
    indexDir = os.path.join(outputDir, indexName)
    for d in [outputDir, indexDir]:
        if not os.path.exists(d):
            os.makedirs(d)

    for snippet in data["snippets"]:
        shutil.copyfile(
            os.path.join(dataDir, snippet),
            os.path.join(indexDir, snippet)
        )
    shutil.copyfile(
        index,
        os.path.join(indexDir, os.path.basename(index))
    )

    main(index, os.path.join(indexDir, "trace.json"))
