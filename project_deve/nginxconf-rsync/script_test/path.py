import os
import glob

#print(os.path.isfile('/tmp/test/1.txt'))
#print(os.path.exists('/tmp/test/*.txt'))
print(glob.glob(r'/tmp/test/.*'))
print(len(glob.glob(r'/tmp/test/.*')) == 0)



#swp
#swx
