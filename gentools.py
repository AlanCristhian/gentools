"""A collection of tools that extend the functionality of
the *generator object*."""

import types
import opcode


def _replace_globals_and_closures(generator, **constants):
    """Replace globals variables and closures inside the generator
    by the values defined in constants."""
    gi_code = generator.gi_code
    new_code = list(gi_code.co_code)
    new_consts = list(gi_code.co_consts)
    locals = generator.gi_frame.f_locals
    new_freevars = list(gi_code.co_freevars)

    i = 0
    # through the list of op_codes
    while i < len(new_code):
        op_code = new_code[i]
        # Replace global lookups by the values defined in *constants*.
        if op_code == opcode.opmap['LOAD_GLOBAL']:
            oparg = new_code[i + 1] + (new_code[i + 2] << 8)
            # the names of all global variables are stored
            # in the .co_names property
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
                new_code[i] = opcode.opmap['LOAD_CONST']
                new_code[i + 1] = pos & 0xFF
                new_code[i + 2] = pos >> 8

        # Here repalce closures lookups by constants lookups with the values
        # defined in *constants*
        if op_code == opcode.opmap['LOAD_DEREF']:
            oparg = new_code[i + 1] + (new_code[i + 2] << 8)
            # !!!: Now the name is sotred i the .co_freevars property
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
                new_code[i] = opcode.opmap['LOAD_CONST']
                new_code[i + 1] = pos & 0xFF
                new_code[i + 2] = pos >> 8
            # !!!: the .co_locals and .co_freevars store the closures names
            # I clear this names because if not the generator can't compile
            if name in locals:
                del locals[name]
                new_freevars.remove(name)
        i += 1
        if op_code >= opcode.HAVE_ARGUMENT:
            i += 2

    # make a string of op_codes
    code_str = ''.join(chr(op_code) for op_code in new_code)

    # NOTE: the lines comented whit the *CUSTOM:* tag mean that such argument
    # is a custom version of the original object

    # create a new *code object* (like generator.gi_code)
    code_object = types.CodeType(
        gi_code.co_argcount,
        gi_code.co_kwonlyargcount,
        gi_code.co_nlocals,
        gi_code.co_stacksize,
        gi_code.co_flags,
        bytes(code_str, 'utf-8'),   # CUSTOM: co_code
        tuple(new_consts),          # CUSTOM: co_consts
        gi_code.co_names,
        gi_code.co_varnames,
        gi_code.co_filename,
        gi_code.co_name,
        gi_code.co_firstlineno,
        gi_code.co_lnotab,
        tuple(new_freevars),        # CUSTOM: co_freevars
        gi_code.co_cellvars)

    # Make a *generator function*
    # NOTE: the *generator functon* make a *generator object* when is called
    function = types.FunctionType(
        code_object,                    # CUSTOM: __code__
        generator.gi_frame.f_globals,   # CUSTOM: __globals__
        generator.__name__,
    )

    # return the *generator object*
    return function(**locals)


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
        self.generator = \
            _replace_globals_and_closures(self.generator, **constants)
        return self

    @property
    def gi_running(self):
        return self.generator.gi_running

    def __iter__(self):
        return self.generator

    def __next__(self):
        return next(self.generator)
