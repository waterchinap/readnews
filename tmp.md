```python
def funa():
    if not n:
        print("n is zero")
        exit()
    print("n is not zero")
    dosomething()

def funb():
    for i in range(10):
        funa()
        dothing()
```
当我运行funb()时，funa()会被调用10次，但是funa()中会有一个if语句，当n为0时，会退出程序，我希望i能在n为0时，跳过funa()，继续执行funb()
