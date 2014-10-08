# gentools (experimental)

A collection of experimental tools that extend the functionality of the
*generator object*.

## Another way to define functions (only work with one argument, for now)

Whit `gentools` you can define functions that do *type checking* with yours
arguments and your returned value. All those with an more expressive sintax.
For example, supose that you want this mathematical fuction:

   `ƒ: ℜ → ℜ = {2·x / x ∊ ℜ}`

The above mathematical expression can be writed with the following notation in
Python:

```python
from gentools import Real
f = Real(2*x for x in Real)
```

You can see that the expression `f = Real(2*x for x in Real)` is very
equvalent to `ƒ: ℜ → ℜ = {2·x / x ∊ ℜ}`.

Also this functions do type checking:

```python
>>> from gentools import Real
>>> f = Real(2*x for x in Real)
>>> f(2)
4
>>> f('a')
Traceback (most recent call last):
...
AssertionError: argument value must be a 'number.Real', not 'str'
>>>
```

If you don't care about the type you can use the `Object` type. Is equivalent
to tell "is type object", in Python 3 all is an object.

```python
>>> from gentools import Object
>>> triple = Object(3*x for x in Object)
>>> f(2)
6
>>> f('a')
'aaa'
>>>
```

##### gentools.inject_constants(generator, **constants)

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


##### gentools.Define.where()

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
