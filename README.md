# gentools

Add the where clause to the generator expression

Usage

The `Define()` class wraps an generator and add the .where() method.

```python
>>> from gentools import Define
>>> weight = Define(m*g for m in range(5)).where(g=9.81)
>>> list(weight)
[0.0, 9.81, 19.62, 29.43, 39.24]
```