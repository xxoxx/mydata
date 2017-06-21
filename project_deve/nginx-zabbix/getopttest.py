import re
import sys

# import getopt
#
# args = '-a 1 -b 2 -c 3'.split()
#
# print(args)
#
# opts, args = getopt.getopt(args, 'a:b:c')
# print(opts)
# print(args)
# for opt, arg in opts:
#     print(opt, arg)

#s = '--condition=foo --testing --output-file abc.def -x a1 a2'
#args = s.split()
#print(args)
#print(getopt.getopt(args, 'x:', ['condition=', 'output-file=', 'testing']))



s = '0 322 44 1233333 444444444444555'
#print(re.findall(r'\d{1,}', s))


#def usage():
#    print('Usage: getNginxInfo.py -h 127.0.0.1 -p 80 -a [active|accepted|handled|request|reading|writing|waiting]')
#    sys.exit(1)

#print(sys.argv[1:])


hostlists = [('172.31.0.146', 8134), ('172.31.0.52', 80)]
for ip, port in hostlists:
    print(ip, port)
