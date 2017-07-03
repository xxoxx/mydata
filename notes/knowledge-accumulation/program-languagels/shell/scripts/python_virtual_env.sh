 #/bin/bash
 #Program: intall pyenv
 #Author: Neal
 #E_mail: sky_551@163.com
 #Date: 2016-9-22
 #Version 1.0

 # depend
 #apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev
 #apt-get install -y libsqlite3-dev libbz2-dev libreadline6 libreadline6-dev

 #clone pyenv from git
 git clone https://github.com/yyuu/pyenv.git /usr/local/pyenv

 #clone pyenv-virtualenv
 git clone https://github.com/yyuu/pyenv-virtualenv.git /usr/local/pyenv/plugins/pyenv-virtualenv

 #env
 cat <<EOF >> /etc/profile.d/pyenv.sh
 export PYENV_ROOT="/usr/local/pyenv"
 export PATH="\$PYENV_ROOT/bin:\$PATH"
 eval "\$(pyenv init -)"
 eval "\$(pyenv virtualenv-init -)"
 EOF

 echo "*********plase re-login terminal**************"
