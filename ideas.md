###### `Define.With()` (not yet implemented)

The `Define.With()` method alow yo to use context objecst. E.g..

```python
>>> lines = Define(line for line in file).With(file=open('file.txt'))
>>> for l in lines:
...     print(l)

first line
second line
...
```

I capitalize the method `Where` because `With` is a reserved word of python.

## Define functions with `Def()` class (not yet implemented)

You can define functions with generators using the `Def()` class:

```python
>>> add = Def((a + b) for (a, b) in Parameters)
>>> add(2, 3)
5
```

The `Parameters` object is an implicit constant injected in the generator.
This mean that `a` and `b` are functons arguments. So
`add = Def((a + b) for (a, b) in Parameters)` expression is equivalent to:

```python
def add(a, b):
    return a + b
```

As `Def` inherit from Define you can use .where() and .With() methods:

```python
>>> mass = Def(weight/g for weight in Parameters).where(g=9.81)
>>> mass(60)
6.116207951070336
```

You can ensure the tipe of each argument passed to the function.

```python
>>> title_case = Def(text.title().replace(' ', '') for text in Str)
>>> title_case('Alan Cristhian Ruiz')
AlanCristhianRuiz
```

**Warning:** `Def()` only check the type of the argument. Is not for statical
type checking. The `title_case` function is the same as:

```python
def title_case(text):
    assert isinstance(text, gentools.String), \
        TypeError('%s must be an instance of Str' % text)
    return a + b
```

`Def()` support all built-in types but you must declare them as Upercase. E.g.:
`Str` for `str`, `Complex` for `complex`, ...

The `Parameters` type is an alias of the `Object` type.

You can define your own type by subclassing of the `gentools.BaseType`

```python
class CustomType(gentools.BaseType):
    ...

function = Def(x for x in CustomType)
```

Or with the 'gentools.MetaType' metaclass:

```python
class OrderedDict(collections.OrderedDict, metaclass=gentools.MetaType):
    def __init__(self):
        super().__init__()

function = Def(d for d in OrderedDict)
```

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



## `BaseType()` class (not yet implemented)

## `MetaType()` class (not yet implemented)
