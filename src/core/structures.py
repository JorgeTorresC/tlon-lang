## _structures.py
# Defines structures used by tlon-lang
##

import inspect

##
# Class TLONVariable__
# Defines class TLONVariable__ to save scripts variables.
##


class TLONVariable__:
  def __init__(self, name, value=None, kind=None, params={}):
    self.name = name
    self.kind = kind
    self.value = value
    self.params = params

  def __eq__(self, other):
    return isinstance(other, TLONVariable__) and self.name == other.name

  def __str__(self):
    return "- Name: " + self.name + " - Value: " + str(self.value)

  def set_value(self, value):
    self.value = value

##
# Class TLONParameter__
# Defines class TLONParameter__ to manage parameters in functions
##

class TLONParameter__:
  def __init__(self, name, kind=None, mandatory=False, default=None):
    self.name = name
    self.kind = kind
    self.mandatory = mandatory
    self.default = default

  def is_mandatory(self):
    return self.mandatory == True

##
# Class TLONLocalMemory__
# Defines class TLONLocalMemory__ to manage local variables in functions
##

class TLONLocalMemory__:

  name = None
  depth = None
  variables = None

  def __init__(self, name, depth, variables={}):
    self.name = name
    self.depth = depth
    self.variables = {}

    if isinstance(variables, dict):
      for (name, var) in variables.items():
        if isinstance(var, TLONVariable__):
          self.variables[name] = var
        else:
          raise Exception('Error: Wrong type of Variable item.')

  def find(self, name):
    portions = name.split('.')
    current_portion = 0
    result = None
    current = self.variables

    for portion in portions:
      current_portion += 1

      # Is the last portion
      if current_portion == len(portions):

        if isinstance(current, dict):
          result = current.get(portions[-1])
        elif isinstance(current, TLONVariable__):
          if isinstance(current.value, dict):
            result = current.value.get(portions[-1])
          else:
            try:
              result = TLONVariable__(portion, getattr(current.value, portion))
            except Exception as e:
              raise Exception('Error: Variable not found.')
        else:
          try:
            result = TLONVariable__(portion, getattr(current, portion))
          except Exception as e:
            raise Exception('Error: Variable not found.')
      else:
        if isinstance(current, dict):
          nxt = current.get(portion, False)
          if nxt:
            current = nxt
          else:
            raise Exception('Error: Variable not found.')
        elif isinstance(current, TLONVariable__):
          if isinstance(current.value, dict):
            nxt = current.value.get(portion, False)
            if nxt:
              current = nxt
            else:
              raise Exception('Error: Variable not found.')
          else:
            try:
              current = TLONVariable__(portion, getattr(current.value, portion))
            except Exception as e:
              raise Exception('Error: Variable not found.')
        else:
          # Special type of variable
          raise Exception('Error: Variable not found.')

    return result

  def assign(self, name, obj):
    var = self.find(name)

    if var is None:
      self.variables[name] = TLONVariable__(name, obj, 'default')
    else:
      var.set_value(obj)

  def getVariables(self):
    return self.variables

##
# Class __GlobalMemory__
# Defines class __GlobalMemory__ to manage local memories
##

class TLONGlobalMemory__():

  memory_stack = None

  def __init__(self, local_memories=[]):
    self.memory_stack = []

    if type(local_memories) is list:
      if len(local_memories) > 0:
        for memory in local_memories:
          if isinstance(memory, TLONLocalMemory__):
            self.memory_stack.append(memory)
          else:
            raise Exception('Error: Wrong type of Memory item.')
      else:
        main_memory = TLONLocalMemory__('Main', 0)
        self.memory_stack.append(main_memory)
    else:
      raise Exception('Error: Wrong type of Memory item.')

  def find(self, name):
    result = None

    for memory in self.memory_stack:
      try:
        result = memory.find(name)
      except Exception as e:
        pass

      if result is not None:
        break

    return result

  def peek_memory(self):
    return self.memory_stack[-1]

  def assign(self, name, obj):
    var = self.find(name)

    if var is None:
      local_memory = self.peek_memory()
      local_memory.assign(name, obj)
    else:
      var.set_value(obj)