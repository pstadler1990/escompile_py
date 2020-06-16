[![Build Status](https://travis-ci.com/pstadler1990/escompile_py.svg?branch=master)](https://travis-ci.com/pstadler1990/escompile_py)

# escompile
Small compiler for the ``evoscript`` language (es).

## Known limitations and bugs
- string concatenation is currently buggy, due to the way it's using the stack. Building 
a string from more than two substrings / literals could end up in a shifted / reversed string.

## Description
`escompile` is a tool for lexical analysis, parsing and code generation for the `evoscript` language. 
It's grammar and syntax is mostly based on a modern dialect of the `BASIC` programming language - some
programs may also be compatible. 

## Script file input
TBD

## Code generation
This tool compiles to byte code for a custom virtual machine running on the desired embedded devices.

Currently, each operation (except for the ones creating and dealing with `strings`) is **9 bytes** wide.

```
[1 BYTE OP code] [4 BYTES (u32) arg1] [4 BYTES (u32)]
```

OP = Operation code,

arg1 = operation payload (MSB if arg2),
 
arg2 = operation payload (LSB if arg1)

However, some commands need more than 4 bytes for their argument, so arg1 and arg2 are combined.

```
[1 BYTE OP code] [8 BYTES (u32) arg1]
```

As every number is represented as `double` type, all operations dealing with plain numbers are using the above 
binary format.

## Byte compression
TBD


## Keyword reference
`let` defines a variable with a given name and value.
```
let my_var = 42
```

#### Program flow
`if` / `elseif` / `else` / `endif` allows structuring the control flow of the program.
```
...
if(my_var = 42) then
    ...
elseif(my_var = 69) then
    ...
else
    ...
endif
```

`repeat` .. `until` / `repeat` .. `forever` are used to create loops. 
```
let i = 1
repeat
    i = i + 1
    print("i: " + i)
until i = 10
```
`repeat` .. `until` creates infinite loops.
```
repeat
    print("This will be printed forever")
forever
```
You can use the `exit` keyword to break from loop. This also works in nested loops.

#### Arrays
`let my_arr = [1, 2, 2+1, 42.69]` defines an array with 4 elements (last index is 3!). To access an array's specific index,
use `my_var[<index>]`.

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

#### Iterating over an array
```
let i = [1, 1+1, 3, 42.69]
let j = 0
repeat
    print("i: " + i[j])
    j = j + 1
until j = 4
```
produces
```
i: 1.000000
i: 2.000000
i: 3.000000
i: 42.690000
```

### Was andres
```
let a = 42
if(a = 42) then
    print("eins")
elseif(a = 43) then
    print("zwei")
elseif(a = 44) then
    print("drei")
else
    print("was andres")
endif
```