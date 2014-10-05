# gentools

A collection of tools that extend the functionality of the *generator object*.

## More declarative generators

The gentools.Define() class allow you write code in an more declarative way
adding the where clause. This enforce the idea of don't tell the computer
what to do, but tell it what is.

### `Define.where()`

The `where()` method inject constants inside the generator. E.g:

```python
>>> from gentools import Define
>>> weight = Define(m*g for m in range(5)).where(g=9.81)
>>> list(weight)
[0.0, 9.81, 19.62, 29.43, 39.24]
```

The `g` var isn't defined inside the generator expression. Either is defined
in the global scope. Only is definde as keyword argument in the invocation of
the where method.
