FROM python:3.11-slim-bullseye
LABEL org.opencontainers.image.authors="gene@kultpower.de"

RUN pip install --upgrade pip
RUN pip3 install Mastodon.py
RUN pip3 install python-dotenv