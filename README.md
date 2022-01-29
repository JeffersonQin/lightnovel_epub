- [Introduction](#introduction)
- [Supported Sites Overview](#supported-sites-overview)
- [Requirements](#requirements)
- [Usage Overview](#usage-overview)
- [Usage](#usage)
	- [轻之国度](#轻之国度)
		- [缓存相关](#缓存相关)
	- [轻之国度 App](#轻之国度-app)
		- [Prerequisite](#prerequisite)
		- [Background](#background)
		- [界面布局相关参数](#界面布局相关参数)
		- [旋转相关](#旋转相关)
		- [合并模式相关](#合并模式相关)
		- [缓存相关](#缓存相关-1)
	- [轻小说文库](#轻小说文库)
		- [缓存相关](#缓存相关-2)
		- [指定卷数](#指定卷数)
- [Known Issues](#known-issues)
- [TODO](#todo)
- [Contribution](#contribution)
- [LICENSE](#license)
- [技术分析](#技术分析)
	- [原理概览](#原理概览)
	- [轻之国度网页版 合集文章](#轻之国度网页版-合集文章)

# Introduction

~~本工具用于基于[轻之国度](https://lightnovel.us)网页或 app 生成`epub`小说。~~

Update [2022/01/20]: **现已升级成为轻小说 epub 生成框架，支持更多网站**~~（当年名字取得好啊！）~~

**注意：本工具仅作学习交流使用，作者不对内容和使用情况付任何责任！**

~~本来就是一个面向过程的小工具，怎么越发繁琐起来了。。。这里还要感慨一下LK牛逼的防御技术~~

# Supported Sites Overview

| 站点 | 单页 | 合集 | 详细说明 |
| :--: | :---: | :---: | :-: |
| [轻之国度](https://www.lightnovel.us) | ✅ | ✅ | [说明](#轻之国度) |
| 轻之国度 App | ✅ | ❌ | [说明](#轻之国度-app) |
| [轻小说文库](https://www.wenku8.net/index.php) | ❌ | ✅ | [说明](#轻小说文库) |

# Requirements

* python 3.5 +
* click
* beautifulsoup4
* requests
* ebooklib
* uiautomator2
* dominate
* opencc
* opencv
* js2py

# Usage Overview

下载命令：

```bash
python3 cli.py download <options> <url>
```

下面是我写的 `--help`:

```
$ python3 cli.py download --help
Usage: cli.py download [OPTIONS] URL

  download the light novel

  ARGUMENTS:

  * URL: url of light novel to download

Options:
  --dump-path PATH                directory for dumping files and caches      
  --title TEXT                    title of light novel
  --authors TEXT                  authors' names, separated by comma (,)      
  --identifier TEXT               identifier of light novel
  --cover-link TEXT               cover link of light novel. cover link can   
                                  either be web link or file path. if it is   
                                  not beginned with "http", it would be       
                                  recognized as file path. if nothing was     
                                  given, then it will use the first picture of
                                  webpage.
  --cvt TEXT                      OpenCC conversion configuration, used to    
                                  convert between different Chinese
                                  characters. you can choose the value from
                                  "s2t", "t2s", "s2tw", "tw2s", "s2hk",
                                  "hk2s", "s2twp", "tw2sp", "t2tw", "hk2t",
                                  "t2hk", "t2jp", "jp2t", "tw2t". if nothing
                                  is provided, no conversion would be
                                  performed. for more information, please
                                  visit: https://github.com/BYVoid/OpenCC
  --path PATH                     directory for saving the light novel
  --lk-html-dump PATH             (lightnovel.us) html content dump file path
  --wenku8-volume INTEGER         (wenku8.net) identify the index of the
                                  volume to generate. -1 means every volume,
                                  which is also the default option. index
                                  starts from 1.
  --lk-mobile-top-area-height INTEGER
                                  (lk mobile) the height of the top area
  --lk-mobile-bottom-area-height INTEGER
                                  (lk mobile) the height of the bottom area
  --lk-mobile-image-equal-threshold INTEGER
                                  (lk mobile) the threshold of judging whether
                                  two images are equal
  --lk-mobile-safe-area-padding INTEGER
                                  (lk mobile) the padding of the safe area
  --lk-mobile-vert-dump PATH      (lk mobile) vertical content dump file path
  --lk-mobile-horz-dump PATH      (lk mobile) horizontal content dump file
                                  path
  --lk-mobile-html-dump PATH      (lk mobile) html content dump file path
  --lk-mobile-conflict-mode BOOLEAN
                                  (lk mobile) whether to resolve conflict
                                  manually
  --lk-mobile-ignore-newline BOOLEAN
                                  (lk mobile) whether to ignore newline
  --help                          Show this message and exit.
```

注意：
* 书籍有关的 `options` 可以直接忽略，因为执行命令后如果发现没有 `options` 会进行第二轮询问。
* `dump-path` 是指缓存以及其他的临时文件的输出位置，若提示找不到路径，创建即可
* 针对每个网站，可能有自己的 `options`，具体可以参见 `help` 和下一小节

# Usage

## 轻之国度

Options:

```
  --lk-html-dump PATH             (lightnovel.us) html content dump file path
```

### 缓存相关

* 单页面
  * 会缓存 HTML，每下载一张图片后会用本地路径替换掉 HTML 中的链接
* 合集
  * 每篇文章都会像单页面一样进行缓存

| 情形 | 加载命令 | 描述 | 文件格式 | 文件名规范 |
| :-: | :-: | :-: | :-: | :-: |
| 单文章 | `--lk-html-dump` | 文章内容 | HTML | `<timestamp>.html` |
| 合集内文章 | 无，但会检查 `dump-path` 内是否存在 | 文章内容 | HTML | `<article-id>.html` |

## 轻之国度 App

Options:

```
  --lk-mobile-top-area-height INTEGER
                                  (lk mobile) the height of the top area
  --lk-mobile-bottom-area-height INTEGER
                                  (lk mobile) the height of the bottom area
  --lk-mobile-image-equal-threshold INTEGER
                                  (lk mobile) the threshold of judging whether
                                  two images are equal
  --lk-mobile-safe-area-padding INTEGER
                                  (lk mobile) the padding of the safe area
  --lk-mobile-vert-dump PATH      (lk mobile) vertical content dump file path
  --lk-mobile-horz-dump PATH      (lk mobile) horizontal content dump file
                                  path
  --lk-mobile-html-dump PATH      (lk mobile) html content dump file path
  --lk-mobile-conflict-mode BOOLEAN
                                  (lk mobile) whether to resolve conflict
                                  manually
  --lk-mobile-ignore-newline BOOLEAN
                                  (lk mobile) whether to ignore newline
```

### Prerequisite

首先，不管是模拟器还是真机，都需要开启 ADB。现在的代码只适用于只有一个 ADB 设备的情况，如果有需求，请自行修改 `mobile.py`。

TODO:

- [ ] 日后为这块增加命令行参数

### Background

对 app 模拟手的滚动操作，同时获取元素，最后生成 epub。

注意到：客户端非常恶心，每一行文本都是一个 View，所以我采用了 Portrait 和 Landscape 扫两遍，然后双指针 Merge 的思路来进行对抗，效果喜人。

![](./assets/text-split.png)

### 界面布局相关参数

* `--lk-mobile-top-area-height`: 设备最顶端到导航栏的高度
* `--lk-mobile-bottom-area-height`: 设备下方评论栏的高度
* 上面两个参数默认值为分辨率是 **3840 * 2160** 的情况
* 其余的可以保持默认，有兴趣可以研究

<div align="center">
	<img src="./assets/mobile-params.png" width=300>
</div>

### 旋转相关

* 最开始进入页面之前屏幕应为 Portrait 状态，命令行会要求用户确认
* Portrait 扫描完成之后，设备会自动进入 Landscape 状态，但是需要用户退出界面并重新进入，原因是需要 Layout 重新加载。这一步同样会要求用户确认
* 由于图片的获取是通过截图，所以建议将分辨率调高
* 由于整个过程耗时长，可能出现意外状况，故有若干 `dump` 命令。`--vert-dump` 可以加载之前操作获取的 Portrait (Vertical) 数据，`--horz-dump` 可以加载之前操作获取的 Landscape (Horizontal) 数据，`--html-dump` 可以加载之前导出的 `html` 数据

![](assets/rotate-quit.png)

### 合并模式相关

`--lk-mobile-new-line` 和 `--lk-mobile-conflict-mode`这两个参数的诞生和排版有着密切的关系。举个简单的例子：

<div align="center">
这是一前半段没有加粗的文字<b>这是中间加粗的文字</b>这是最后没有加粗的文字
</div>

如果上面这段话在同一行里，那么会解析成：

```json
[
	"这是一前半段没有加粗的文字\n这是中间加粗的文字\n这是最后没有加粗的文字"
]
```

但是，如果排版变成了：

<div align="center">
这是一前半段没有加粗的文字<b>这是中间加粗的文字</b><br/>这是最后没有加粗的文字
</div>

就会解析成：

```json
[
	"这是一前半段没有加粗的文字\n这是中间加粗的文字", 
	"这是最后没有加粗的文字"
]
```

可以发现有一个 `\n` 就这样凭空消失了。这就会导致一个问题：双指针扫描匹配的时候永远无法找到同样的文字内容。为了解决这个问题，我引入了两个方案：
1. `--lk-mobile-ignore-newline`: 将文中所有出现的 `\n` 全部忽略，效果很好。但是同时，我们也丧失了知道哪里有排版的机会。
2. `--lk-mobile-conflict-mode`: 程序最初的版本如果遇到图片但是文字还没有合并，会直接报错。如果加上了 `--lk-mobile-conflict-mode True` 就会在这个情况下让用户选择选择 Landscape 还是 Portrait 的版本。以后可能还会加上让用户手动输入的选项。

### 缓存相关

上面已经提到，由于整过过程耗时很长，所以在获取完 Landscape 和 Portrait 数据后会分别写入到文件，两组数据合并完成后也会写入到 Html。

| 情形 | 加载命令 | 描述 | 文件格式 | 文件名规范 |
| :-: | :-: | :-: | :-: | :-: |
| 单文章 | `--lk-mobile-vert-dump` | 获取到的 Portrait 数据 | Pickle 二进制数据 | `<timestamp>.out` |
| 单文章 | `--lk-mobile-horz-dump` | 获取到的 Landscape 数据 | Pickle 二进制数据 | `<timestamp>.out` |
| 单文章 | `--lk-mobile-html-dump` | 合并后的数据 | HTML | `<timestamp>.html` |

## 轻小说文库

Options:

```
  --wenku8-volume INTEGER         (wenku8.net) identify the index of the
                                  volume to generate. -1 means every volume,
                                  which is also the default option. index
                                  starts from 1.
```

### 缓存相关

| 情形 | 加载命令 | 描述 | 文件格式 | 文件名规范 |
| :-: | :-: | :-: | :-: | :-: |
| 合集内文章 | 无，但会检查 `dump-path` 内是否存在 | 文章内容 | HTML | `<article-id>.html` |

### 指定卷数

在轻小说文库的总览页面，一般以：卷 => 章 作为导航。而小说生成一般以卷为主。所以我们提供了指定卷数的选项：`--wenku8-volume`，来指定某一卷。若需要一并生成，参数为 -1 或保持默认。

# Known Issues

* 轻之国度
  * 对于部分 **先显示无权限观看**，**后可以观看** 的文章无效，以后可能会写浏览器模式
* 轻之国度 App
  * HTML 排版无法获取
  * 【已解决】 ~~排版问题可能导致 Lanscape / Portrait 信息无法 Merge，如果遇到这种情况，找到任意一个 Case 的 `dump` 文件 (这里记作 `dump-file`)，并加上命令行参数：`--vert-dump <dump-file> --horz-dump <dump-file>`~~

# TODO

- [x] 图片下载至临时路径
- [ ] 用 PyQt 写 GUI ~~(基本上是不可能了，完全不想写，而且也没有意义)~~
- [x] 为漫画提供更好的支持
- [ ] 增加更多 `metadata` : `tags`, `publisher`, ...
- [ ] 自动抓取标题
- [ ] 自动生成目录，~~如果网页上有 headers 的话~~
- [ ] 添加自定义 CSS / 字体 等支持
- [x] 简繁自动转换
- [x] 模拟轻国手机版
- [ ] 增加移动端截屏图片压缩选项
- [ ] 目录多重嵌套
- [ ] 增加移动端 ADB 参数

相关帖子：
* https://www.v2ex.com/t/800508
* https://www.lightnovel.us/cn/themereply/1088005

# Contribution

1. 在 `provider` 文件夹中新建文件，最主要实现两个方法：
   * `get_contents(url, dump_path)` 用来获取信息。返回值可以是 `str` 或 `list`。`list` 内的数据均为 `{'title': title, 'content': content}`
   * `get_cover(link, dump_path)` 用来获取封面。之所以有这个是因为某些站有特殊的 http header，我不说是谁
   * 可以额外设计一些 `options`，写明即可
2. 在 `cli.py` 内接入即可

# LICENSE

* `lightnovel.py`, `cli.py` 使用 AGPL License 授权（`ebooklib` 使用该协议）
* 项目内的其他文件使用 MIT License 进行授权 

# 技术分析

~~以前写好了舍不得删掉所以再开一个板块，下面基本都是废话~~

## 原理概览

直接抓取 HTML，然后将其中的图片下载至本地，随后打包成 EPUB。

EPUB 内部目录：

```
.
├── Images               # 图片
│   ├── ...
│   └── ...
└── Text                 # 文本
    ├── about.xhtml      # 本项目自动生成
    └── lightnovel.xhtml # 轻小说正文
```

对于合集文章：

```
.
├── Images               # 图片
│   ├── ...
│   └── ...
└── Text                 # 文本
    ├── about.xhtml      # 本项目自动生成
    ├── Section1.xhtml   # P1
    ├── Section2.xhtml   # P2
    └── ...
```

TODO: 
- [ ] 日后可能会支持多重嵌套

## 轻之国度网页版 合集文章

对于合集文章，解析的过程比较有趣，这里讨论一下。

首先是对 HTML 的分析。

![](./assets/series-inspector.png)

很遗憾，并不是 `<a>` 也没有 `href`。去 `Source` 里一看，貌似框架选的是 `Vue`，不熟悉前端，不多做评价。

接着查看 `event`，发现是混淆过的 `js`，放弃逆向。

![](./assets/series-event.png)

经观察，数据应该在文档最后的某个 `<script>` 标签内：

![](./assets/series-script.png)

经过分析，这个 `<script>` 只暴露了一个接口：

```js
window.__NUXT__ = (function(...) { ... }) (...)
```

故我们只需要 evaluate 这个脚本，然后获取 `window.__NUXT__` 的值即可。
