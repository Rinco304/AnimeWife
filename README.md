# 抽二次元老婆

一个适用于HoshinoBot的随机二次元老婆插件

## 如何安装

1. 在HoshinoBot的插件目录modules下clone本项目

    `git clone https://github.com/Rinco304/AnimeWife`

2. 下载 `Releases` 中的  [wife.rar](https://github.com/Rinco304/AnimeWife/releases/download/v1.0/wife.rar) 并将其解压到 `/res/img` 目录下 

3. 在 `config/__bot__.py`的模块列表里加入 `AnimeWife`

4. 重启HoshinoBot

## 怎么使用

```
[抽老婆]	看看今天的二次元老婆是谁
[添加老婆+人物名称+图片]	群管理员每天可以添加一次人物，超级管理员无限制
```

## 备注

`config` 文件夹是用于记录群友每日抽的老婆信息，不用于配置插件，插件的配置位于 ` animewife.py ` 文件中

```
# 群管理员每天可添加老婆的次数
_max=1

# 当超出次数时的提示
max_notice = f'为防止滥用，管理员一天最多可添加{_max}次，若需添加更多请使用 来杯咖啡 联系维护组'
```

若 `Releases` 中下载速度太慢或下载失败，可以尝试使用百度网盘下载

[网盘下载](https://pan.baidu.com/s/1FbRtczF1h1jIov_CXU1qew?pwd=amls)
提取码：amls

## 效果图

![效果图](mdimg.jpg) 

## 参考致谢

| [dailywife](https://github.com/SonderXiaoming/dailywife) | [@SonderXiaoming](https://github.com/SonderXiaoming) |

| [whattoeat](https://github.com/A-kirami/whattoeat) | [@A-kirami](https://github.com/A-kirami) |

| [zbpwife](https://github.com/FloatTech/zbpwife) |（绝大部分老婆图片都是出自这里，个人也添加了一些）
