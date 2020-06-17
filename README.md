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
use `my_var[<index>]`. Arrays can be made of mixed values, currently `numbers` and `strings`.

```
let b = 42
let a = [1, 2, b]
print("" + a[2])
a[2] = "Hello"
print("" + a[2])
```

outputs:

```
42.000000
Hello
```

## Procedures
Procedures are subroutines without any returned value (in contrast to functions). 

You can define a procedure anywhere in the code, it will be guarded automatically by the compiler.
Use the `sub` and `endsub` keywords to define a procedure.

```
sub my_sub
 ...
endsub
```

You can define procedures to take `n` arguments, if you don't specify any arguments, then the 
parentheses after the procedure's name are optional.

```
sub my_sub(a, b)
 ... do something with a and b
endsub
```

Calling a subroutine (procedure) is done by using the procedures name followed by parantheses, i.e. `my_sub()` or `my_sub(42)`.

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

#### Iterating and changing an array
Changes all members of a zero initialized array to the current counter value:
```
let a = [0, 0, 0, 0]
let i = 0
repeat
    a[i] = i
    print("i after: " + a[i])
    i = i + 1
until i = 4
```
produces
```
i after: 0.000000
i after: 1.000000
i after: 2.000000
i after: 3.000000
```

#### If, elseif, else
```
let a = 42
if(a = 42) then
    print("a is 42")
elseif(a = 43) then
    print("a is 43")
elseif(a = 44) then
    print("a is 44")
else
    print("a is something else")
endif
```

#### Procedures
```
sub count_to_zero(param)
    repeat
        print("" + param)
        param = param - 1
    until param = 0
endsub

print("Now jump into the procedure")
count_to_zero(5)
```

produces:

```
Now jump into the procedure
5.000000
4.000000
3.000000
2.000000
1.000000
```