安装依赖

apt-get update

```sh
apt-get install libreadline-dev libncurses5-dev libpcre3-dev libssl-dev perl make build-essential
```

编译参数：
```sh
./configure --prefix=/usr/local/openresty-1.11.2.1 \
--user=nginx \
--group=nginx \
--with-file-aio \
--pid-path=/var/run/openresty-1.11.2.1.pid \
--lock-path=/var/lock/subsys/openresty-1.11.2.1 \
--with-http_ssl_module \
--with-http_flv_module \
--with-http_mp4_module \
--with-http_gunzip_module \
--with-http_gzip_static_module \
--with-http_stub_status_module \
--with-http_auth_request_module \
--with-http_realip_module \
--with-http_secure_link_module \
--http-client-body-temp-path=/var/tmp/openresty-1.11.2.1/client \
--http-proxy-temp-path=/var/tmp/openresty-1.11.2.1/proxy \
--http-fastcgi-temp-path=/var/tmp/openresty-1.11.2.1/fastcgi \
--http-uwsgi-temp-path=/var/tmp/openresty-1.11.2.1/uwsgi \
--http-scgi-temp-path=/var/tmp/openresty-1.11.2.1/scgi \
--with-luajit
```


