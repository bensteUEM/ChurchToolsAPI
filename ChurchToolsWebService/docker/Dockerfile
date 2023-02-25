FROM python:3.10

WORKDIR /app

COPY docker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir git+https://github.com/bensteUEM/ChurchToolsAPI.git@v1.2.1.1#egg=ChurchToolsAPI

CMD [ "python", "-m", "ChurchToolsWebService"]

EXPOSE 5000