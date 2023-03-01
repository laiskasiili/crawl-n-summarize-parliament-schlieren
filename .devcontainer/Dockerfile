FROM python:3.9.16-bullseye

# Install poetry
# https://stackoverflow.com/questions/72465421/how-to-use-poetry-with-docker
# ##############
ENV POETRY_VERSION=1.2.0
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache
# Install poetry separated from system interpreter
RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}
# Add `poetry` to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

# Install firefox and geckodriver for selenium
#######################
RUN apt-get update && apt-get install -y firefox-esr
RUN wget -c https://github.com/mozilla/geckodriver/releases/download/v0.32.2/geckodriver-v0.32.2-linux-aarch64.tar.gz -O - | tar xz -C /usr/local/bin/

CMD ["bash"]
