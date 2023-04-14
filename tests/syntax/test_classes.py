
import math
import pytest

from scenic.core.errors import TokenParseError, ASTParseError, RuntimeParseError, ScenicSyntaxError
from tests.utils import compileScenic, sampleScene, sampleEgoFrom, sampleEgoActions


def test_old_constructor_statement():
    with pytest.raises(ScenicSyntaxError):
        compileScenic("""
            constructor Foo:
                blah: (19, -3)
            ego = new Foo with blah 12
        """)

def test_python_class():
    scenario = compileScenic("""
        class Foo(object):
            def __init__(self, x):
                 self.x = x
        ego = new Object with width Foo(4).x
    """)
    scene = sampleScene(scenario, maxIterations=1)
    ego = scene.egoObject
    assert ego.width == 4

def test_invalid_attribute():
    with pytest.raises(ScenicSyntaxError):
        compileScenic("""
            class Foo:\n
                blah[baloney_attr]: 4
        """)

def test_invalid_attribute_2():
    with pytest.raises(ScenicSyntaxError):
        compileScenic("""
            class Foo:\n
                blah[additive, baloney_attr]: 4
        """)

def test_invalid_attribute_3():
    with pytest.raises(ScenicSyntaxError):
        compileScenic("""
            class Foo:\n
                blah[additive, 'dynamic']: 4
        """)

def test_invalid_attribute_4():
    with pytest.raises(ScenicSyntaxError):
        compileScenic("""
            class Foo:\n
                blah[additive + dynamic]: 4
        """)

def test_property_simple():
    scenario = compileScenic("""
        class Foo:
            position: (3, 9, 0)
            flubber: -12
        ego = new Foo
    """)
    scene = sampleScene(scenario, maxIterations=1)
    ego = scene.egoObject
    assert type(ego).__name__ == 'Foo'
    assert tuple(ego.position) == (3, 9, 0)
    assert ego.flubber == -12

def test_property_inheritance():
    scenario = compileScenic("""
        class Foo:
            flubber: -12
        class Bar(Foo):
            flubber: 7
        ego = new Bar
    """)
    scene = sampleScene(scenario, maxIterations=1)
    ego = scene.egoObject
    assert type(ego).__name__ == 'Bar'
    assert ego.flubber == 7

def test_property_additive():
    scenario = compileScenic("""
        class Foo:
            flubber[additive]: -12
        class Bar(Foo):
            flubber[additive]: 7
        ego = new Bar
    """)
    scene = sampleScene(scenario, maxIterations=1)
    ego = scene.egoObject
    assert type(ego).__name__ == 'Bar'
    assert ego.flubber == (7, -12)

def test_property_additive_2():
    """Additive properties"""
    ego = sampleEgoFrom("""
        class Parent:
            foo[additive]: 1
        class Child(Parent):
            foo[additive]: 2
        ego = new Child
    """)
    assert ego.foo == (2, 1)

def test_property_final_override():
    """Properties marked as `final` cannot be overwritten"""
    with pytest.raises(RuntimeParseError) as excinfo:
        compileScenic(
            """
                class Parent():
                    one[final]: 1
                class Child(Parent):
                    one: 2
                ego = new Object at (1,1,1)
            """
        )
    assert "property cannot be overridden" in str(excinfo.value)

def test_property_final_specifier():
    """Properties marked as `final` cannot be specified"""
    with pytest.raises(RuntimeParseError) as excinfo:
        compileScenic(
            """
                class MyObject():
                    one[final]: 1
                ego = new MyObject with one 2
            """
        )
    assert "cannot be directly specified" in str(excinfo.value)

def test_isinstance_issubclass():
    scenario = compileScenic("""
        class Foo: pass
        ego = new Foo
        if isinstance(ego, Foo):
            other = new Object at (10, 0)
        if not isinstance(other, Foo):
            new Object at (20, 0)
        if issubclass(Foo, Point):
            new Object at (30, 0)
    """)
    scene = sampleScene(scenario)
    assert len(scene.objects) == 4
