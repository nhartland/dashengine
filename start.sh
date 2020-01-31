#!/bin/sh

WORKDIR=/app
DEMODIR=/app/demo

# Check for configuration file, if it doesn't exist, use the demo
if [ ! -f $WORKDIR/config.yaml ]; then
  echo "No configuration file found, using demo configuration"
  ln -s $DEMODIR/config.yaml $WORKDIR/config.yaml
fi

# Check for queries folder, if it doesn't exist, use the demo
if [ ! -d $WORKDIR/queries ]; then
  echo "No queries directory found, using demo queries"
  ln -s $DEMODIR/queries $WORKDIR/queries
fi

# Check for pages folder, if it doesn't exist, use the demo
if [ ! -d $WORKDIR/pages ]; then
  echo "No pages directory found, using demo pages"
  ln -s $DEMODIR/pages $WORKDIR/pages
fi

exec gunicorn --worker-tmp-dir=/dev/shm --workers=2 --threads=4 --worker-class=gthread main:app

