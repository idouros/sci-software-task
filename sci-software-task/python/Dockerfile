 FROM python:3.8-slim

RUN apt-get update && \
    apt-get install -y gcc g++ gdal-bin libgdal-dev

WORKDIR /opt/

COPY requirements.txt .
RUN PIP_NO_BINARY=rasterio pip install -r requirements.txt  # no binary for rasterio means we can use the GDAL binaries above

COPY . .

ENTRYPOINT [ "python", "sci_software_task/main.py" ]
