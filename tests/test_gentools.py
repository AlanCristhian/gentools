import gentools
import unittest


class TestDefineBehaviour(unittest.TestCase):
    def test_first_class(self):
        g = gentools.Define(i for _ in range(1)).where(i=5)
        self.assertTrue(isinstance(g, gentools.Define))

    def test_constants_exposition(self):
        """Make sure the constants is not exposed."""
        i = 10
        gentools.Define(i for _ in range(1)).where(i=5)
        self.assertEqual(i, 10)

    def test_next(self):
        """Test direct calls to next()"""
        g = gentools.Define(i for _ in range(3)).where(i=5)
        expected = [5, 5, 5]
        obtained = [next(g), next(g), next(g)]
        self.assertEqual(expected, obtained)

    def test___iter__(self):
        """Check the __iter__ slot is defined to return self.generator"""
        g = gentools.Define(i for _ in range(1)).where(i=5)
        self.assertIs(iter(g), g.generator)

    def test_generator_attributes(self):
        """Check that generator attributes are present"""
        g = gentools.Define(i for _ in range(1)).where(i=5)
        attributes = dir(g)
        self.assertTrue('gi_frame' in attributes)
        self.assertTrue('gi_running' in attributes)
        self.assertTrue('close' in attributes)
        self.assertTrue('send' in attributes)
        self.assertTrue('throw' in attributes)

    def test_running_flag(self):
        """Verify that the running flag is set properly"""
        g = gentools.Define(me.gi_running for i in (0,1))
        me = g
        self.assertEqual(me.gi_running, 0)
        self.assertEqual(next(me), 1)
        self.assertEqual(me.gi_running, 0)

    def test_weak_reference(self):
        """Verify that the object are weakly referencable"""
        import weakref
        g = gentools.Define(i*i for i in range(4))
        wr = weakref.ref(g)
        self.assertTrue(wr() is g)
        p = weakref.proxy(g)
        self.assertTrue(list(p), [0, 1, 4, 9])


g_i = 50
global_g = gentools.Define(g_i for _ in range(3)).where(g_i=5)


class TestDefineMethods(unittest.TestCase):
    def test_global_definition(self):
        self.assertEqual([5, 5, 5], list(global_g))

    def test_constant_global_exposition(self):
        """Make sure the constants is not exposed in the global scope."""
        self.assertEqual(g_i, 50)

    def test_where_method(self):
        a, b, c = 1, 2, 3
        expected = [(a, b, c) for _ in range(5)]
        g = gentools.Define((x, y, z) for _ in range(5)).where(x=1, y=2, z=3)
        obtained = list(g)
        self.assertEqual(expected, obtained)


class TestObjectClass(unittest.TestCase):
    def test__argument_sender_coroutine(self):
        _argument_sender = gentools._argument_sender()
        next(_argument_sender)
        a = _argument_sender.send(1)
        self.assertEqual(a, 1)

    def test_Object(self):
        function = gentools.Object(2*x for x in gentools.Object)
        self.assertEqual(function(1), 2)


class TestFloat(unittest.TestCase):
    def test_Float_arguments(self):
        function = gentools.Float(2*x for x in gentools.Float)
        pattern = "argument value must be a '\w+', not '\w+'"
        with self.assertRaisesRegex(AssertionError, pattern):
            function('a')
        # ensure that function still work
        self.assertAlmostEqual(function(2.0), 4.0)

    def test_Float_result(self):
        function = gentools.Float('x' if x < 2 else x*2 for x in gentools.Float)
        pattern = "returned value must be a '\w+', not '\w+'"
        with self.assertRaisesRegex(AssertionError, pattern):
            function(1.0)
        # ensure that function still work
        self.assertAlmostEqual(function(3.0), 3.0*2)


if __name__ == '__main__':
    unittest.main()
