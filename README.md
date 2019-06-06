# myscripts
个人常用脚本

## 1. html2xmind

从博客生成xmind思维导图文件

环境
```
requests,xmind,lxml
```
使用命令
```
python html2xmind.py -n name -u url
```

## 2. 163courseTime
从网易云课堂上获取时间信息

```
python 163courseTime.py -f -n -c 1004503010
-f 是否生成csv文件
-n 文件的名称是什么
-c 课程id
```