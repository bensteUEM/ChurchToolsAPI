FROM python:3.10

WORKDIR /app

RUN pip install --upgrade pip

COPY docker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ARG VERSION
RUN echo "Version ${VERSION} of ChurchToolsAPI will be used"
ENV URL="git+https://github.com/bensteUEM/ChurchToolsAPI.git@"$VERSION"#egg=ChurchToolsAPI"
RUN echo "Trying to install package from $URL"
RUN pip install --no-cache-dir $URL

# Unset the environment variables
ENV URL=
RUN unset URL

CMD [ "python", "-m", "ChurchToolsWebService"]

EXPOSE 5000