#!/bin/bash
docker build --no-cache --build-arg \
VERSION="$(python3 -c "import versions; print(versions.VERSION)")" \
-f docker/Dockerfile -t churchtools_web_service_docker . \
&& docker run -p 5000:5000 --env CT_DOMAIN=https://elkw1610.krz.tools\
 --name ChurchToolsAPI churchtools_web_service_docker