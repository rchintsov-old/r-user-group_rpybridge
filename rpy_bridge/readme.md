# RPyBridge

Version of 2017-09-01

Only for testing.

## Current state

#### Support:
- flat tables
- matrixes
- numpy arrays
- dictionaries
- lists
- single values (integer, decimal, Boolean)

#### Not support (yet):
- nested tables
- pivot tables
- complex numbers

#### Necessary improvements:
- reading speed (in R)
- big tables support (in R)


## Types conversion
```
    Python         |      R
---------------------------------
 pandas.DataFrame <-> data.frame
                  <-  data.table 
---------------------------------
 numpy.matrix     <->  matrix
 numpy.array       ->  
---------------------------------
 dict              =  list
 list              =  vector
---------------------------------
 int               =  int
 float             =  float
 bool              =  bool
 string            =  string
```


## Syntax

### Python:

```python
save_var(variable, filename, path='', varname='', varlist=False)
```
- *path (optional)* - a string with a path. If you don't specify the place, path will be equal to current working directory.
You can check it by calling ```[this_module].getwd()``` (alias to ```os.getwd()```)

- *varname (optional)* - a string with a single variable name or a list/tuple with a list of variable names in
varlist (if you want to save all them to one file).

- *varlist (optional)* - a boolean that specifies whether 'variable' parameter gets a single variable
or a list of other variables.

If you want to save all variables of your current environment at once, do the following:
- Put all of your variables into a list like ```[var_A, var_B, ...]```
- Pass this list into 'variable' parameter
- Switch 'varlist' to 'True'
- Save by this function
- Profit!

```python
load_var(filename, path='')
```
This return the variable(s) from ***.rpba** file. To get information about this file use ```info_rpba()``` function.

### R:
```r
save_var(variable, filename, varname = '', varlist = FALSE)

load_var(filename)
```

#
Feel free to write me about this code. I'll be glad to get your help or feedback.
