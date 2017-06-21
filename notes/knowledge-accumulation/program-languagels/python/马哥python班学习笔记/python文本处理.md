对文件的操作一般有文件打开、文件读取、文件修改、文件关闭这几个操作。

# file( )方法

文件打开，使用file()方法打开文件，如下语法：

```py
file(name[, mode[, buffering]]) -> file object
```
1. name：表示文件名称
2. mode：表示打开文件时的模式，有`r、w、a`，分别表示读取(默认)、写入、追加。如果在模式后加上“+”号同时表示读写，还有一个模式“b”，表示对二进制文件进行操作
3. buffering：表示对文件操作时是事打开缓冲功能，“0”表示不打开缓冲，“1”表示打开缓冲，任何大于1的数表示缓冲区的大小

举例操作：

```shell
root@master:~/python/day2# pwd
/root/python/day2
root@master:~/python/day2# ls
test.txt
root@master:~/python/day2# cat test.txt   #做测试的文件内容
He is a man
Her is a girl
He is a baby
Her is a child
root@master:~/python/day2# python
Python 2.7.9 (default, Mar  1 2015, 12:57:24)
[GCC 4.9.2] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> file('test.txt','r')
<open file 'test.txt', mode 'r' at 0x7f1e35e114b0>
```
上边以只读方式打开一个文件，返回的是一个地址，我们将无法对此文件进行读取操作，如果以不同的模块打开文件把‘r’做更换即可，如果是'w'模式，那原文件的内容会先被清除。

# open()方法

使用open()方法打开文件，如下语法：

```py
open(name[, mode[, buffering]]) # 返回一个file object
```
语法与file()相同，不再作解释，但在file()的帮助文件档中建议在打开文件时用open()方法

文件读取：

上边把一个文件打开后我们就得到了一个成打开状态的文件句柄，接下来就可以对这个文件进行读取、写入等操作。

读取文件内容的方法有read()、readline()、readlines()、xreadlines()，这几种方法读取文件有何不同以实例来说明。

接着上边的操作：

```python
>>> f = open('test.txt','r')  #把打开文件后获取的地址给予一个变量
>>> f
<open file 'test.txt', mode 'r' at 0x7f489947d540>
>>> file_read = f.read()
>>> print file_read
He is a man
Her is a girl
He is a baby
Her is a child
                                #这里有一个换行
>>> print file_read,    #而在后边加上一个逗号后，输出的最后没有了一个空白行
He is a man
Her is a girl
He is a baby
Her is a child
>>> file_read    #直接输出变量时python会把文件的内容如下显示
'He is a man\nHer is a girl\nHe is a baby\nHer is a child\n'
>>> type(file_read)   #用read()方法获取文件内容后是一个大的字符串
<type 'str'>
>>> f.close()   #最后记得关闭此文件
```

接下来用readline()方法来读取文件：

```python
>>> f = open('test.txt','r')
>>> f.readline()
'He is a man\n'
>>> f.readline()
'Her is a girl\n'
>>> f.readline()
'He is a baby\n'
>>> f.readline()
'Her is a child\n'
>>> f.readline()
''
>>> f.close()
```

从上边的输出可知，readline()一次读取一行内容，读到文件最后时就输出空白字符


再来看看readlines()方法：

```python
>>> f = open('test.txt','r')
>>> file_readlines = f.readlines()
>>> file_readlines
['He is a man\n', 'Her is a girl\n', 'He is a baby\n', 'Her is a child\n']    #用readlines()方法读取文件后，文件的每一行就成了一个列表中的一个元素
>>>f.close()
```

再来看xreadlines()方法：

```python
>>> f = open('test.txt','r')
>>> file_xreadlines = f.xreadlines()
>>> file_xreadlines
<open file 'test.txt', mode 'r' at 0x7f489947d4b0>   #这返回的是什么？查资料说是生成器
>>> type(file_xreadlines)
<type 'file'>
```

那要怎样才能获取file_xreadlines里的内容呢？如下：

```python
>>> for line in file_xreadlines:   #用循环的方式
...     print line,
...
He is a man
Her is a girl
He is a baby
Her is a child
>>>f.close()
```

小结：
在python中打开一个文件有open和file两个方法，但建议使用open方法，而读取文件中的内容时有read、readline、readlines、xreadlines这四个方法，当需要读取的文件比较大时建议用xreadlines方法，这样性能更好。

最后来说下文件的修改操作：

例如我想把上边文件中所有行的“is”更改为“IS”，代码如下：

```python
#!/usr/bin/env python
# -*- coding:utf-8 -*-

f = open('test.txt','r+')
old_str = 'is'
new_str = 'IS'
content = f.readlines() #把文件的所有内容读出来
new_file  = ""   #初始化一个空字符串
for line in content:
    new_line = line.replace(old_str,new_str)
    new_file += new_line  #把替换后的行追加给new_file
    f.seek(0) #每次循环后都把指针指向文件开头
    f.write(new_file) #循环完成后把new_file的内容写入文件
f.close()
```

再来一种方法，代码如下：


```python
#!/usr/bin/env python
# -*- coding:utf-8 -*-

old = 'is'
new = 'IS'
f = open('test.txt','r+')
while True:
    line = f.readline()
    if old in line:
        last_line_pos = f.tell() - len(line) #当前的pos值减去当前行的长度就等于上一行的pos值
        f.seek(last_line_pos)  #把位置指向上一个pos
        new_line = line.replace(old,new)
        f.write(new_line)
    else:
        break
f.close()
```

这种方法有一个致命的bug，如果被替换的字符串的长度与原字符串的长度不一样，那就会发产不能全文替换的情况。



# fileinput模块

在python中要对文件进行处理还是用自带的模块才高效，这里记录一下fileinput模块的常用方法,基本语法如下：

```python
fileinput.input (files=None, inplace=False, backup='', bufsize=0, mode='r', openhook=None)
```

> files:                     #文件的路径列表，默认是stdin方式，多文件['1.txt','2.txt',...]
inplace:                #是否将标准输出的结果写回文件，默认为“0”不会，“1”表示会
backup:                #备份文件的扩展名，只指定扩展名，如.bak。如果该文件的备份文件已存在，则会自动覆盖。
bufsize:                #缓冲区大小，默认为0，如果文件很大，可以修改此参数，一般默认即可
mode:                   #读写模式，默认为只读
openhook:            #该钩子用于控制打开的所有文件，比如说编码方式等;
此模块常用的方法有：
fileinput.input()       #返回能够用于for循环遍历的对象
fileinput.filename()    #返回当前文件的名称
fileinput.lineno()      #返回当前已经读取的行的数量（或者序号）
fileinput.filelineno()  #返回当前读取的行的行号
fileinput.isfirstline() #检查当前行是否是文件的第一行
fileinput.isstdin()     #判断最后一行是否从stdin中读取
fileinput.close()       #关闭队列

举例：

```python
root@master:~/python/day2# vim fileinput_module.py
#!/usr/bin/env python
# -*- coding:utf8 -*-

import fileinput
for line in fileinput.input('test.txt'):
    print 'filename:',fileinput.filename(),'|','line number:',fileinput.lineno(),\
          '|','content:',line,
root@master:~/python/day2# python fileinput_module.py
filename: test.txt | line number: 1 | content: He is a man
filename: test.txt | line number: 2 | content: Her is a girl
filename: test.txt | line number: 3 | content: He is a baby
filename: test.txt | line number: 4 | content: Her is a child
```

先把test.txt还原再来做个测试，如下：

```python
root@master:~/python/day2# vim fileinput_module.py
#!/usr/bin/env python
# -*- coding:utf8 -*-

for line in fileinput.input('test.txt',inplace=1,backup='.bak'):
    print line.replace('is','IIIIIS'),

root@master:~/python/day2# python fileinput_module.py

root@master:~/python/day2# ls test.txt*
test.txt  test.txt.bak
root@master:~/python/day2# cat test.txt
He IIIIIS a man
Her IIIIIS a girl
He IIIIIS a baby
Her IIIIIS a child
root@master:~/python/day2# cat test.txt.bak
He is a man
Her is a girl
He is a baby
Her is a child
```
