import telnetlib
import logging


with open('domain.txt', 'r') as f:
    for i in f.readlines():
        try:
            tn = telnetlib.Telnet(i.strip(), 20080, timeout=3)
            #print(tn.get_socket())
        except Exception as e:
            logging.error('{0} cat not connect.{1}'.format(i, e))

