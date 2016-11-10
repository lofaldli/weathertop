# weathertop

this is a temperature monitor meant to be used with an [rtl-sdr][1] (or similar) dongle and to pick up messages from nearby sensors using the 433 MHz ISM-band

it features `logger.py` which reads data from the rtl-sdr and post them to the flask webserver in `server` which also generates plots in the webbrowser

## setup

1. install requirements

        pip install -r requirements.txt

2. install [rtl-sdr][2] and [rtl_433][3] 

2. setup `logger.py` as crontab

        crontab -e

    add this line to run the logger every 30 minutes

        */30 * * * * /path/to/logger.py

## running the webserver

        export FLASK_APP=server/server.py
        flask run --host=0.0.0.0

this makes the webserver publicly available on port 5000

[1]: http://sdr.osmocom.org/trac/wiki/rtl-sdr
[2]: https://github.com/steve-m/librtlsdr
[3]: https://github.com/merbanan/rtl_433
