# only for testing
# ver of 2017-09-01

require(rjson)
rpybridge.varlist.count = 1

save_var <- function(variable, filename, varname='', varlist=FALSE){
  
  serialize_main <- function(var_m, name) {
    
    if (name == '')
      name <- deparse(substitute(var_m))
    
    type <- class(var_m)[1]
    
    if (type == 'data.frame') {
      type_n <- 'DF'
      serialized_var <-  toJSON(var_m)
    } else if (type == 'data.table'){
      type_n <- 'DF'
      serialized_var <-  toJSON(var_m)
    } else if (type == 'matrix') {
      type_n <- 'MA'
      serialized_var <-  toJSON(as.data.frame.matrix(t(var_m)))
    } else {
      type_n <- 'RAW'
      serialized_var <-  toJSON(var_m)
    }
    
    length_m <- length(serialized_var)
    sv <- list(header = serialized_var)
    
    return(setNames(sv, paste0(c(length_m, type_n, name), collapse = '&%&')))
  }
  
  packing <- function(var_m, name, varlist) {
    
    if(varlist == FALSE){
      packed <- serialize_main(var_m, name)
    } 
    
    else if(varlist == TRUE){
      serialized_var <- mapply(function(x, y){
        serialize_main(x, y)
      }, var_m, simplify2array(name), SIMPLIFY = F)
      
      length_m = length(toJSON(serialized_var))
      sv <- list(header = serialized_var)
      
      header <- paste0(c(length_m, 'VL', paste0('varlist_', rpybridge.varlist.count)), collapse = '&%&')
      rpybridge.varlist.count <<- rpybridge.varlist.count + 1
      
      packed <- setNames(sv, header)
    }
    return(toJSON(packed))
  }
  
  fn <- paste0(filename, '.rpba')
  fileConn <- file(fn, encoding = 'UTF-8')
  writeLines(packing(variable, varname, varlist), fileConn)
  close(fileConn)
  print(paste0('Successfully saved to ', fn, ' in ',  getwd()))
}



load_var <- function(filename) {
  
  var_info <- function(string){
    size_var <- strsplit(names(fromJSON(string))[1], '&%&', fixed = T)[[1]][1]
    type_var <- strsplit(names(fromJSON(string))[1], '&%&', fixed = T)[[1]][2]
    name_var <- strsplit(names(fromJSON(string))[1], '&%&', fixed = T)[[1]][3]
    return(c(size_var, type_var, name_var))
  }
  
  var_content <- function(string){
    return(simplify2array(fromJSON(string)))
  }
  
  
  unserialize_main <- function(string) {
    
    type_var <- var_info(string)[2]
    
    if (type_var == 'DF'){
      r <- data.frame(fromJSON(var_content(string)[[1]]))
    } else if (type_var == 'MA'){
      temp_m <- as.matrix(data.frame(fromJSON(var_content(string)[[1]])))
      colnames(temp_m) <- NULL
      r <- t(temp_m)
    } else if (type_var == 'RAW'){
      r <- fromJSON(var_content(string)[[1]])
    }
    return(r)
  }
  
  unpacking <- function(string) {
    
    type_var <- var_info(string)[2]
    if (type_var == 'VL'){
      r <- sapply(simplify2array(fromJSON(string)), function(x){
        unserialize_main(toJSON(x))
      })
    } else {
      r <- unserialize_main(string)
    }
    return(r)
  }
  
  fileConn <- file(filename)
  string <- readLines(fileConn, encoding = 'UTF-8')
  close(fileConn)
  
  return(unpacking(string))
}


