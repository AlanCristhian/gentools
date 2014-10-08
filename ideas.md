## Special types (not yet implemented) (maybe not recommended)

The `Nonlocal` and `Global` types are like the `nonlocal` and `global`
statements.

```python
>>> x = 10
>>> f = (x for _ in Object)
>>> f()
Traceback (most recent call last):
  File "<pyshell#87>", line 1, in <module>
    x
NameError: name 'x' is not defined
```
