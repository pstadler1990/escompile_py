[![Build Status](https://travis-ci.com/pstadler1990/escompile_py.svg?branch=master)](https://travis-ci.com/pstadler1990/escompile_py)

# escompile
Small compiler for the ``evoscript`` language (es).

## Known limitations and bugs
- string concatenation is buggy, because of the way it's using the stack. Building 
a string from more than two substrings / literals could end up in a shifted / reversed string.

### Examples
#### Number swapping (w/ temporary variable)
```
let a = 1
let b = 2
let tmp = a
a = b
b = tmp
print("a: " + a)
print("b: " + b)

> a: 2.000000
> b: 1.000000
```

#### Number swapping (w/o temporary variable)
```
let a = 1
let b = 2
a = a - b
b = a + b
a = b - a
print("a: " + a)
print("b: " + b)

> a: 2.000000
> b: 1.000000
```

#### Upcounter
```
let a = 0
repeat
    a = a + 1
    print("a is: " + a)
forever
```

#### Nested loops
Inner loop (a) counts to 5 while outer loop (a) counts to 10
Results in a total amount of 50 inner loop iterations.
```
let a = 0
repeat
    a = a + 1
    let b = 0
    print("outer loop a: " + a)
    repeat
        b = b + 1
        print("-> inner loop b: " + b)
        if(b = 5) then
            exit
        endif
    forever
    if(a = 10) then
        exit
    endif
forever
```

#### FizzBuzz
https://en.wikipedia.org/wiki/Fizz_buzz
```
let i = 1
repeat
    if(i mod 3 = 0 and i mod 5 = 0) then
        print("FizzBuzz")
    elseif(i mod 3 = 0) then
        print("Fizz")
    elseif(i mod 5 = 0) then
        print("Buzz")
    else
        print("" + i)
    endif
    
    if(i >= 100) then
        exit
    endif
    i = i + 1
forever
```

Outputs the famous FizzBuzz pattern:
```
1.000000
2.000000
Fizz
4.000000
Buzz
Fizz
7.000000
8.000000
Fizz
Buzz
11.000000
Fizz
13.000000
14.000000
FizzBuzz
16.000000
...
```