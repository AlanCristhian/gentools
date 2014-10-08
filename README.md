# gentools

A collection of experimental tools that extend the functionality of the
*generator object*.


###### gentools.inject_constants(generator, **constants)

Return a copy of of the `generator` parameter. This copy have the constants
defined in the `constants` map. If a key of `constants` share the same name
than a global or local object, then replace such global or local by the value
defined in the `constants` argument.

```python
>>> import gentools as gt
>>> gen = (x*y for x in range(4))
>>> gen2 = gt.inject_constants(gen, y=2)
>>> list(gen2)
[0, 2, 4, 6]
```

Remember that ignores the variables that are outside the scope of the generator
expression. In the example below, first define the `a` var with the `2` value.
Then define the `g` generator. the `g2` generator use "10" as value of `a` but
not `2`.

```python
>>> import gentools as gt
>>> a = 2
>>> gen = (a*b for b in range(4))
>>> gen2 = gt.inject_constants(gen, y=2)
>>> list(gen2)
[0, 10, 20, 30]
```


## More declarative generators whit `Define` class

The gentools.Define() class allow you write code in an more declarative way
adding the where clause. This enforce the idea of don't tell the computer
what to do, but tell it what is.


###### gentools.Define.where()

The `where()` method inject constants inside the generator. E.g:

```python
>>> import gentools as gt
>>> weight = gt.Define(m*g for m in range(5)).where(g=9.81)
>>> list(weight)
[0.0, 9.81, 19.62, 29.43, 39.24]
```

The `g` var isn't defined inside the generator expression. Either is defined
in the global scope. Only is definde as keyword argument in the invocation of
the where method.
