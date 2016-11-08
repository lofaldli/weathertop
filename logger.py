from datetime import datetime as dt
import json
import requests
import subprocess

URL = 'http://localhost:5000/add'
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
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
    timestamp = dt.now().strftime(TIME_FORMAT)
    data = {'timestamp': timestamp, 'temperature': temperature}
    r = requests.post(URL, data=data)
    print r.status_code


def main(N=10):
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
                print entry
                temp_list.append(entry['temperature_C'])
                n += 1
        except KeyboardInterrupt:
            break

    p.terminate()
    avg = 1.0 * sum(temp_list) / n
    print 'collected %d entries with an average of %.2f' % (N, avg)
    print 'posting to', URL
    post_data(avg)


if __name__ == '__main__':
    main()
