# lightnovel_epub

本工具用于基于[轻之国度](https://lightnovel.us)网页生成`epub`小说。

**注意：本工具仅作学习交流使用，作者不对内容和使用情况付任何责任！**

## 原理

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

## Requirements

* python 3.5 +
* click
* beautifulsoup4
* requests
* ebooklib

## CLI使用方法

下载命令：

```bash
python3 cli.py download <link> <path>
```

下面是我写的 `--help`:

```
$ python3 cli.py download --help
Usage: cli.py download [OPTIONS] URL PATH

  download the light novel

  ARGUMENTS:
  * URL: url of light novel to download
  * PATH: directory to store the light novel

Options:
  --title TEXT       title of light novel
  --authors TEXT     (optional) authors' names, separated by comma (,)
  --identifier TEXT  (optional) identifier of light novel
  --cover_link TEXT  (optional) cover_link of light novel. cover_link can
                     either be web link or file path. if it is not beginned
                     with "http", it would be recognized as file path. if
                     nothing was given, then it will use the first picture of
                     webpage.

  --help             Show this message and exit.
```

注意：命令的 `options` 可以直接忽略，因为执行命令后如果发现没有 `options` 会进行第二轮询问。

## TODO

- [x] 图片下载至临时路径
- [ ] 用 PyQt 写 GUI
- [ ] 为漫画提供更好的支持
- [ ] 增加更多 `metadata` : `tags`, `publisher`, ...
- [ ] 自动抓取标题
- [ ] 自动生成目录，~~如果网页上有 headers 的话~~
- [ ] 添加自定义 CSS / 字体 等支持
- [ ] 简繁自动转换

相关帖子：
* https://www.v2ex.com/t/800508
* https://www.lightnovel.us/cn/themereply/1088005
