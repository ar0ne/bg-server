FROM python:3.11
MAINTAINER Sergey S

RUN pip install --upgrade pip

RUN useradd -ms /bin/bash bguser
USER bguser
WORKDIR /home/bguser

COPY --chown=bguser:bguser requirements.txt requirements.txt

ENV PATH="/home/bguser/.local/bin:${PATH}"

RUN pip install --user -r requirements.txt

COPY --chown=bguser:bguser . .

EXPOSE 8888

# ENTRYPOINT ["python", "main.py"]

ENTRYPOINT ["sh", "start.sh"]
