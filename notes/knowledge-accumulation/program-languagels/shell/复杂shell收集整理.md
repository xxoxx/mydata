# 网络相关



- 系统网络连接状态统计命令：

```sh

netstat -n | awk '/^tcp/ {++state[$NF]} END {for(key in state) print key,"\t",state[key]}'

```

会得到类似下面的结果，具体数字会有所不同：

LAST_ACK         1
SYN_RECV         14
ESTABLISHED      79
FIN_WAIT1        28
FIN_WAIT2        3
CLOSING          5
TIME_WAIT        1669

也就是说，这条命令可以把当前系统的网络连接状态分类汇总。

状态：描述
CLOSED：无连接是活动的或正在进行
LISTEN：服务器在等待进入呼叫
SYN_RECV：一个连接请求已经到达，等待确认
SYN_SENT：应用已经开始，打开一个连接
ESTABLISHED：正常数据传输状态
FIN_WAIT1：应用说它已经完成
FIN_WAIT2：另一边已同意释放
ITMED_WAIT：等待所有分组死掉
CLOSING：两边同时尝试关闭
TIME_WAIT：另一边已初始化一个释放
LAST_ACK：等待所有分组死掉



参考：http://bbs.51cto.com/thread-1071001-1-1.html
