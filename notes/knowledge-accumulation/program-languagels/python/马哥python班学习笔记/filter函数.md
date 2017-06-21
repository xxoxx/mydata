filter从字面意思就是过虑，在python中filter()函数的功能也是过虑匹配的字符串，它也是一个高阶函数，它也是接收一个函数和一个序列，fileter()把传入的函数作用于每个元素中，并根据返回值是Ture或Falsea来决定是保留此元素，还是丢弃此元素。

例如，要想获取一个列表中的奇数元素，代码如下：

```py
>>> def is_odd(x):
...     return x % 2 == 1
...
>>> is_odd(2)
False
>>> is_odd(5)
True
>>> filter(is_odd,[4])
[]
>>> filter(is_odd,[1,2,4,5,7,8,9])
[1, 5, 7, 9]
```

如果一个序列中出现了空字符串，我们又需要把空字符串删掉，应该怎么做呢？如下代码：

```py
>>> def not_empty(s):
...     return s.strip()
...
>>> filter(not_empty,['zhaochj','','cora',''])
['zhaochj', 'cora']
```

这里使用了strip()方法，这个方法是用来移除字符串头尾揎的字符，默认为空格，如果是字符串中间有空格，它是不会移除的，如下：

```py
>>> filter(not_empty,['zhaoc  hj','','cora',''])
['zhaoc  hj', 'cora']
```


> 参考：http://www.liaoxuefeng.com/wiki/001374738125095c955c1e6d8bb493182103fac9270762a000/001418612033918f1f341b1e0f14762a118891fa52949aa000
