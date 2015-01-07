__author__ = 'luckydonald'
import re

unallowed_in_variable_name = re.compile('[\W]+')

class DictObject(dict):
	"""
	DictObject is a subclass of dict with attribute-style access.


			>>> some_dict = { "key": "value" }
			>>> bunch = DictObject( some_dict )

		You can access values either like a dict,

			>>> bunch["key"]
			'value'

		Or object oriented attribute-style access

			>>> bunch.key
			'value'

		Both ways are possible, and the other always reflect the changes

			>>> bunch.key = "something"
			>>> bunch["key"]
			'something'


		--------------
		 Setting data
		--------------

		You can just drop a dict into it.
			>>> a = DictObject({"I": "have", "no": "idea", "what": {"example": "names"}, "to": "choose"})

			>>> a == {"I": "have", "no": "idea", "what": {"example": "names"}, "to": "choose"}
			True

		It's possibly to give a set set of keyword arguments.

			>>> b = DictObject(test="foo", hurr="durr", best_pony = "Littlepip")

			>>> b == {"test": "foo", "hurr": "durr", "best_pony": "Littlepip"}
			True

		You can merge multible dicts at once.

			>>> a = {"one": 1, "two": 2, "three": 3}
			>>> b = {"eins": 1, "zwei": 2, "drei": 3}
			>>> c = DictObject(a, b)
			>>> c == {"one": 1, "two": 2, "three": 3, "eins": 1, "zwei": 2, "drei": 3}
			True

		This works with everything subclassing 'dict', so you can use to_objects too.
		You also can combine everything above.


			>>> d = DictObject(c, unos=1, dos=2, tres=3)
			>>> d =={"one": 1, "two": 2, "three": 3, "eins": 1, "zwei": 2, "drei": 3, "unos": 1, "dos": 2, "tres": 3,}
			True

		And you can define more values anytime by just setting them, per key or attribute

			>>> e = DictObject()

			>>> e["isa"]    = 1
			>>> e["dalawa"] = 2
			>>> e["tatlo"]  = 3

			>>> e.ien = 1
			>>> e.twa  = 2
			>>> e.trije = 3

			>>> e == {"isa":1,"dalawa": 2,"tatlo": 3,"ien": 1,"twa": 2, "trije": 3}
			True

		See below (in the merge_dict function)
		how to merge another dict into a DictObject.

	"""
	_attribute_to_key_map = None  # to resolve the attributes.
	# key is the attribute name,
	# value the full, original name used as original key.
	# Examples:
	# "int_1"    > "1"
	# "foo_2_4_" > "foo-: '2.4;"
	def __init__(self, *args,  **kwargs):
		if len(args) == 1:
			dict.__init__(self,*args, **kwargs)
		else:
			dict.__init__(self, **kwargs)
		self._attribute_to_key_map = {} # else they will be still here if i instanciate a new one.
		kwargs_dict = dict(**kwargs)
		for arg in args:
			self.merge_dict(arg)
		self.merge_dict(kwargs_dict)

	def merge_dict(self, d):
		"""
		---------------
		 Merging dicts
		---------------

		You know what is more fun than a dict?
		Adding more dict to it.

			>>> first_dict  = {"best pony":'Littlepip'}
			>>> b = DictObject( first_dict )

		There we got some DunchDict. Let's merge!

			>>> second_dict = {"best fiction":"Fallout: Equestria"}
			>>> b.merge_dict( second_dict )

		but you can go all fancy and use the += operator:

			>>> b += {"4458":"just google it?"}


			>>> b == {'4458': 'just google it?', 'best fiction':'Fallout: Equestria', 'best pony': 'Littlepip'}
			True

		"""
		if not isinstance(d, dict):
			raise TypeError("Argument is no dict.")
		# self._dict = d
		for a, b in d.items():
			attribute_name = self.get_attribute_name_by_key(a)
			self._add_to_object_part(a, b)
			self._attribute_to_key_map[attribute_name] = a

	def __iadd__(self, other):
		self.merge_dict(other)
		return self

	@staticmethod
	def get_attribute_name_by_key(key):
		"""
		To get a methods name from a key name.
		Methods only allow a-z, A-Z, _ and after the first charakter 0-9

			>>> b = DictObject()

		Keys starting with an Number will be prefixed with 'int_'

			>>> b[2] = "heya"
			>>> b[2]
			'heya'
			>>> b.int_2
			'heya'
			>>> b += { "1": "foo" }
			>>> b.int_1
			'foo'

			>>> b += {"2abc345": "foobar"}
			>>> b.int_2abc345
			'foobar'

		It allows you to use non string values, but they will be prefixed with 'data_', and the rest will be the result
		 of str(key).

			>>> b[False] = 456
			>>> b[False]
			456
			>>> False in b
			True
			>>> b.data_False
			456

			>>> b[None] = 1234
			>>> b.data_None
			1234

		And finally illegal characters will be replaced with underscores, but adding only a singe underscore
		 between legal characters. (nobody likes to count ______ underscores.)

			>>> b += { 'foo-2.4;"':'foo again' }
			>>> b.foo_2_4_
			'foo again'

			# that is was should be in b so far:
			>>> b ==  {False: 456, 2: 'heya', None: 1234, '1': 'foo', 'foo-2.4;"': 'foo again', '2abc345': 'foobar'}
			True

		Now it is possible that 2 keys will be stripped to the same attribute string. To keep them accessable
		 they will be numbered. To be more precisely, '_n' will be appended, with 'n' beeing the next free number.

			>>> del b
			>>> b = DictObject()

			>>> b["1"] = "a"
			>>> b
			{'1': 'a'}

			>>> b[1] =  "b"
			<BLANKLINE>
			CRITICAL WARNING in DictObject: Mapped key '1' to attribute 'int_1_1', because attribute 'int_1' was already set by key '1'.

			>>> b = DictObject()

			>>> b[1] = "a"
			>>> b
			{1: 'a'}

			>>> b['1'] =  "b"
			<BLANKLINE>
			CRITICAL WARNING in DictObject: Mapped key '1' to attribute 'int_1_1', because attribute 'int_1' was already set by key '1'.


		"""

		attribute_name = str(key)
		if str(key)[0].isdigit():
			attribute_name = "int_" + str(attribute_name)
			# to access  a = {'1':'foo'}  with DictObject(a).int_1
			# Note:  a = {'2foo4u':'bar'} will be DictObject(a).int_2foo4u
		elif not isinstance(key, str):
			attribute_name = "data_" + str(attribute_name)
			# a[None] = 'foo'  >   a.data_None

		attribute_name = unallowed_in_variable_name.sub('_', attribute_name)  # a = {'foo-2.4;"':'foo'} becomes DictObject(a).foo_2_4_
		return attribute_name

	def _add_to_object_part(self, name, obj):
		if isinstance(obj, (list, tuple)):  # add all list elements
			dict.__setitem__(self, name, type(obj)(DictObject(x) if isinstance(x, (dict, list, tuple)) else x for x in obj)) # type(obj)( ... for ... in ..)   is same as   [( ... for ... in ..)]
		elif isinstance(obj, dict):  # add dict recursivly
			dict.__setitem__(self, name, DictObject(obj))
		else:  # add single element
			dict.__setitem__(self, name, obj)

	# Items (Array/Dict)

	# no __getitem__ because we want to use the dict's one.

	def __setitem__(self, key, value):
		"""
		Updates the value, or creates a new item.

		>>> b = DictObject({"foo": {"lol": True}, "hello":42, "ponies":'are pretty!'})
		>>> b["foo"] = "updated value"
		>>> b == {'ponies': 'are pretty!', 'foo': 'updated value', 'hello': 42}
		True
		>>> b.foo
		'updated value'
		>>> b["foo"]
		'updated value'
		>>> b["bar"] = "created value"
		>>> b == {'ponies': 'are pretty!', 'foo': 'updated value', 'bar': 'created value', 'hello': 42}
		True
		>>> b["bar"]
		'created value'
		>>> b.bar
		'created value'
		>>> b.barz = "more created value"
		>>> b["barz"]
		'more created value'
		>>> b.barz
		'more created value'
		>>> b.barz = "changed this."
		>>> b["barz"]
		'changed this.'
		>>> b.barz
		'changed this.'

		"""
		attribute_name = self.get_attribute_name_by_key(key)
		unique_attribute_name = attribute_name
		# check, if there is already a key representing this attribute
		if attribute_name in self._attribute_to_key_map and self._attribute_to_key_map[attribute_name] != key:
			# This attribute is already set, but the key is not.
			# Now search for the next free one
			i = 1
			while i != 0:
				unique_attribute_name = attribute_name + "_" + str(i)
				i = i+1 if (unique_attribute_name in self._attribute_to_key_map and
							self._attribute_to_key_map[unique_attribute_name] != key) else 0
							# if is not free name, continue to increase,
							# else, if is free, set to 0 to exit loop
			#end while
			print("\nCRITICAL WARNING in DictObject: Mapped key '%s' to attribute '%s', because attribute '%s' was already set by key '%s'." % (key, unique_attribute_name, attribute_name, self._attribute_to_key_map[attribute_name]))
		self._add_to_object_part(key, value)
		self._attribute_to_key_map[unique_attribute_name] = key

	def __delitem__(self, key):
		attribute_name = self.get_attribute_name_by_key(key)
		del self._attribute_to_key_map[attribute_name]
		dict.__delitem__(self, key)

	# Attributes (Object)

	def __setattr__(self, name, value):
		if name == "_attribute_to_key_map":
			#self._attribute_to_key_map = value
			super(DictObject, self).__setattr__(name, value)
			return
		else:
			key_name = self._attribute_to_key_map[name] if name in self._attribute_to_key_map else name  	# if there is a key representing this attribute
																			# update this key, too

		self._add_to_object_part(name, value)  	# needed allways to keep items  beeing recursive.
		self._attribute_to_key_map[name] = key_name 	# needed only on adding new element. (not when updating)
		# object.__setattr__(self, key, value)
		dict.__setitem__(self,self._attribute_to_key_map[name], value)  # self[self._key_map[key]] = value

	def __getattr__(self, name):
		"""
		Directly pulls the content form the dict itself,
		works as long as _key_map is correct.
		:param name:
		:return:
		"""
		try:
			return dict.__getattribute__(self, name)  # Raise exception if not found in original dict's attributes either
		except AttributeError:
			try:
				if self._attribute_to_key_map:
					key_name = self._attribute_to_key_map[name]  # Check if we have this set.
					return dict.__getitem__(self, key_name)  # self[key_name]
				else:
					print("_attribute_to_key_map not dofined.")

			except KeyError:
				raise AttributeError(name)

	def __delattr__(self, name):
		# object.__delattr__(self, item)
		dict.__delitem__(self, self._attribute_to_key_map[name])
		del self._attribute_to_key_map[name]

	def __contains__(self, k):
		"""

			>>> b = DictObject(ponies='are pretty!')
			>>> 'ponies' in b
			True
			>>> 'foo' in b
			False
			>>> b['foo'] = 42
			>>> 'foo' in b
			True
			>>> b.hello = 'hai'
			>>> 'hello' in b
			True
			>>> b[None] = 123
			>>> None in b
			True
			>>> b[False] = 456
			>>> False in b
			True

		"""
		try:
			return dict.__contains__(self, k) or hasattr(self, k)
		except:
			return False


def ______():
	"""
	For test suite:

		>>> e = {"a":{"b":{"c":{"d": "foo","e":"bar"}}}, "best pony":"Littlepip", "1":"should be 'int_1' as attribute", "foo-:-bar": "should be 'foo_bar' as attribute."}
		>>> b = DictObject(e)
		>>> b == {"a":{"b":{"c":{"d": "foo","e":"bar"}}}, "best pony":"Littlepip", "1":"should be 'int_1' as attribute", "foo-:-bar": "should be 'foo_bar' as attribute."}
		True
		>>> b.a == {'b': {'c': {'e': 'bar', 'd': 'foo'}}}
		True
		>>> b.a.c
		Traceback (most recent call last):
			...
		AttributeError: c
		>>> b.a.b.c == {'e': 'bar', 'd': 'foo'}
		True
		>>> b.a["b"].c == {'e': 'bar', 'd': 'foo'}
		True
		>>> b.a["b"].c["e"] = "barz"
		>>> b == {'a': {'b': {'c': {'e': 'barz', 'd': 'foo'}}}, '1': "should be 'int_1' as attribute", 'foo-:-bar': "should be 'foo_bar' as attribute.", 'best pony': 'Littlepip'}
		True
		>>> b.a["b"].c.e = "barz2"
		>>> b == {'a': {'b': {'c': {'e': 'barz2', 'd': 'foo'}}}, '1': "should be 'int_1' as attribute", 'foo-:-bar': "should be 'foo_bar' as attribute.", 'best pony': 'Littlepip'}
		True
		>>> b.foo_bar
		"should be 'foo_bar' as attribute."
		>>> b["foo-:-bar"]
		"should be 'foo_bar' as attribute."
		>>> b.foo_bar = "changed!"
		>>> b == {'1': "should be 'int_1' as attribute", 'best pony': 'Littlepip', 'foo_bar': 'changed!', 'foo-:-bar': 'changed!', 'a': {'b': {'c': {'e': 'barz2', 'd': 'foo'}}}}
		True
		>>> b.foo_bar
		'changed!'
		>>> b["foo-:-bar"]
		'changed!'
		>>> b["foo-:-bar"] = "changed again!"
		>>> b.foo_bar
		'changed again!'
		>>> b["foo-:-bar"]
		'changed again!'
		>>> b["foo...bar"] = "heya"
		<BLANKLINE>
		CRITICAL WARNING in DictObject: Mapped key 'foo...bar' to attribute 'foo_bar_1', because attribute 'foo_bar' was already set by key 'foo-:-bar'.
		>>> b == {'foo-:-bar': 'changed again!', 'foo...bar': 'heya', '1': "should be 'int_1' as attribute", 'foo_bar': 'changed!', 'best pony': 'Littlepip', 'a': {'b': {'c': {'e': 'barz2', 'd': 'foo'}}}}
		True
		>>> b.foo_bar
		'changed again!'
		>>> b["foo-:-bar"]
		'changed again!'
		>>> b.hello = 'world'
		>>> b.hello
		'world'
		>>> b['hello'] += "!"
		>>> b.hello
		'world!'


		>>> b = DictObject(ponies='are pretty!')
		>>> 'ponies' in b
		True
		>>> 'foo' in b
		False
		>>> b['foo'] = 42
		>>> 'foo' in b
		True
		>>> b.hello = 'hai'
		>>> 'hello' in b
		True
		>>> b[None] = 123
		>>> None in b
		True
		>>> b[False] = 456
		>>> False in b
		True

		>>> m = DictObject()
		>>> m
		{}

	"""
	pass