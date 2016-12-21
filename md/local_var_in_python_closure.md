### Python作用域的一些麻烦
Python 的作用域有这样的规则，你在内部的局部作用域里，仅仅使用外部的变量是允许的，但是改变这个引用本身是不被允许的。

```python
def outer():
    v = 2
    def inner():
        t = v + 1
        print(t)
    return inner
```

上面的代码是没有错误的， v 被认为是外部作用域的变量，引用它是可以的。

```python
def outer():
    v = 2
    def inner():
        v = 3
        v += 1
        print(v)
    return inner
```

上面也是没有错误的， v 被定义为内部作用域的变量，对它的操作和外部的 v 无关。


但是，这样是错误的：

```python
def outer():
    v = 2
    def inner():
        t = v + 1
        print(t)
        v = t
    return inner
```

上面的例子里，执行`t = v + 1`这一行时会报错，因为这个作用域里有改变 v 本身的操作：`v = t`，所以 v 被认为是一个内部的变量，而我们并不能在这个作用域里找到它的定义。

这个时候需要使用 `nonlocal` 关键字，把 v 声明为外部作用域的变量：

*（ Python2 并没有 nonlocal 关键字，所以没有办法在内部的局部作用域改变外部的局部作用域的变量本身。当然可以使用可变对象如 list 来模拟这样的效果，但你仍旧不能修改这个引用本身指向的对象。）*

*（同理，局部作用域里引用全局变量是可以的，但是当你要改变它时，需要加上`global`关键字。）*

例1：

```python
def outer():
    v = 2
    def inner():
        nonlocal v
        t = v + 1
        print(t)
        v = t
    return inner
```

例2：

```python
def outer(v):           # 传入的参数 v 同样是 outer 作用域的变量
    def inner():
        nonlocal v      # 如果你打算改变它，也需要加上 nonlocal 关键字
        t = v + 1
        print(t)
        v = t
    return inner
```

如果你熟悉 javascript 或者其他可以使用闭包的语言，会因为 Python 处理作用域的机制遇到麻烦。

### 下面是对于几种情况的分析

先来看第一种情况，内部作用域仅仅使用外部变量而不改变它：

![](https://www.kindjeff.com/static/img/local_var_in_python_closure/right_closure_1.jpg)

![](https://www.kindjeff.com/static/img/local_var_in_python_closure/right_closure_2.jpg)

这种是一种正确的情况。

从 `print` 出的`v.__str__`可以看到 v 的地址是`0x5C7D5920`；`a.__closure__`是 a 包含的cell对象的元组，可以看到里面只有一个cell对象，并且持有一个 int 类型的对象，地址同样是`0x5C7D5920`。

*（一个 cell 对象用来保存一个在多个作用域中被引用的变量的值。例如这里的 v 在 outer 中被引用，也在inner中被引用，它就会被保存在一个 cell 对象里。）*

后一张图是`dis.dis(a)`得到的字节码。

`LOAD_DEFRED`是从cell中得到对象的内容并 push 进栈。也就是说，是从 cell 里得到的 v 值。

----

第二种情况，内部作用域改变外部变量：

![](https://www.kindjeff.com/static/img/local_var_in_python_closure/wrong_closure_1.jpg)

![](https://www.kindjeff.com/static/img/local_var_in_python_closure/wrong_closure_2.jpg)

这种情况调用`a()`时会报错。

`a.__closure__`没有内容，也就是说，它并不认为 inner 里引用了 outer 作用域的变量，所以并没有创建 cell 来存储任何变量。

看字节码。第一行就是`LOAD_FAST`，把变量 v 的值压入栈。而在此之前 v 并没有被定义，于是会在这里报错。

----

第三种情况，使用 nonlocal 关键字：

![](https://www.kindjeff.com/static/img/local_var_in_python_closure/nonlocal_closure_1.jpg)

![](https://www.kindjeff.com/static/img/local_var_in_python_closure/nonlocal_closure_2.jpg)

`a.__closure__`有一个 cell 对象，且它持有的一个对象的地址和`print`看到的 v 的地址相同。

字节码里的 20 和 23 开头的这两行是`v = t`的步骤。去掉这个，字节码以及`a.__closure__`都和第一种情况完全相同。也就是说，内部的 v 是用一个 cell 对象储存起来、和外部 v 同样的对象。
