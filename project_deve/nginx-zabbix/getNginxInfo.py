import re
import sys
import getopt
import urllib.request


def usage():
    print('Usage: getNginxInfo.py -h 127.0.0.1 -p 80 -a [active|accepted|handled|request|reading|writing|waiting]')
    sys.exit(1)


def main():
    """default values"""
    host = '127.0.0.1'
    port = '80'
    getinfo = 'None'

    print(len(sys.argv))

    if len(sys.argv) < 7:
        usage()

    try:
        opts, _ = getopt.getopt(sys.argv[1:], 'h:p:a:')
    except getopt.GetoptError:
        usage()

    for opt, arg in opts:
        print(opt, arg)
        if opt == '-h':
            host = arg
        if opt == '-p':
            port = arg
        if opt == '-a':
            getinfo = arg

    url = 'http://' + host + ':' + port + '/nginx_status'

    with urllib.request.urlopen(url) as f:
        result = f.read().decode()
        print(result)
        buffer = re.findall(r'\d{1,}', result)

    if getinfo == "active":
        print(buffer[0])
    elif getinfo == "accepted":
        print(buffer[1])
    elif getinfo == "handled":
        print(buffer[2])
    elif getinfo == "requests":
        print(buffer[3])
    elif getinfo == "reading":
        print(buffer[4])
    elif getinfo == "writing":
        print(buffer[5])
    elif getinfo == "waiting":
        print(buffer[6])
    else:
        print('unknown')
        sys.exit(1)


if __name__ == '__main__':
    main()

