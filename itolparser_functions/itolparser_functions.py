#!/usr/bin/env python3

import random
import os
import colorbrewer as cb

list_random = list(range(10)) + ['a' ,'b' ,'c' ,'d' ,'e', 'f']
list_random = [format(x) for x in list_random]

def create_dicts(tmpdf, name, list_vals, CONTINUOUS, MAXCATEGORIES, list_removevals):
  # Get unique values and remove specified items
  nr_values = len(list_vals)

  # Create empty dict
  a_dict = {}

  # check if continuous
  if CONTINUOUS > 0:
    MIN = min(list_vals)
    MAX = max(list_vals)
    for i in list_vals:
      RVAL = int(255 - (((i - MIN) / (MAX - MIN)) * 255))
      GVAL = int(255 - (((i - MIN) / (MAX - MIN)) * 155))
      BVAL = int(150 - (((i - MIN) / (MAX - MIN)) * 150))
      HEX = '#%02x%02x%02x' % (RVAL, GVAL, BVAL)
      a_dict[i] = HEX

    return(a_dict)
  else:

    # if only one after removal: assign black
    if nr_values == 1:
      for i in list_vals:
        a_dict[i] = '#000000'

    # if only two after removal: assign red and grey
    elif nr_values == 2:
      for i in list_vals:
        j = list_vals.index(i)
        HEX = '#%02x%02x%02x' % cb.Set2[3][j]
        a_dict[i] = HEX

    # if 12 or fewer, assign colorbrewer scheme 'Paired'
    elif nr_values <= 12:
      for i in list_vals:
        j = list_vals.index(i)
        HEX = '#%02x%02x%02x' % cb.Paired[nr_values][j]
        a_dict[i] = HEX

    # if 13-18, assign semi-compatible colorbrewer schemes Set1 and Pastel1
    elif nr_values <= 18:
      extra = nr_values - 9
      color_palette = cb.Set1[9] + cb.Pastel1[extra]
      for i in list_vals:
        j = list_vals.index(i)
        HEX = '#%02x%02x%02x' % color_palette[j]
        a_dict[i] = HEX

    # otherwise assign random colours and allow filtering
    else:

      # Get list of counts and select j highest keys. Remove values from list_removevals defined above
      j = MAXCATEGORIES
      list_include = tmpdf[name].value_counts().iloc[:j].index.to_list()
      for removeval in list_removevals:
        if removeval in list_include:
          list_include.remove(removeval)

      # Assign random colors
      for i in list_vals:
        HEX = '#'
        for j in range(6):
          HEX = HEX + random.choice(list_random)
          a_dict[i] = HEX

      # Create alternative dict for filtering, everything not in list_include gets gray colour
      a_dict_alt = dict(a_dict)
      for k in list_vals:
        if k not in list_include:
          a_dict_alt[k] = '#bebebe'

    if nr_values <= 18:
      return(a_dict)
    else:
      return(a_dict_alt, list_include)

def printitol(name, printname, id_name, dict, subdict, outdir, margin, stripwidth, tmpdf, CONTINUOUS):
  pathsafe_name = "".join(i for i in printname if i not in r'\/:*?"<>|')
  FILENAME = 'DATASET_COLORSTRIP_' + pathsafe_name + '.txt'
  FILENAME = FILENAME.replace(' ', '_')
  HEXLEGEND = '#' + random.choice(list_random) + 'f' + random.choice(list_random) + 'f' + random.choice(list_random) + 'f'

  if CONTINUOUS == 0:
    colorstring = ','.join(list(subdict.values()))
    list_names = [format(x) for x in list(subdict.keys())]
    namestring = ','.join(list_names)
    shapestring = ','.join(['1'] * len(subdict.keys()))
  else:
    colorstring = '#ffff96,#006400'
    list_names = [format(x) for x in list(subdict.keys())]
    namestring = list_names[0] + ',' + list_names[-1]
    shapestring = '1,1'

  f = open(os.path.join(outdir, FILENAME), 'w+')
  f.write("DATASET_COLORSTRIP\r\n")
  f.write("SEPARATOR COMMA\r\n")
  f.write("BORDER_WIDTH,0.5\r\n")
  f.write("COLOR," + HEXLEGEND + "\r\n")
  f.write("DATASET_LABEL," + printname + "\r\n")
  f.write("LEGEND_COLORS," + colorstring + ",#ffffff\r\n")
  f.write("LEGEND_LABELS," + namestring + ",NA\r\n")
  f.write("LEGEND_SHAPES," + shapestring + ",1\r\n")
  f.write("LEGEND_TITLE," + printname + "\r\n")
  f.write("MARGIN," + margin + "\r\n")
  f.write("STRIP_WIDTH," + stripwidth + "\r\n")
  f.write("DATA\r\n")

  for index, row in tmpdf.iterrows():
    if dict.get(row[name]) == None:
      tmp_HEX = '#ffffff'
    else:
      tmp_HEX = dict.get(row[name])
    tmp_id = row[id_name]
    tmp_value = row[name]
    f.write(str(tmp_id) + ',' + str(tmp_HEX) + ',' + str(tmp_value) + "\r\n")

  f.close()

