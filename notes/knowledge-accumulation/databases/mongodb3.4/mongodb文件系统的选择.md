# Filesystem

- 使用RAID来配置所有磁盘分区
- `dbPath`指向的分区避免使用NFS，如果使用NFS可能导致MongoDB的性能退化和不稳定性，如果使用的是VMWare虚拟化，应该使用VMWare virtual drives来代替NFS
- Linux/Unix: 磁盘分区请格式化为EXT4或XFS，如果可能的话，XFS分区与MongoDB一起会工作的更好。
 - 如果使用的是WiredTiger存储引擎，那强烈推荐使用XFS分区，特别是当使用EXT4文件系统遇到性能问题时
- Windows: 请使用NTFS，一定不要使用FAT(FAT 16/32/exFAT)文件系统
