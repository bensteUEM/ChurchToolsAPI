#!/bin/bash
#echo $(python3 -c "print('from python')")
export VERSION='TEST FROM SH replace'
#$(python3 -c "import versions; print(versions.VERSION)")

docker build --no-cache --build-arg \
VERSION="$(python3 -c "import versions; print(versions.VERSION)")" \
-f docker/Dockerfile -t churchtools_web_service_docker . \
&& docker run -p 5000:5000 --env domain=https://elkw1610.krz.tools\
 --name ChurchToolsAPI churchtools_web_service_docker