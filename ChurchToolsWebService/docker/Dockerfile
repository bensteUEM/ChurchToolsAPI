FROM python:3.10
ENV VERSION=$('python -c "from versions import VERSION; print(VERSION)"')
ENV URL="git+https://github.com/bensteUEM/ChurchToolsAPI.git@v"$VERSION"#egg=ChurchToolsAPI"

WORKDIR /app

RUN pip install --upgrade pip

COPY docker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir $URL

CMD [ "python", "-m", "ChurchToolsWebService"]

EXPOSE 5000