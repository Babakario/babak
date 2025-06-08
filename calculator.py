def add(x, y):
  """Returns the sum of x and y."""
  return x + y

def subtract(x, y):
  """Returns the difference of x and y."""
  return x - y

def multiply(x, y):
  """Returns the product of x and y."""
  return x * y

def divide(x, y):
  """Returns the division of x by y."""
  if y == 0:
    raise ZeroDivisionError("Cannot divide by zero")
  return x / y
