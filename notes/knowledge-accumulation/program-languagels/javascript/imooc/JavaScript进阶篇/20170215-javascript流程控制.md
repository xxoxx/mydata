# 判断语句（if）

语法：

```js
if (判断条件) {
  条件成立时执行的代码;
}
```

举例：

```js
var mychar = "javascript";
if (mychar == "javascript") {
  document.write("Hello " + mychar);  // 条件成立时执行此语句
}
```

# 判断语句（if...else语句）

`if..else`语句表示对判断条件成立时执行执行代码，条件不成立时执行else后的代码。

语法：

```js
if (条件) {
  条件成立时执行代码;
} else {
  条件不成立时执行代码;
}
```

举例：

```js
var score = 80;
if (score >= 60) {
  document.write("你及格了！");
} else {
  document.write("你没有及格。");
}
```

# 多重判断（if...else嵌套语句）

要在多组语句中选择一组来执行，使用if..else嵌套语句。

语法：

```js
if (条件一) {
  条件一成立时执行的代码;
} else if (条件二) {
  条件二成立时执行的代码;
}
...
else if {条件n} {
  条件n成立时执行的代码;
} else {
  条件1、2 至n不成立时执行的代码;
}
```

举例：

```js
var score = 80;
if (score >= 60 && score < 70) {
  document.write("你及格了，但还得加油。");
} else if (score >= 70 && score < 80) {
  document.write("还不错，继续努力。");
} else if (score >= 80){
  document.write("非常棒！");
} else {
  document.write("你没有及格，要努力得了！");
}
```

# 多种选择（switch语句）

当有很多种选择时，可以使用switch，比使用`if...else if`更方便。

语法：

```js
switch (expression) {
  case expression-1:
    执行代码 1;
    break;
  case expression-2:
    执行代码 2;
    break;
  ...
  case expression-n:
    执行代码 n;
    break;
  default:
    与expression-1, expression-2, ..., expression-n不同时执行的代码;
}
```

举例：

```js
var choice = 2;

switch (choice) {
  case 1:
    document.write("周一学习html");
    break;
  case 2:
  case 3:
  case 4:
    document.write("周二、周三、周四学习javascript");
    break;
  case 5:
    document.write("周五学习css");
    break;
  case 6:
  case 7:
    document.write("周六与周日休息");
    break;
}
```

上边代码将输出： `周二、周三、周四学习javascript`。

总结：

1、 当多个选项的操作是相同时可以类似这样写：

```js
case 2:
case 3:
case 4:
  document.write("周二、周三、周四学习javascript");
  break;
```

2、 所有执行语句后边都要加上一个break语句，否则就会直接继续执行下边case中的语句。

3、 default语句可以省略。

# for循环

for循环可让计算机重复做一件事情，这也是计算机擅长的。

语法：

```js
for (初始化变量; 循环条件; 循环迭代) {
  循环语句;
}
```

举例，计算`1...100`的和：

```js
var n, sum=0;
for (n=1; n<=100; n++) {
  sum = sum + n;
}
document.write("1+2+3+...+100=" + sum);  // 结果为5050
```

# while循环

语法：

```js
while (条件判断) {
  循环语句;
}
```

while循环重复执行一段代码，直到条件不再满足。

举例：

```js
var n=1, sum=0;

while (n<=100) {
  sum = sum + n;
  n++;
}
document.write("sum=" + sum); // 结果为5050
```

# do...while循环

语法：

```js
do {
  循环语句;
}
while (判断条件)
```

`do...while`循环保证至少被执行一次。先执行do中的语句，再做条件判断。

举例：

```js
var num = 10;

do {
  document.write(num + "<br />");  // 输出 10 11 12 13
  num++;
}
while (num < 14)
```

# 退出循环（break）

在`while、for、do...while、while`循环中使用`break`语句退出当前循环，直接执行后面的代码。

语法：

```js
for (初始条件; 判断条件; 循环后条件值更新) {
  if (退出条件) {
    break;
  }
  循环代码;
}
```

举例：

```js
var n;

for (n=1; n<=10; n++) {
  if (n * 2 > 10) {
    break;
  }
  document.write(n);  // 当n为5时上边的退出条件满足，输出 12345
}
```

# 继续循环（continue）

continue的作用是当一个条件满足时就跳出本次的循环，而整个循环体继续执行。

语法：

```js
for (初始值; 判断条件; 循环后条件更新) {
  if {跳出循环的判断} {
    continue;
  }
  循环代码;
}
```

举例，计算100内奇数之和：

```js
var oddSum=0, n;
for (n=1; n<=100; n++) {
  if (n%2 === 0) {  // 跳过偶数
    continue;
  }
  oddSum = oddSum + n;
}

document.write(oddSum);  // 2500
```
