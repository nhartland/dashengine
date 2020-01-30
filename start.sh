#!/bin/sh

WORKDIR=/app
DEMODIR=/app/demo

# Check for queries folder, if it doesn't exist, use the demo
if [ ! -d $WORKDIR/queries ]; then
  echo "No \`queries\' directory found, using demo queries"
  echo $DEMODIR/queries
  ls $DEMODIR/queries
  cp -r $DEMODIR/queries $WORKDIR/queries
fi

# Check for pages folder, if it doesn't exist, use the demo
if [ ! -d $WORKDIR/pages ]; then
  echo "No \`pages\' directory found, using demo pages"
  cp -r $DEMODIR/pages $WORKDIR/pages.yaml
fi

exec gunicorn --worker-tmp-dir=/dev/shm --workers=2 --threads=4 --worker-class=gthread main:app

