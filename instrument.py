from cmaketracing import main
import json
import os
import shutil
import sys

if __name__ == "__main__":
    # The instrumentation feature will pass the path to an index file to our callback
    index = sys.argv[1]

    # Get the buildDir and dataDir from the index file
    with open(index) as f:
        data = json.load(f)
        buildDir = data["buildDir"]
        dataDir = data["dataDir"]

    # Get a unique output directory name based on the index filename
    indexName = os.path.basename(index).split(".")[0]

    # Create an output directory that CMake won't clear, to copy our files into
    outputDir = os.path.join(buildDir, "instrumentation")
    indexDir = os.path.join(outputDir, indexName)
    for d in [outputDir, indexDir]:
        if not os.path.exists(d):
            os.makedirs(d)

    # Copy all the instrumentation data into our output directory
    for snippet in data["snippets"]:
        shutil.copyfile(
            os.path.join(dataDir, snippet),
            os.path.join(indexDir, snippet)
        )
    shutil.copyfile(
        index,
        os.path.join(indexDir, os.path.basename(index))
    )

    # Generate our trace.json file
    main(index, os.path.join(indexDir, "trace.json"))
