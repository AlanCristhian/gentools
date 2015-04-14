"""A collection of tools that extend the functionality of
the *generator object*."""

import types
import opcode
import itertools
from collections import deque
import numbers


__all__ = ["inject_constants", "Define", "Function", "new_type", "Object",
    "Float"]


# cache all constants to improve the performance
OPMAP_LOAD_GLOBAL = opcode.opmap['LOAD_GLOBAL']
OPMAP_LOAD_DEREF = opcode.opmap['LOAD_DEREF']
OPMAP_LOAD_CONST = opcode.opmap['LOAD_CONST']
OPCODE_HAVE_ARGUMENT = opcode.HAVE_ARGUMENT


def inject_constants(generator, **constants):
    """Return a copy of of the `generator` parameter. This copy have
    the constants defined in the `constants` map. If a key of
    `constants` share the same name than a global or local object,
    then replace such global or local by the value defined in the
    `constants` argument."""
    # NOTE: all vars with the *new_* name prefix are custom versions of
    # the original attributes of the generator.
    gi_code = generator.gi_code
    new_code = list(gi_code.co_code)
    new_consts = list(gi_code.co_consts)
    new_locals = generator.gi_frame.f_locals
    new_freevars = list(gi_code.co_freevars)
    new_names = list(gi_code.co_names)

    i = 0
    # through the list of instructions
    while i < len(new_code):
        op_code = new_code[i]
        # Replace global lookups by the values defined in *constants*.
        if op_code == OPMAP_LOAD_GLOBAL:
            oparg = new_code[i + 1] + (new_code[i + 2] << 8)
            # the names of all global variables are stored
            # in generator.gi_code.co_names

            # can't use the new_name variable directly because if I clean the
            # name i get an IndexError.
            name = gi_code.co_names[oparg]
            if name in constants:
                value = constants[name]
                # pos is the position of the new const
                for pos, v in enumerate(new_consts):
                    if v is value:
                        # do nothing  if the value is already stored
                        break
                # add the value to new_consts if such value not exists
                else:
                    pos = len(new_consts)
                    new_consts.append(value)
                    # remove unnecessary names
                    new_names.remove(name)
                new_code[i] = OPMAP_LOAD_CONST
                new_code[i + 1] = pos & 0xFF
                new_code[i + 2] = pos >> 8

        # Here repalce locals lookups by constants lookups with the values
        # defined in *constants*
        if op_code == OPMAP_LOAD_DEREF:
            oparg = new_code[i + 1] + (new_code[i + 2] << 8)
            # !!!: Now the name is sotred in generator.gi_code.co_freevars
            name = new_freevars[oparg]
            if name in constants:
                value = constants[name]
                # pos is the position of the new const
                for pos, v in enumerate(new_consts):
                    # do nothing  if the value is already stored
                    if v is value:
                        break
                # add the value to new_consts if such value not exists
                else:
                    pos = len(new_consts)
                    new_consts.append(value)
                    # !!!: generator.gi_code.co_locals and
                    # generator.gi_code.co_freevars store the locals names.
                    # I clear this names because if not the generator can't
                    # compile.
                    new_freevars.remove(name)
                    if name in new_locals:
                        del new_locals[name]
                new_code[i] = OPMAP_LOAD_CONST
                new_code[i + 1] = pos & 0xFF
                new_code[i + 2] = pos >> 8
        i += 1
        if op_code >= OPCODE_HAVE_ARGUMENT:
            i += 2

    # NOTE: the lines comented whit the *CUSTOM:* tag mean that such argument
    # is a custom version of the original object

    # create a new *code object* (like generator.gi_code)
    code_object = types.CodeType(
        gi_code.co_argcount,
        gi_code.co_kwonlyargcount,
        gi_code.co_nlocals,
        gi_code.co_stacksize,
        gi_code.co_flags,
        bytes(new_code),            # CUSTOM: generator.gi_code.co_code
        tuple(new_consts),          # CUSTOM: generator.gi_code.co_consts
        tuple(new_names),           # CUSTOM: generator.gi_code.co_names
        gi_code.co_varnames,
        gi_code.co_filename,
        gi_code.co_name,
        gi_code.co_firstlineno,
        gi_code.co_lnotab,
        tuple(new_freevars),        # CUSTOM: generator.gi_code.co_freevars
        gi_code.co_cellvars)

    # Make a *generator function*
    # NOTE: the *generator functon* make a *generator object* when is called
    function = types.FunctionType(
        code_object,                    # CUSTOM: function.__code__
        generator.gi_frame.f_globals,   # CUSTOM: function.__globals__
        generator.__name__,)

    # return the *generator object*
    return function(**new_locals)       # CUSTOM: generator.gi_frame.f_locals


class Define:
    """Wrap a generator object and extend their behaviours."""
    def __init__(self, generator):
        assert isinstance(generator, types.GeneratorType)
        self.generator = generator
        self.gi_frame = self.generator.gi_frame
        self.close = self.generator.close
        self.send = self.generator.send
        self.throw = self.generator.throw

    def where(self, **constants):
        """Inject the *constants* map as constants inside
        the generator object."""
        self.generator = inject_constants(self.generator, **constants)
        return self

    @property
    def gi_running(self):
        return self.generator.gi_running

    def __iter__(self):
        return self.generator

    def __next__(self):
        return next(self.generator)


def _argument_sender():
    """A *coroutine function* that recceive a value. Yield the value
    if is an instance of *Class* arguent. Raise a TypeError if not."""
    value = None
    while True:
        value = yield value
        yield value


class Function:
    """A type of callable object that can be defined with
    an generator."""
    def __init__(self, base, generator):
        self.generator = generator
        self.base = base
        self.call = self.generator.gi_frame.f_locals['.0'].send
        self.argument_class = self.generator.gi_frame.f_locals['.0']._class

    def __call__(self, arg):
        """Execute the function."""
        assert isinstance(arg, self.argument_class), \
            "argument value must be a '%s', not '%s'" % \
            (self.argument_class.__name__, arg.__class__.__name__)
        self.call(arg)
        result = next(self.generator)
        assert isinstance(result, self.base), \
            "returned value must be a '%s', not '%s'" % \
            (self.base.__name__, result.__class__.__name__)
        return result


class _AddClassPropery:
    """Add the _class property to a generator"""
    def __init__(self, base, generator):
        self.generator = generator
        self.send = self.generator.send
        self._class = base

    @property
    def gi_running(self):
        return self.generator.gi_running

    def __iter__(self):
        return self.generator

    def __next__(self):
        return next(self.generator)


class _MetaType(type):
    """Make a iterable type that ensure that the value sended
    is an instance of the first element of bases argument."""
    def __init__(cls, name, bases, namespace):
        cls.base_type = bases[0]
        return type.__init__(cls, name, bases[1:], namespace)

    def __iter__(cls):
        coroutine = _argument_sender()
        iterable = _AddClassPropery(cls.base_type, coroutine)
        next(iterable)
        return iterable

    def __call__(cls, *args, **kwds):
        """Create an instance of the Function class."""
        return Function(cls.base_type, *args, **kwds)


def new_type(name, base):
    """Create a new Iterable type that make a Function
    instance if is called."""
    return _MetaType(name, (base,), {})


Object = new_type('Object', object)
Float = new_type('Float', float)
# FIXME:
# Real = new_type('Real', numbers.Real)
