# 插件管理工具安装 (Vbundle)

插件地址： https://github.com/VundleVim/Vundle.vim

1、 Set up Vundle:

```shell
$ git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim
```

2、 Configure Plugins:

把以下内容保存为`~/.vimrc`文件。

```
set nocompatible              " be iMproved, required
filetype off                  " required

" set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
" alternatively, pass a path where Vundle should install plugins
"call vundle#begin('~/some/path/here')

" let Vundle manage Vundle, required
Plugin 'VundleVim/Vundle.vim'

" The following are examples of different formats supported.
" Keep Plugin commands between vundle#begin/end.
" plugin on GitHub repo
Plugin 'tpope/vim-fugitive'
" plugin from http://vim-scripts.org/vim/scripts.html
Plugin 'L9'
" Git plugin not hosted on GitHub
Plugin 'git://git.wincent.com/command-t.git'
" git repos on your local machine (i.e. when working on your own plugin)
"Plugin 'file:///home/gmarik/path/to/plugin'
" The sparkup vim script is in a subdirectory of this repo called vim.
" Pass the path to set the runtimepath properly.
Plugin 'rstacruz/sparkup', {'rtp': 'vim/'}
" Install L9 and avoid a Naming conflict if you've already installed a
" different version somewhere else.
"Plugin 'ascenator/L9', {'name': 'newL9'}

" All of your Plugins must be added before the following line
call vundle#end()            " required
filetype plugin indent on    " required
" To ignore plugin indent changes, instead use:
"filetype plugin on
"
" Brief help
" :PluginList       - lists configured plugins
" :PluginInstall    - installs plugins; append `!` to update or just :PluginUpdate
" :PluginSearch foo - searches for foo; append `!` to refresh local cache
" :PluginClean      - confirms removal of unused plugins; append `!` to auto-approve removal
"
" see :h vundle for more details or wiki for FAQ
" Put your non-Plugin stuff after this line
```

上边的`Plugin 'file:///home/gmarik/path/to/plugin'`和`Plugin 'ascenator/L9', {'name': 'newL9'}`注释掉，不然可能会报错。

3、 Install Plugins:

在vim中运行`：PluginInstall`命令或在shell中运行`vim +PluginInstall +qall`进行插件安装。


# 树形结构插件安装

如果你想要一个不错的文件树形结构，那么NERDTree是不二之选。

`Plugin 'scrooloose/nerdtree'`

如果你想用tab键，可以利用vim-nerdtree-tabs插件实现：

`Plugin 'jistr/vim-nerdtree-tabs'`

还想隐藏.pyc文件？那么再添加下面这行代码吧：

`let NERDTreeIgnore=['\.pyc$', '\~$'] "ignore files in NERDTree`

以上配置后打开vim并不会有树形窗口出现，还需要配置打开树形窗口的快捷键或默认打开vim就打开树形窗口：

```sh
" NERDTree config
" 自动打开树形
"autocmd vimenter * NERDTree
" F2打开树形
map <F2> :NERDTreeToggle<CR>
autocmd bufenter * if (winnr("$") == 1 && exists("b:NERDTreeType") &&b:NERDTreeType == "primary") | q | endif
```

- 关于使用

快捷键非常多，先记住几个比较常用的。

切换工作台或目录类：

```
ctrl + w + w    光标自动在左右侧窗口切换
ctrl + w + r    切换当前窗口的布局位置，树形窗口可左右切换
ctrl + w + h    光标 focus 左侧树形目录
ctrl + w + l    光标 focus 右侧文件显示窗口
```

编辑文件类：

```
o       在已有窗口中打开文件、目录或书签，并跳到该窗口
i       split 一个新窗口打开选中文件，并跳到该窗口
s       vsplit 一个新窗口打开选中文件，并跳到该窗口
ma      新建文件或目录，目录以`/`结尾
```

其他：

```
P       跳到根结点(大写p)
p       跳到父结点(小写p)
I       切换是否显示隐藏文件
B       切换是否显示书签
```

更多的使用请参考这里： http://yang3wei.github.io/blog/2013/01/29/nerdtree-kuai-jie-jian-ji-lu/ 或 http://www.jianshu.com/p/eXMxGx
