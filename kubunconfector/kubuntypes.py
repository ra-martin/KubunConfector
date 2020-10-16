from __future__ import \
	annotations  # -> For Generator[Self] & Return-Type of Self, not needed in Python 3.10

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Generator, List, Literal, NewType, Optional, Type, TypedDict
import typeguard

from .misc import KubunIdentifier

class ConfigLine():
	def __init__(self, name: str, conftype: Type, optional: bool):
		self.name = name
		self.conftype = conftype
		self.optional = optional


class ConfigSet():
	def __init__(self, configLines: List[ConfigLine]):
		self.configLines = configLines

	def getParameter(self, paramName: str):
		p = filter(lambda l: l.name == paramName, self.configLines)
		try:
			return next(p)
		except StopIteration:
			raise Exception(f"ConfigSet: Parameter {paramName} not found.")

	def checkConfig(self, configData: dict, paramName: str):
		for line in self.configLines:
			configParam = configData.get(line.name)

			if configParam is None:
				if not line.optional:
					raise Exception(f"Config is missing some Parameter: Property: { paramName } : { line.name }, { line.conftype }")

			# TODO: Also check for unnecessary options? Re-Serialize this!

			else:
				try:
					typeguard.check_type('variablename', configParam, line.conftype)
				except TypeError:
					raise Exception(
						f"Config is Invalid: Property: { paramName }, ConfigParam: { configParam } , Found: { configParam }, Expected: { line.conftype } ; Config: { configData }")


class LinkTarget(TypedDict):
	target_tag: str
	target_ident: str  # TODO: Validate UUID


TagIdentifier = NewType('TagIdentifier', str)
PropertyIdentifier = NewType('PropertyIdentifier', KubunIdentifier)

NumericConfig = ConfigSet([
	ConfigLine('suffix', str, True)
])

EnumConfig = ConfigSet([
	ConfigLine("variants", List[str], False),
	ConfigLine("ordered", bool, True),
	ConfigLine("logos", List[Optional[str]], True),
	ConfigLine("variants", List[str], True),
])

DateFormat = NewType('DateFormat', Literal['MonthSlashYear', 'DayDotMonthDotYear', 'Year'])

TypeName = NewType('TypeName', Literal[
	'KubunInt',
	'KubunFloat',
	'KubunString',
	'KubunBool',
	'KubunEnum',
	'KubunDate',
	'KubunBox',
	'KubunLink',
	'KubunList',
	'KubunFeatureList',
	'KubunURL',
	'KubunTextArea',
	'KubunLocation'
])


class KubunType():

	def toTypeName(self) -> TypeName:
		return self.__class__.__name__

	@classmethod
	def toDict(cls):
		return cls.__class__.__name__

	@staticmethod
	def getConfigSet() -> ConfigSet:
		return ConfigSet([])

	@staticmethod
	def isStructural() -> bool:
		return False

	@staticmethod
	def isLink() -> bool:
		return False

	@classmethod
	def expectedPropValue(cls) -> KubunType:
		return cls


class KubunInt(int, KubunType):
	@staticmethod
	def getConfigSet() -> ConfigSet:
		return NumericConfig


class KubunFloat(float, KubunType):
	@staticmethod
	def getConfigSet() -> ConfigSet:
		return NumericConfig


class KubunSelector(KubunType):
	def __init__(self, subValues: List[any], subType: KubunType) -> KubunSelector:
		self.subValues = list(map(subType, subValues))
		assert len(subValues) > 0

	def toDict(self):
		return [{'type': s.__class__.__name__, 'value': s} for s in self.subValues]


class KubunString(str, KubunType):
	pass


class KubunTextArea(str, KubunType):
	pass


class KubunBool(KubunType):
	def __init__(self, val: bool):
		self.val = val
	
	def toDict(self) -> bool:
		return self.val


class KubunEnum(str, KubunType):
	@staticmethod
	def getConfigSet() -> ConfigSet:
		return EnumConfig


class KubunDate(KubunType):
	def __init__(self, ts):
		self.dt = datetime.utcfromtimestamp(ts)

	def toDict(self) -> dict:
		return int(self.dt.timestamp())

	@staticmethod
	def getConfigSet() -> ConfigSet:
		return ConfigSet([
			ConfigLine("format", DateFormat, True),
		])


class KubunTags(List[str], KubunType):
	pass


class KubunBox(KubunType):
	@staticmethod
	def isStructural() -> bool:
		return True


class KubunLink(KubunType):
	@staticmethod
	def getConfigSet() -> ConfigSet:
		return ConfigSet([
			ConfigLine("navigate", bool, True),
			ConfigLine("target", LinkTarget, True),
			ConfigLine("reverse_ident", str, True),  # TODO: Validate UUID
			ConfigLine("show_cover", bool, True),
		])

	@classmethod
	def expectedPropValue(cls) -> KubunType:
		return KubunSelector

	@staticmethod
	def isLink() -> bool:
		return True


class KubunList(List[KubunType], KubunType):
	@staticmethod
	def getConfigSet() -> ConfigSet:
		return ConfigSet([
			ConfigLine("subtype", TypeName, False),
			# TODO: Validate me! Should be: ConfigSet
			ConfigLine("subconfig", dict, True),
		])


class KubunFeatureList(List[bool], KubunType):
	@staticmethod
	def getConfigSet() -> ConfigSet:
		return EnumConfig


class KubunURL(str, KubunType):
	@staticmethod
	def getConfigSet() -> ConfigSet:
		return ConfigSet([
			ConfigLine("show_favicon", bool, True),
			ConfigLine("as_button", bool, True),
		])


# TODO: Vec<Vec<String>>, List of paths in a common tree
class KubunHierarchies(List[List[str]], KubunType):
	@staticmethod
	def getConfigSet() -> ConfigSet:
		return ConfigSet([
			ConfigLine("structure", Dict, False),
		])


# TODO: KubunLocation is currently based on Google-Services, which will change in the future.
class KubunLocation(dict, KubunType):
	pass


def typeNameToKubunType(typename: TypeName) -> KubunType:
	return {
		'KubunInt': KubunInt,
		'KubunFloat': KubunFloat,
		'KubunString': KubunString,
		'KubunBool': KubunBool,
		'KubunEnum': KubunEnum,
		'KubunDate': KubunDate,
		'KubunBox': KubunBox,
		'KubunLink': KubunLink,
		'KubunList': KubunList,
		'KubunFeatureList': KubunFeatureList,
		'KubunURL': KubunURL,
		'KubunTextArea': KubunTextArea,
		'KubunTags': KubunTags,
		'KubunHierarchies': KubunHierarchies,
		'KubunLocation': KubunLocation
	}[typename]


# Eg. {"type": "KubunInt", "value": 12} -> KubunInt(12)
def initTypeFromSerialization(data: dict) -> KubunType:
	kubunType = typeNameToKubunType(data['type'])
	return kubunType(data['value'])


class Property():
	def __init__(self, data: dict):

		self.title = str(data['title'])

		# TODO: This is very hacky ( and stupid :( ) and will be changed, in reality we only need "type"
		self.propType = data.get('prop_type')
		self.kubunType = data.get('type')
		self.value = data.get('value')
		self.hidden = bool(data.get('hidden', False))

		if self.kubunType is not None:
			assert self.kubunType == 'KubunBox', "Only KubunBox has the 'type'-Attribute."
			assert self.value is not None, "KubunBox needs a value (can be an empty list)."
			self.value = list(map(lambda p: Property(p), self.value))

		self.typeName = self.propType or self.kubunType
		self.kubunType = typeNameToKubunType(self.typeName)
		self.config = data.get('config')

		if (ident := data.get('ident')) is not None:
			self.ident = KubunIdentifier(ident)
		else:
			assert (self.kubunType.isStructural(
			)), "Only Structural Properties (KubunBox) omit the identifier."
			self.ident = None

		self.kubunType.getConfigSet().checkConfig(self.config or {}, self.title)

	def collect(self) -> Generator[Property]:
		if self.kubunType.isStructural():
			for v in self.value:
				yield from v.collect()
		else:
			yield self

	def pretty_print(self, depth=0):
		prefix = "\t" * depth
		ktypeRepr = f"   [ { self.typeName }"
		if self.kubunType.isLink() and (targetConfig := self.config.get('target')) is not None:
			targetTag = targetConfig['target_tag']
			ktypeRepr += f" -> {targetTag}"
		ktypeRepr += " ]"
		print(f"{prefix}◦ {self.title} {ktypeRepr}")
		if self.kubunType.isStructural():
			for v in self.value:
				v.pretty_print(depth + 1)

	def toDict(self) -> dict:

		if self.kubunType.isStructural():
			value = list(map(lambda p: p.toDict(), self.value))
		else:
			value = None

		ident = None
		if self.ident is not None:
			ident = self.ident.toDict()

		d = {
			"title": self.title,
			"ident": ident,
			"value": value,
			"config": self.config,
			"hidden": self.hidden,
			"type": None,
			"prop_type": None
		}

		if self.kubunType.isStructural():
			d.update({"type": "KubunBox"})  # TODO! Part of Type-Refactoring
		else:
			d.update({"prop_type": self.propType})

		return d

	def isOutboundLink(self) -> bool:
		if self.kubunType is KubunLink:
			return self.config.get('target') is not None
		else:
			return False

	def __repr__(self) -> str:
		return f"<Property: {self.title}>"


class Schema():
	def __init__(self, data: dict):
		self.main = Property(data['main'])
		self.mini = Property(data['mini'])

		self.propLookup: Dict[KubunIdentifier, Property] = {
			p.ident: p for p in self.main.collect() if p.ident is not None
		}

	@staticmethod
	def fromFile(path: Path) -> Schema:
		return Schema(json.loads(path.read_text()))

	@staticmethod
	def fromEmpty() -> Schema:
		return Schema({
			"main": {
				"title": "",
				"ident": None,
				"type": "KubunBox",
				"value": [],
				"config": None
			},
			"mini": {
				"title": "",
				"ident": None,
				"type": "KubunBox",
				"value": [],
				"config": None
			}
		})

	def getProperty(self, propertyIdent: KubunIdentifier) -> Property:

		if type(propertyIdent) is not KubunIdentifier:
			propertyIdent = KubunIdentifier(propertyIdent)

		prop = self.propLookup.get(propertyIdent)
		assert prop is not None, f"Property not found in Schema: { propertyIdent }"
		return prop

	def toDict(self) -> dict:
		return {
			"main": self.main.toDict(),
			"mini": self.mini.toDict()
		}

	def pretty_print(self):
		self.main.pretty_print()

	def __repr__(self) -> str:
		return "<Schema>"


# TODO:
# KubunYoutubeVideo -> Embeds a YT-Video
# KubunSplitPane -> Structural Element, Side-by-side view
# KubunSemanticScholar -> u64, SemanticScholar Ident
