# 概要

MongoDB是一个开源的文档数据库，他自身提供了高可用性，高性能和自动伸缩的特性。

## 文档数据库

在MongoDB数据库中一条记录被称为一个document，类似于一个JSON对象，类似如下：

```JSON
{
  name: "sue",
  age: 26,
  status: "A",
  groups: ["news", "sports"]

}
```

采用这种类JSON对象来存储数据有以下优势：

- 文档类型(JSON对象)的数据能够适应多种编程语言环境
- 嵌入式的文档对象(文档中的value可以是另一个文档对象)能够减少类似关系数据库中的昂贵的join操作，MongoDB也不支持join操作
- 无须事前定义schema，所以全长更加灵活

## 主要特性

### 高性能

MongoDB支持高性能的数据持久化，特别是：

- 因其支持嵌入式的数据模型，在数据库系统中能减少I/O活动
- 支持索引，能够实现数据的快速查询

### 丰富的查询语言

MongoDB支持数据库该有的create、read、update和delete(CRUD)操作，还支持[数据聚合](https://docs.mongodb.com/manual/core/aggregation-pipeline/)，[文本搜索](https://docs.mongodb.com/manual/text-search/)和[基于地理空间的查询](https://docs.mongodb.com/manual/tutorial/geospatial-tutorial/)。

### 高可用性

MongoDB有复制架构，叫做复本集(replica set)，复本集提供以下特性：

- 自动故障转移
- 数据冗余

MongoDB的复本集是一组运行了MongoDB Serves的实例，这些实例维护的数据相同，他们共同提供了数据的冗余和数据的可用性。

### 支持水平扩展

支持水平扩展是MongoDB核心功能的一部分：

- [sharding](https://docs.mongodb.com/manual/sharding/#sharding-introduction)特性能够跨机器分配数据
- MongoDB 3.4还支持基于shard key来创建[zones](https://docs.mongodb.com/manual/core/zone-sharding/#zone-sharding)的特性，此特性的引入是为了支持企业跨数据中心部署应用实现全球化运作和持续在线

### 支持多存储引擎

MongoDB支持多种存储引擎，例如：

- [WiredTiger Storage Engine](https://docs.mongodb.com/manual/core/wiredtiger/)
- [MMAPv1 Storage Engine](https://docs.mongodb.com/manual/core/mmapv1/)

从MongoDB 3.2开始，WiredTiger storage engine是默认的存储引擎。而且MongoDB还支持可插拔的存储引擎API，这样可以方便的接入第三方存储引擎。
