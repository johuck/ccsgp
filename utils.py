def zip_flat(a, b):
  """zip two lists and flattens the result

  :returns: flatten list of elements in a & b alternately
  """
  return list(
    itertools.chain.from_iterable(zip(a, b))
  )
