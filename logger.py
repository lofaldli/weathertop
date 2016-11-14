import argparse
import json
import requests
import subprocess
import logging
logging.basicConfig(filename='logger.log',
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)

HOST = 'localhost'
PORT = 5000
CMD = 'rtl_433 -G -F json'


def start_process(cmd):
    return subprocess.Popen(cmd.split(),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)


def read_stderr(p):
    return p.stderr.readline().strip()


def read_stdout(p):
    return p.stdout.readline().strip()


def parse_entry(text):
    try:
        entry = json.loads(text)
        return entry
    except:
        return None


def check_entry(entry):
    '''
    don't trust those scrubs with low battery
    '''
    if not entry:
        return False
    if 'battery' not in entry or entry['battery'] != 'OK':
        return False
    if 'temperature_C' not in entry:
        return False
    return True


def post_data(temperature):
    url = 'http://%s:%d/add' % (HOST, PORT)
    data = {'temperature': temperature}
    try:
        requests.post(url, data=data)
    except Exception:
        logging.debug('could not connect to %s' % url)
        pass


def main(args, N=10):
    if args.num_entries:
        N = args.num_entries

    p = start_process(CMD)

    while True:
        err = read_stderr(p)
        if err == '':
            break
        elif err == 'No supported devices found.':
            logging.debug(err)
            p.terminate()
            return

    n = 0
    temp_list = []

    while n < N:
        try:
            text = read_stdout(p)
            entry = parse_entry(text)
            if check_entry(entry):
                temp_list.append(entry['temperature_C'])
                n += 1
        except KeyboardInterrupt:
            break

    p.terminate()
    if n > 0:
        avg = 1.0 * sum(temp_list) / n
        logging.info('collected %d entries with an average of %.2f' % (n, avg))
        post_data(avg)
    else:
        logging.info('no data collected, exiting')


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('-d', '--dummy', type=float,
                   help='send dummy data and exit')
    p.add_argument('-n', '--num-entries', type=int,
                   help='number of entries to sample before sending')
    p.add_argument('-a', '--host', type=str,
                   help='host address of webserver')
    p.add_argument('-p', '--port', type=int,
                   help='port of webserver')
    return p.parse_args()

if __name__ == '__main__':
    args = parse_args()

    if args.host:
        HOST = args.host
    if args.port:
        PORT = args.port

    if args.dummy:
        post_data(args.dummy)
    else:
        main(args)
