当你打开一个视频页面的源代码，可以找到某一行，在播放器的位置，有一个 cid 参数。
![](https://www.kindjeff.com/static/img/get_bilibili_user/source_code.png)

B 站发送的请求里也可以看到弹幕请求：
![](https://www.kindjeff.com/static/img/get_bilibili_user/danmu_list.png)

请求弹幕的地址是`http://comment.bilibili.com/看到的cid.xml`

弹幕信息的内容：
`<d p="时间,模式,字体大小,颜色,时间戳,弹幕池,？？？,弹幕ID">内容</d>`。

从这里并不能看到用户的 ID 。上面？？？的部分应该是用户 ID 的某种 hash 。

测试一下。我的B站空间是 http://space.bilibili.com/4764287/ ，其中 `4764287` 是我的 ID 。在弹幕列表找到自己发过的弹幕，？？？部分是 `01da63f0` 。

经过一些测试，**最后发现 `4764287` 经过 CRC32b hash 结果是 `f063da01` ，而储存在弹幕信息里的值是 `01da63f0` 。也就是说，弹幕信息？？？部分是用户 ID CRC32b 之后得到的结果按每两位一组倒序排列的结果。**

所以，已知弹幕信息，想逆向找到发弹幕的用户，需要有所有用户 ID 的 CRC32b 彩虹表（现在 B 站用户 ID 为 1 到接近 60, 000, 000）即可。

而且已经有人做了这件事：[https://danmu.fuckbilibili.com/](https://danmu.fuckbilibili.com/)
