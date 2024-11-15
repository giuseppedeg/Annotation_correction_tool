#!/bin/sh

ABSPATH=$(cd "$(dirname "$0")"; pwd -P)
cd $ABSPATH

open "" "http://localhost:5500"

python -m http.server 5500

