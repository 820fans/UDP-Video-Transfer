# FireStreamer

## 介绍
使用UDP实现低延迟视频传输。

大家拿到这个项目名字的时候，因为都没有做过相关研究，所以每个人进行了不同方面的研究。

这个项目里面是2个人的探索，使用的技术点都是将视频读取成帧图像，一张张图像发送。

组内另一人研究了SRT协议，是基于`视频流`传输，具体可参考这位同学的博客：https://blog.csdn.net/blgpb/article/details/86642522

## 文件夹功能介绍
- `backup`是个人备份，可不看
- `milestone`是里程碑，实现的是无交互（发送端无脑发送，接收端无脑接受）的版本。
- `yuxiang`是组里另一位小伙伴的探索。
- `no_request`是另一位小伙伴完成的多路视频传输。
- `zhangwei`是本人的探索，实现了720p视频传输。相关博客：https://blog.csdn.net/u013033845/article/details/86765598

## 使用介绍
- python3
- 依赖opencv
- 基于`windows`开发，尚未在linux测试
