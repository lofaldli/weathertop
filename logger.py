import argparse
import json
import requests
import subprocess

HOST = 'localhost'
PORT = 5000
URL = 'http://%s:%i/add' % (HOST, PORT)
cmd = 'rtl_433 -G -F json'


def parse_entry(text):
    try:
        entry = json.loads(text)
        return entry
    except ValueError, e:
        print e, 'sorry...'
        print text


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
    data = {'temperature': temperature}
    try:
        r = requests.post(URL, data=data)
        print r.status_code
    except Exception, e:
        print e


def main(args, N=10):
    if args.num_entries:
        N = args.num_entries

    print 'executing', cmd
    p = subprocess.Popen(cmd.split(),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    n = 0
    temp_list = []

    while n < N:
        try:
            text = p.stdout.readline().strip()
            entry = parse_entry(text)
            if check_entry(entry):
                print 'good entry'
                temp_list.append(entry['temperature_C'])
                n += 1
            else:
                print 'bad entry'
        except KeyboardInterrupt:
            break

    p.terminate()
    if n > 0:
        avg = 1.0 * sum(temp_list) / n
        print 'collected %d entries with an average of %.2f' % (N, avg)
        print 'posting to', URL
        post_data(avg)
    else:
        print 'no data collected, exiting'


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('-d', '--dummy', type=float,
                   help='send dummy data and exit')
    p.add_argument('-n', '--num-entries', type=int,
                   help='number of entries to sample before sending')
    return p.parse_args()

if __name__ == '__main__':
    args = parse_args()
    print args

    if args.dummy:
        post_data(args.dummy)
    else:
        print args
        main(args)
