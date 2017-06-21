import urllib.request
import re

url = 'http://172.31.0.146:8134/nginx_status'
with urllib.request.urlopen(url) as f:
    result = f.read().decode()
    print(result)




buffer = re.findall(r'\d{1,}', result)
print(buffer)
