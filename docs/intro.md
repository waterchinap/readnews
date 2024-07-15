---
sidebar_position: 1
---

# 关于本站

这个主要用来一站式看新闻。

## 目录结构

- 主目录为/docs
- 一级目录准备用日期
- 二级目录为频道
- 三级目录为具体文章

目录需要注意的地方：
- 目录下文件如果和目录名相同，就成了一个特殊的文件，不会显示为单独的文件，所以尽量不要和目录名相同。一般不会。
- 最后一级的文件排序还没有想好怎么做。
- 第一级目录按日期倒序排，这个看如何做。
  - 为每一个一级目录创建一个文件，文件名和目录名相同，内容是为了确定一级目录下的顺序。

## 使用

Run the development server:

```bash
cd my-website
npm run start
npm run deploy # deploys your site to cloudflare
```

## 实现思路

- rsshub提供路由
- feedparser解析各频道
- 处理解析的文本，为每个文章生成一个md文件并放入相应文件路径


