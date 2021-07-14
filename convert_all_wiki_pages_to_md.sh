#!/usr/bin/env bash
set -euo pipefail

for f in $(find . -name "*.textile"); do
    # strip extension, append md
    python3 convert_wiki_to_md.py $f
    FILENAME="${f%*.*}.md"
    # Wiki.textile should be replaced with index.md for mkdocs
    FILENAME=$(echo ${FILENAME} | sed -e 's/Wiki.md/index.md/')

    # convert textile to md
    pandoc $f -o $FILENAME
    rm $f
done
