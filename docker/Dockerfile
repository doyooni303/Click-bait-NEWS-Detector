FROM doyoondavidkim/chromeextension:241216

# default
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y vim \
    && apt-get install -y git \
    && apt-get install -y g++ && apt-get install -y curl

# install basic libraries via requirements.txt
RUN pip install --upgrade pip
COPY ../requirements.txt ./
RUN pip install -r requirements.txt

# fonts
RUN apt-get install -y fonts-nanum
RUN rm -rf ~/.cache/matplotlib/*