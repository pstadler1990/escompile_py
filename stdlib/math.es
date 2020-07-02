# Math constants
let EULER = 2.718281828 const
let PI = 3.141592654 const

func abs(n)
	if(n < 0) then
		return -n
	else
		return n
	endif
endfunc

func max(arr)
	# Max function
	# Takes either a single value of type Number or an array of values
	# Returns: 
	# 	The maximum value on success
	#	-1 if failed
	let __t = argtype(arr)
	if(__t = __ARGTYPE_ARRAY) then
		let __alen = len(arr)
		
		if(__alen < 2) then
			return arr[0]
		else
			let __m = arr[0]
			let __i = 0
			repeat
				let __cur_val = arr[__i]
				if(argtype(__cur_val) = __ARGTYPE_STRING) then
					__cur_val = len(arr[__i])
				endif
				
				if(__cur_val > __m) then
					__m = arr[__i]
				endif
				__i = __i + 1
			until __i = __alen
			return __m
		endif
	elseif(__t = __ARGTYPE_NUMBER) then
		# Single argument is always the maximum
		return arr
	else
		return len(arr)
	endif
endfunc

func min(arr)
	# Min function
	# Takes either a single value of type Number or an array of values
	# Returns: 
	# 	The minimum value on success
	#	-1 if failed
	let __t = argtype(arr)
	if(__t = __ARGTYPE_ARRAY) then
		let __alen = len(arr)
		
		if(__alen < 2) then
			return arr[0]
		else
			let __m = arr[0]
			let __i = 0
			repeat
				let __cur_val = arr[__i]
				if(argtype(__cur_val) = __ARGTYPE_STRING) then
					__cur_val = len(arr[__i])
				endif
				
				if(__cur_val < __m) then
					__m = arr[__i]
				endif
				__i = __i + 1
			until __i = __alen
			return __m
		endif
	elseif(__t = __ARGTYPE_NUMBER) then
		# Single argument is always the maximum
		return arr
	else
		return len(arr)
	endif
endfunc

func pow(x, n)
    if(n = 1) then
        return x
    else
        return x * pow(x, n - 1)
    endif
endfunc