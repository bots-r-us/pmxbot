import unittest

from pmxbot.stack import stack, Stack, help


class DummyStorage():

    def __init__(self, table=None):
        self.table = table or {}

    def get_items(self, topic):
        return self.table.get(topic, [])

    def save_items(self, topic, items):
        self.table[topic] = items


class TestStackAdd(unittest.TestCase):

    def test_stack_add(self):
        Stack.store = DummyStorage()
        self.assertEqual(stack("fumanchu", ""), "(empty)")
        stack("fumanchu", "add foo")
        self.assertEqual(stack("fumanchu", ""), "1: foo")
        stack("fumanchu", "add an interruption")
        self.assertEqual(
            stack("fumanchu", ""),
            "1: an interruption | 2: foo"
        )
        stack("fumanchu", "add [-1] cleanup")
        self.assertEqual(
            stack("fumanchu", ""),
            "1: an interruption | 2: foo | 3: cleanup"
        )
        stack("fumanchu", "add [1] a Distraction")
        self.assertEqual(
            stack("fumanchu", ""),
            "1: an interruption | 2: a Distraction | 3: foo | 4: cleanup"
        )
        stack("fumanchu", "add ['distract'] lunch")
        self.assertEqual(
            stack("fumanchu", ""),
            "1: an interruption | 2: a Distraction | 3: lunch | 4: foo | 5: cleanup"
        )
        stack("fumanchu", "add [0] bar")
        self.assertEqual(
            stack("fumanchu", ""),
            "1: bar | 2: an interruption | 3: a Distraction | 4: lunch | 5: foo | 6: cleanup"
        )

    def test_stack_add_multiple(self):
        Stack.store = DummyStorage()
        self.assertEqual(stack("fumanchu", ""), "(empty)")
        stack("fumanchu", "add foo")
        self.assertEqual(stack("fumanchu", ""), "1: foo")
        stack("fumanchu", "add foo")
        self.assertEqual(stack("fumanchu", ""), "1: foo | 2: foo")
        stack("fumanchu", "add foo")
        self.assertEqual(stack("fumanchu", ""), "1: foo | 2: foo | 3: foo")
        stack("fumanchu", "add ['foo'] bar")
        self.assertEqual(stack("fumanchu", ""), "1: foo | 2: bar | 3: foo | 4: bar | 5: foo | 6: bar")


class TestStackPop(unittest.TestCase):

    def make_colors(self):
        """Set Store.stack to a dummy with ROYGBIV color names as items."""
        Stack.store = DummyStorage({
            "fumanchu": ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
        })
        self.assertEqual(
            stack("fumanchu", "show"),
            "1: red | 2: orange | 3: yellow | 4: green | 5: blue | 6: indigo | 7: violet"
        )

    def test_stack_pop_no_index(self):
        self.make_colors()
        self.assertEqual(stack("fumanchu", "pop"), "-: red")
        self.assertEqual(
            stack("fumanchu", "show"),
            "1: orange | 2: yellow | 3: green | 4: blue | 5: indigo | 6: violet"
        )

    def test_stack_pop_integer_index(self):
        self.make_colors()

        self.assertEqual(stack("fumanchu", 'pop [2]'), "-: orange")
        self.assertEqual(
            stack("fumanchu", "show"),
            "1: red | 2: yellow | 3: green | 4: blue | 5: indigo | 6: violet"
        )

        self.assertEqual(stack("fumanchu", 'pop [-1]'), "-: violet")
        self.assertEqual(
            stack("fumanchu", "show"),
            "1: red | 2: yellow | 3: green | 4: blue | 5: indigo"
        )

        self.assertEqual(stack("fumanchu", 'pop [0]'), "(none popped)")
        self.assertEqual(
            stack("fumanchu", "show"),
            "1: red | 2: yellow | 3: green | 4: blue | 5: indigo"
        )

        self.assertEqual(stack("fumanchu", 'pop [-1200]'), "(none popped)")
        self.assertEqual(
            stack("fumanchu", "show"),
            "1: red | 2: yellow | 3: green | 4: blue | 5: indigo"
        )

        self.assertEqual(stack("fumanchu", 'pop [7346]'), "(none popped)")
        self.assertEqual(
            stack("fumanchu", "show"),
            "1: red | 2: yellow | 3: green | 4: blue | 5: indigo"
        )

    def test_stack_pop_integer_range(self):
        self.make_colors()

        self.assertEqual(stack("fumanchu", 'pop [2:4]'), "-: orange | -: yellow | -: green")
        self.assertEqual(
            stack("fumanchu", "show"),
            "1: red | 2: blue | 3: indigo | 4: violet"
        )

        self.assertEqual(stack("fumanchu", 'pop [-2:]'), "-: indigo | -: violet")
        self.assertEqual(
            stack("fumanchu", "show"),
            "1: red | 2: blue"
        )

        self.assertEqual(stack("fumanchu", 'pop [-2123:]'), "-: red | -: blue")
        self.assertEqual(
            stack("fumanchu", "show"),
            "(empty)"
        )

    def test_stack_pop_text_match(self):
        self.make_colors()

        self.assertEqual(stack("fumanchu", 'pop ["re"]'), "-: red | -: green")
        self.assertEqual(
            stack("fumanchu", "show"),
            "1: orange | 2: yellow | 3: blue | 4: indigo | 5: violet"
        )

    def test_stack_pop_regex(self):
        self.make_colors()

        self.assertEqual(stack("fumanchu", 'pop [/r.*e/]'), "-: red | -: orange | -: green")
        self.assertEqual(
            stack("fumanchu", "show"),
            "1: yellow | 2: blue | 3: indigo | 4: violet"
        )

    def test_stack_pop_first(self):
        self.make_colors()

        self.assertEqual(stack("fumanchu", "pop [first]"), "-: red")
        self.assertEqual(
            stack("fumanchu", "show"),
            "1: orange | 2: yellow | 3: green | 4: blue | 5: indigo | 6: violet"
        )

    def test_stack_pop_last(self):
        self.make_colors()

        self.assertEqual(stack("fumanchu", "pop [last]"), "-: violet")
        self.assertEqual(
            stack("fumanchu", "show"),
            "1: red | 2: orange | 3: yellow | 4: green | 5: blue | 6: indigo"
        )

    def test_stack_pop_multiple_indices(self):
        self.make_colors()

        self.assertEqual(
            stack("fumanchu", "pop [3, -2, 2]"),
            "-: orange | -: yellow | -: indigo"
        )
        self.assertEqual(
            stack("fumanchu", "show"),
            "1: red | 2: green | 3: blue | 4: violet"
        )

    def test_stack_pop_duplicate_indices(self):
        self.make_colors()

        self.assertEqual(
            stack("fumanchu", "pop [6, 6, 6]"),
            "-: indigo"
        )
        self.assertEqual(
            stack("fumanchu", "show"),
            "1: red | 2: orange | 3: yellow | 4: green | 5: blue | 6: violet"
        )

    def test_stack_pop_combo(self):
        self.make_colors()

        self.assertEqual(
            stack("fumanchu", "pop [last, /r.*e/, 5]"),
            "-: red | -: orange | -: green | -: blue | -: violet"
        )
        self.assertEqual(
            stack("fumanchu", "show"),
            "1: yellow | 2: indigo"
        )

    def test_stack_pop_illegal_combo(self):
        self.make_colors()

        self.assertEqual(
            stack("fumanchu", "pop [3, 'stray, comma', 7]"),
            help["index"]
        )


class TestStackShuffle(unittest.TestCase):

    def make_colors(self):
        """Set Store.stack to a dummy with ROYGBIV color names as items."""
        Stack.store = DummyStorage({
            "fumanchu": ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
        })
        self.assertEqual(
            stack("fumanchu", "show"),
            "1: red | 2: orange | 3: yellow | 4: green | 5: blue | 6: indigo | 7: violet"
        )

    def test_stack_shuffle_random(self):
        self.make_colors()

        olditems = set(Stack.store.table["fumanchu"])
        stack("fumanchu", "shuffle")
        self.assertEqual(set(Stack.store.table["fumanchu"]), olditems)

    def test_stack_shuffle_explicit(self):
        self.make_colors()

        self.assertEqual(
            stack("fumanchu", "shuffle [3:5, last, 1]"),
            "1: yellow | 2: green | 3: blue | 4: violet | 5: red"
        )

    def test_stack_shuffle_topic(self):
        self.make_colors()

        self.assertEqual(
            stack("fumanchu", "shuffle fumanchu[3:5, last, 1]"),
            "1: yellow | 2: green | 3: blue | 4: violet | 5: red"
        )

        olditems = set(Stack.store.table["fumanchu"])
        stack("fumanchu", "shuffle fumanchu[]")
        self.assertEqual(set(Stack.store.table["fumanchu"]), olditems)


class TestStackShow(unittest.TestCase):

    def make_colors(self):
        """Set Store.stack to a dummy with ROYGBIV color names as items."""
        Stack.store = DummyStorage({
            "fumanchu": ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
        })

    def test_stack_show_no_index(self):
        self.make_colors()
        self.assertEqual(
            stack("fumanchu", "show"),
            "1: red | 2: orange | 3: yellow | 4: green | 5: blue | 6: indigo | 7: violet"
        )

    def test_stack_show_integer_index(self):
        self.make_colors()

        self.assertEqual(stack("fumanchu", 'show [2]'), "2: orange")
        self.assertEqual(stack("fumanchu", 'show [-1]'), "7: violet")
        self.assertEqual(stack("fumanchu", 'show [0]'), "(empty)")
        self.assertEqual(stack("fumanchu", 'show [-1200]'), "(empty)")

    def test_stack_show_multiline(self):
        self.make_colors()
        self.assertEqual(
            stack("fumanchu", "show m"),
            "1: red\n2: orange\n3: yellow\n4: green\n5: blue\n6: indigo\n7: violet"
        )


class TestStackTopics(unittest.TestCase):

    def make_colors(self):
        """Set Store.stack to a dummy with ROYGBIV color names as items."""
        Stack.store = DummyStorage({
            "fumanchu": ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
        })
        self.assertEqual(
            stack("fumanchu", "show"),
            "1: red | 2: orange | 3: yellow | 4: green | 5: blue | 6: indigo | 7: violet"
        )

    def test_stack_topic_as_nick(self):
        self.make_colors()
        self.assertEqual(stack("sarah", ""), "(empty)")
        self.assertEqual(stack("sarah", "add write tests"), None)
        self.assertEqual(stack("sarah", "show"), "1: write tests")
        # Working on sarah's topic shouldn't alter fumanchu's
        self.assertEqual(
            stack("fumanchu", "show"),
            "1: red | 2: orange | 3: yellow | 4: green | 5: blue | 6: indigo | 7: violet"
        )

    def test_stack_explicit_topics(self):
        self.make_colors()
        self.assertEqual(stack("fumanchu", "show project1[]"), "(empty)")
        self.assertEqual(stack("fumanchu", "add project1[] write tests"), None)
        self.assertEqual(stack("fumanchu", "show project1[]"), "1: write tests")
        # Working on project1's topic shouldn't alter fumanchu's
        self.assertEqual(
            stack("fumanchu", "show"),
            "1: red | 2: orange | 3: yellow | 4: green | 5: blue | 6: indigo | 7: violet"
        )


class TestStackHelp(unittest.TestCase):

    def test_stack_help(self):
        Stack.store = DummyStorage()
        self.assertEqual(stack("fumanchu", "help"), help["help"])
        self.assertEqual(stack("fumanchu", "help add"), help["add"])
        self.assertEqual(stack("fumanchu", "help pop"), help["pop"])
        self.assertEqual(stack("fumanchu", "help show"), help["show"])
        self.assertEqual(stack("fumanchu", "help shuffle"), help["shuffle"])
        self.assertEqual(stack("fumanchu", "help index"), help["index"])
        self.assertEqual(stack("fumanchu", "help stack"), help["stack"])

        self.assertEqual(stack("fumanchu", "not a command"), help["stack"])
