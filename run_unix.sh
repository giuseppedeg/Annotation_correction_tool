#!/bin/sh

ABSPATH=$(cd "$(dirname "$0")"; pwd -P)
cd $ABSPATH

open "" "http://localhost:5500"

python3 -m http.server 5500


