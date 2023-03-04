FROM python:3.10

WORKDIR /app

ARG VERSION
RUN echo "Version number from build arg is: ${VERSION}"

ENV URL="git+https://github.com/bensteUEM/ChurchToolsAPI.git@"$VERSION"#egg=ChurchToolsAPI"
RUN echo "url is $URL"


RUN pip install --upgrade pip

COPY docker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


RUN pip install --no-cache-dir $URL

CMD [ "python", "-m", "ChurchToolsWebService"]

EXPOSE 5000