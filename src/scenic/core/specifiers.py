"""Specifiers and associated objects."""

import itertools

from scenic.core.lazy_eval import (DelayedArgument, valueInContext, requiredProperties,
                                   needsLazyEvaluation)
from scenic.core.distributions import toDistribution
from scenic.core.errors import RuntimeParseError

## Specifiers themselves

class Specifier:
	"""Specifier providing values for properties, at various priorities,
	given dependencies.

	Args:
		name: The name of this specifier.
		priorities: A dictionary mapping properties to the priority
		  they are being specified with.
		value: A dictionary mapping properties to the values they are
		  being specified as.
		deps: An iterable containing all properties that this
		  specifier relies on.
	"""
	def __init__(self, name, priorities, value, deps=None):
		assert isinstance(priorities, dict)
		assert isinstance(value, dict) or isinstance(value, DelayedArgument)

		self.priorities = priorities
		self.value = value

		if deps is None:
			deps = set()

		deps |= requiredProperties(self.value)

		for p in priorities:
			if p in deps:
				raise RuntimeParseError(f'specifier for property {p} depends on itself')

		self.requiredProperties = tuple(sorted(deps))
		self.name = name

	def applyTo(self, obj, properties, overriding=False):
		"""Apply specifier to an object"""
		val = valueInContext(self.value, obj)

		assert isinstance(val, dict)

		for prop in properties:
			dist_val = toDistribution(val[prop])
			assert not needsLazyEvaluation(dist_val)
			obj._specify(prop, dist_val, overriding=overriding)

	def __str__(self):
		return f'<{self.name} Specifier for {self.priorities}>'

class ModifyingSpecifier(Specifier):
	"""Specifier providing values for properties, at various priorities,
	given dependencies. Can also modify existing properties.

	Args:
		name: The name of this specifier.
		priorities: A dictionary mapping properties to the priority
		  they are being specified with.
		value: A dictionary mapping properties to the values they are
		  being specified as.
		modifiable_props: What properties specified by this specifier
		  can be modified.
		deps: An iterable containing all properties that this
		  specifier relies on.
	"""
	def __init__(self, name, priorities, value, modifiable_props, deps=None):
		self.modifiable_props = modifiable_props
		super().__init__(name, priorities, value, deps)

## Support for property defaults

class PropertyDefault:
	"""A default value, possibly with dependencies."""
	def __init__(self, requiredProperties, attributes, value):
		self.requiredProperties = set(requiredProperties)
		self.value = value

		def enabled(thing, default):
			if thing in attributes:
				attributes.remove(thing)
				return True
			else:
				return default

		self.isAdditive = enabled('additive', False)
		self.isDynamic = enabled('dynamic', False)
		self.isFinal = enabled('final', False)
		for attr in attributes:
			raise RuntimeParseError(f'unknown property attribute "{attr}"')

	@staticmethod
	def forValue(value):
		if isinstance(value, PropertyDefault):
			return value
		else:
			return PropertyDefault(set(), set(), lambda self: value)

	def resolveFor(self, prop, overriddenDefs):
		"""Create a Specifier for a property from this default and any superclass defaults."""
		for other in overriddenDefs:
			if other.isFinal:
				raise RuntimeParseError(f'"{prop}" property cannot be overridden')
		if self.isAdditive:
			allReqs = self.requiredProperties
			for other in overriddenDefs:
				allReqs |= other.requiredProperties
			def concatenator(context):
				allVals = [self.value(context)]
				for other in overriddenDefs:
					allVals.append(other.value(context))
				return tuple(allVals)
			val = DelayedArgument(allReqs, concatenator, _internal=True) # TODO: @Matthew Change to dicts
		else:
			val = DelayedArgument(self.requiredProperties, self.value, _internal=True)

		return Specifier("PropertyDefault", {prop: -1}, {prop: val})
