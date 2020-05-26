[![Build Status](https://travis-ci.com/pstadler1990/escompile_py.svg?branch=master)](https://travis-ci.com/pstadler1990/escompile_py)

# escompile
Small compiler for the ``evoscript`` language (es).

## Known limitations and bugs
- string concatenation is buggy, because of the way it's using the stack. Building 
a string from more than two substrings / literals could end up in a shifted / reversed string.

### Examples
```
let tmp = 5
if(tmp = 3) then
    print("Hello" + " " + "World ->" + tmp)
    let c = tmp + 2
    print("" + c)
else
    print("tmp is 4")
endif
let d = tmp + 99
print("tmp is now: " + d)
print("--- END ---")
```
