FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir /fragments

# Run the ldes crawler/static conversion when the container launches.
CMD [ "python3", "./run-ldes-static-conversion.py" ]
