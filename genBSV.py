#############################################################################################################################
# This Python code, given an input array size, generates Bluespec code for odd-even merge sort of an array of	that size. 	
# The generated Bluespec code will take an array of the specified size as input, through the getInput () method.
# The code will display the sorted array elements in order (sorted in ascending order).
# Note: $finish(0) will happen inside the generated module itself.
# Idea of this code: ultimately, the odd-even merge sort comes down to compare-and-swap calls in the correct order. We try 
# to obtain the stages of compare-and-swap operations, each stage containing compare and swaps that can be done in parallel.
#############################################################################################################################

# top-down, for merge (odd-even swap and odd-even merge)
def call2(lo,n,r):
	ans = []
	m = r*2
	if (m<n):
		for i in range(lo+r,lo+n-r,m):
			#parallelized compare and swap calls go into same ans array 
			ans.append((i, i+r))
	else:
		ans = [(lo,lo+r)]
	return ans

# top-down, for sort
def call1(lo,n):
	pairs = []
	y = int(n/2)
	z = y
	while z>0:
		tmp = []
		for a in range(z):
			#parallelized merge calls go into same tmp array
			t = call2(lo+a,n,z)
			for t1 in t:
				tmp.append(t1)
		pairs.append(tmp)
		z=int(z/2)
	return pairs


n = int(raw_input())									# taking number as input

# generating the answer
a = 2
answer = []
while a<=n:
	tx = []
	for y in range(0,n,a):
		#parallelized sort calls go into same tx array
		ty = call1(y,a)
		if len(tx)==0:
			tx = ty
		else:
			for l in range(len(tx)):
				for k in ty[l]:
					tx[l].append(k)
	answer.append(tx)								# bottom-up
	a=a*2

#sol array contains lists of parallelly executing compare and swap calls
sol = []
for x in answer:
	for y in x:
		sol.append(y)

interfaceName = "Oem"
moduleName = "mkOem"
packageName = "OddEven"

# code generation starts
print("package %s;" % (packageName))							# beginning of package
print("import Vector::*;")								# importing modules for vector (array)
print("import ConfigReg::*;\n")								# and configreg (register)

print("interface %s;" % (interfaceName))
print("method Action getInput (Vector#(%d, int) data);" % (n))
print("endinterface: %s\n" % (interfaceName))

print("(* synthesize *)")
print("module %s (%s);" % (moduleName, interfaceName))					# beginning of module
print("\tVector#(%d, Reg#(int)) array <- replicateM (mkConfigReg (0));" % (n))		# array
print("\tReg#(int) n <- mkConfigReg (0);")		
print("\tReg#(int) g <- mkConfigReg (0);\n")
nx = 1											# current rule number

# rules for odd-even swap
for s in sol:
	#putting parallel compare and swap calls in same rule
	print("\trule r_%d (n == %d);" % (nx, nx))
	for s1 in s:
		print("\t\tif (array[%d] > array[%d]) begin" % (s1[0], s1[1]))
		print("\t\t\tarray[%d] <= array[%d];" % (s1[0], s1[1]))
		print("\t\t\tarray[%d] <= array[%d];" % (s1[1], s1[0]))
		print("\t\tend\n")
	nx = nx+1
	print("\t\tn <= %d;" % (nx))
	print("\tendrule\n")

#rule to print array
print("\trule r_%d (n == %d && g < %d);" % (nx+1, nx,n))
print("\t\t$display (array[g]);\n")
print("\t\tg <= g+1;\n")
print("\tendrule")

# rule to finish program
print("\trule r_%d (n == %d && g == %d);" % (nx, nx,n))
print("\t\t$finish(0);\n")			
print("\tendrule")

#method to initialize array
print("\tmethod Action getInput (Vector#(%d, int) data);" % (n))
print("\t\tint i;")
for i in range (n):
	print("\t\tarray[%d] <= data[%d];" % (i, i))
#print("\t\tfor (i = 0; i < %d; i = i+1) begin" % (n))
#print("\t\t\tarray[i] <= data[i];")
#print("\t\tend")
print("\t\tn <= 1;" )
print("\tendmethod: getInput\n")

print("endmodule: %s" % (moduleName))							# end of module
print("\nendpackage: %s" % (packageName))						# end of package
# code generation ends
