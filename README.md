# Lump Quantum Annealer Encoding from Quantum Gate Circuit
```
-----------------------------------------------------------------------------------------------------
GENERAL NOTES
-----------------------------------------------------------------------------------------------------
 
 - Set PYTHONPATH to Lump-Annealer-Encoding-From-Gate-Circuit/logical directory or
   Lump-Annealer-Encoding-From-Gate-Circuit/blochsphere directory to run corresponding examples
   
   e.g., ~/path/to/Lump-Annealer-Encoding-From-Gate-Circuit/logical$ export PYTHONPATH=$(pwd)

-----------------------------------------------------------------------------------------------------
CONTENTS
-----------------------------------------------------------------------------------------------------

   I) Gate circuit-to-lump annealer embedding by way of intermediate logical truth table 
      representation
   	  - Covers implementation through an example of an XNOR function
	  - TODO list
	
   II) Bloch sphere truth table representation of qubit
   	  - Notes and ideas on this approach
	  	- General Notes
		- Annealer embeddings for single gates using Bloch sphere
		  truth table representation of qubit
	  - TODO list for implementation of this approach
	  
   III) Lump annealer embedding as composite of single gate annealer embeddings 
   	  - Notes and ideas on this approach
	  	- Manually composed embeddings from which general composition rules 
		  will be discerned
		- Rules for composing an embedding from smaller ones
		- Composing emeddings onto a Dwave-compatible graph
	  - TODO list for implementation of this approach

-----------------------------------------------------------------------------------------------------
(I) GATE CIRCUIT-TO-ANNEALER EMBEDDING BY WAY OF INTERMEDIATE LOGICAL TRUTH TABLE REPRESENTATION
-----------------------------------------------------------------------------------------------------

This approach will be unable to scale to any practical circuit as practical circuits often 
require upwards of 100 qubits. Clearly, solving a system of 2**100 inequalities is infeasible.
However, the classes and functions used to implement this approach are useful in the later parts
of this project, discussed in sections II and III.

The following describes how this approach generates a lump annealer embedding from a multi-gate 
circuit through an example of the XNOR function. 

File locations are described assuming the base directory is 
~/path/to/Lump-Annealer-Encoding-From-Gate-Circuit/logical/

1) Truthtable initialized in QuantumCircuit class based on the lengths of its QuantumRegisters. 
   Added to quantum circuit in converter/qiskit/_quantumcircuit.py. truthtable class implemented 
   in converter/qiskit/get_annealer_encoding.py

	from converter.qiskit import QuantumCircuit 
        from converter.qiskit import ClassicalRegister, QuantumRegister, 
	from converter.qiskit import execute

	qr0 = QuantumRegister(1)
	qr1 = QuantumRegister(1)
	cr0 = ClassicalRegister(1)
	cr1 = ClassicalRegister(1)
	
	qc = QuantumCircuit(qr0,qr1,cr0,cr1) ----.
	   .-------------------------------------'				  
	   |					 
	   '-->	In this case, when QuantumCircuit is called its truthtable
		attribute is initialized as follows:
			qc.truthtable.numinputs = 4 (2 for qr0 and 2 for qr1)			
			qc.truthtable.inputnames = ['q1_0','q0_0','q1_0_out','q0_0_out']
			qc.truthtable.inputtypes = ['Circ_Input','Circ_Input','Circ_Output','Circ_Output']
			qc.truthtable.outputs = numpy vector of length (2 ** truthtable.numinputs) 
						It is initialized with 1's in positions where input bits are
						equal to output bits in the graycode. The left half columns 
						are input bits and the right half columns are output bits.
			qc.truthtable.graycode = Gray code as a numpy array with (2 ** truthtable.numinputs) 
						rows and (truthtable.numinputs) columns. This is used in 
						routines that modify truthtable.output such as gate 
						functions and truthtable reduction. However, it is 
						inefficient and will be eliminated once better gate and 
						reduction routines are implemented

                                                                                           
                       'q0_0', 'Circ_Input' <-----.         .------> 'q1_0_out', 'Circ_Output'
                                                   \       /                                          
                       'q1_0', 'Circ_Input' <----.  \     /  .-----> 'q0_0_out', 'Circ_Output'
                                                  \  \   /  /
				               [[ 0  0  0  0 ]    1 
	        				[ 0  0  0  1 ]    0
					        [ 0  0  1  0 ]    0
			 		        [ 0  0  1  1 ]    0
                                                [ 0  1  0  0 ]    0
                                                [ 0  1  0  1 ]    1
 	truthtable.graycode as initialized -->  [ 0  1  1  0 ]    0  <-- values of truthtable.outputs  
						[ 0  1  1  1 ]    0      corresponding to gray code rows
                                                [ 1  0  0  0 ]    0
    					        [ 1  0  0  1 ]    0
						[ 1  0  1  0 ]    1
 				                [ 1  0  1  1 ]    0
                                                [ 1  1  0  0 ]    0 
						[ 1  1  0  1 ]    0
                                                [ 1  1  1  0 ]    0
						[ 1  1  1  1 ]]   1


2) Gate operations modify values truthtable.output. They are currently implemented in 
   converter/qiskit/extension/standard/x.py, cx.py. ccx.py, etc. but in the future, these scripts will just 
   serve to append the instruction to a list (specifically, QuantumCircuit.data) so that they can be carried 
   out after the truthtable is reduced.
	
        from converter.qiskit import QuantumCircuit
        from converter.qiskit import ClassicalRegister, QuantumRegister,
        from converter.qiskit import execute

	qr0 = QuantumRegister(1)
        qr1 = QuantumRegister(1)
        cr0 = ClassicalRegister(1)
        cr1 = ClassicalRegister(1)

        qc = QuantumCircuit(qr0,qr1,cr0,cr1)  
     
        qc.cx(qr0[0],qr1[0])--,
     .--qc.x(qr1[0])          |
     |        .---------------'                                    .----------> Target bit 'q1_0_out'
     |        '---> Before cx:                       After cx:    /  .--------> Control bit 'q0_0_out'
     |                                                           /  /
     |                 [[ 0  0  0  0 ]    1            [[ 0  0  0  0 ]    1
     |                  [ 0  0  0  1 ]    0             [ 0  0  0  1 ]    0    Positions of 1's in  
     |                  [ 0  0  1  0 ]    0             [ 0  0  1  0 ]    0    truthtable.output are changed
     |                  [ 0  0  1  1 ]    0             [ 0  0  1  1 ]    0    in positions where the 
     |                  [ 0  1  0  0 ]    0             [ 0  1  0  0 ]    0    control bit ('q0_0_out')
     |                  [ 0  1  0  1 ]    1 <---.       [ 0  1  0  1 ]    0    is one. They are moved to
     |                  [ 0  1  1  0 ]    0      \      [ 0  1  1  0 ]    0    positions where rows of
     |                  [ 0  1  1  1 ]    0       '---> [ 0  1  1  1 ]    1    truthtable.graycode are
     |                  [ 1  0  0  0 ]    0             [ 1  0  0  0 ]    0    identical in all bits except
     |                  [ 1  0  0  1 ]    0             [ 1  0  0  1 ]    0    the target bit ('q1_0_out').
     |                  [ 1  0  1  0 ]    1             [ 1  0  1  0 ]    1
     |                  [ 1  0  1  1 ]    0             [ 1  0  1  1 ]    0     
     |                  [ 1  1  0  0 ]    0             [ 1  1  0  0 ]    0     
     |                  [ 1  1  0  1 ]    0       .---> [ 1  1  0  1 ]    1
     |                  [ 1  1  1  0 ]    0      /      [ 1  1  1  0 ]    0
     |                  [ 1  1  1  1 ]]   1 <---'       [ 1  1  1  1 ]]   0
     |
     |
     '------------> Before x:                       After x:      ,-----------> Target bit 'q1_0_out'
                                                                 /  
                       [[ 0  0  0  0 ]    1 <---,      [[ 0  0  0  0 ]    0
                        [ 0  0  0  1 ]    0      \      [ 0  0  0  1 ]    0    Positions of 1's in  
                        [ 0  0  1  0 ]    0       '---> [ 0  0  1  0 ]    1    truthtable.output are changed
                        [ 0  0  1  1 ]    0             [ 0  0  1  1 ]    0    to positions where the 
                        [ 0  1  0  0 ]    0             [ 0  1  0  0 ]    0    rows of truthtable.graycode
                        [ 0  1  0  1 ]    0       ,---> [ 0  1  0  1 ]    1    identical except for 
                        [ 0  1  1  0 ]    0      /      [ 0  1  1  0 ]    0    the target bit ('q1_0_out').
                        [ 0  1  1  1 ]    1 <---'       [ 0  1  1  1 ]    0     
                        [ 1  0  0  0 ]    0       ,---> [ 1  0  0  0 ]    1    
                        [ 1  0  0  1 ]    0      /      [ 1  0  0  1 ]    0    Similar routines are
                        [ 1  0  1  0 ]    1 <---'       [ 1  0  1  0 ]    0    implemented for other gates
                        [ 1  0  1  1 ]    0             [ 1  0  1  1 ]    0    
                        [ 1  1  0  0 ]    0             [ 1  1  0  0 ]    0     
                        [ 1  1  0  1 ]    1 <---,       [ 1  1  0  1 ]    0
                        [ 1  1  1  0 ]    0      \      [ 1  1  1  0 ]    0
                        [ 1  1  1  1 ]]   0       '---> [ 1  1  1  1 ]]   1
     
     
3) Calling measure appends the measure instruction to a list (specifically, QuantumCircuit.data) so that it 
   can be known when execute() is called. This is necessary for determining which bits will be considered 
   ancillas and eliminated from the truthtable. ie any bit with type 'Circ_Output' that isn't measured will 
   be recast as type 'Ancilla' when execute is called.

        from converter.qiskit import QuantumCircuit
        from converter.qiskit import ClassicalRegister, QuantumRegister,
        from converter.qiskit import execute

        qr0 = QuantumRegister(1)
        qr1 = QuantumRegister(1)
        cr0 = ClassicalRegister(1)
        cr1 = ClassicalRegister(1)

        qc = QuantumCircuit(qr0,qr1,cr0,cr1)

        qc.cx(qr0[0],qr1[0])
        qc.x(qr1[0])
	
	qc.measure(qr1,cr1)  ---------------->  in converter/qiskit/_measure.py the only
                                                significant thing that happens is: 
                                                    
                                                                  qc.data.append('q1_0_out')

5) execute() is implemented in converter/qiskit/tools/_compiler.py. execute() first recasts bits not 
   measured as ancillas and reduces the truth table accordingly as mentioned above. reduce_truthtable() 
   is implemented as a class method of truthtable in converter/qiskit/get_annealer_encoding.py

        from converter.qiskit import QuantumCircuit
        from converter.qiskit import ClassicalRegister, QuantumRegister,
        from converter.qiskit import execute

        qr0 = QuantumRegister(1)
        qr1 = QuantumRegister(1)
        cr0 = ClassicalRegister(1)
        cr1 = ClassicalRegister(1)

        qc = QuantumCircuit(qr0,qr1,cr0,cr1)

        qc.cx(qr0[0],qr1[0])
        qc.x(qr1[0])
	
        qc.measure(qr1,cr1)

	execute(qc)

    'q0_0',
 'Circ_Input' <--.         .------> 'q1_0_out', 'Circ_Output'
                  \       /
   'q1_0', <----.  \     /   .----> 'q0_0_out', 'Ancilla' <-. 
 'Circ_Input'    \  \   /   /         .---------------------'  
               [[ 0  0  0  0 ]    0   '-> Type change                     .-------> 'q0_0', 'Circ_Input'
                [ 0  0  0  1 ]    0       so it can be                   / .------> 'q1_0', 'Circ_Input'
                [ 0  0  1  0 ]    1       identified in                 / / .-----> 'q1_0_out',
                [ 0  0  1  1 ]    0       reduce_truthtable()          / / /        'Circ_Output'
                [ 0  1  0  0 ]    0                                [[ 0 0 0 ]    0
                [ 0  1  0  1 ]    1                                 [ 0 0 1 ]    1
                [ 0  1  1  0 ]    0                                 [ 0 1 0 ]    1
                [ 0  1  1  1 ]    0                                 [ 0 1 1 ]    0
                [ 1  0  0  0 ]    1 ----- reduce_truthtable() ----> [ 1 0 0 ]    1 
                [ 1  0  0  1 ]    0                                 [ 1 0 1 ]    0
                [ 1  0  1  0 ]    0                                 [ 1 1 0 ]    0
                [ 1  0  1  1 ]    0                                 [ 1 1 1 ]]   1
                [ 1  1  0  0 ]    0
                [ 1  1  0  1 ]    0
                [ 1  1  1  0 ]    0
                [ 1  1  1  1 ]]   1

	If the ancilla bit to be removed is not in the least significant position elements of 
	truthtable.inputnames, truthtable.inputtypes, and truthtable.outputs are adjusted until it is. 
	Then, the reduced output is constructed from the old output.

6) Next in execute(), a system of inequalities in terms of annealer qubit and coupler weights are generated 
   from the truthtable

	         [[ 0 0 0 ]    0           system_inequalities = ['0 > G',
                  [ 0 0 1 ]    1                                  'w0 = G',
                  [ 0 1 0 ]    1                                  'w1 = G',
                  [ 0 1 1 ]    0                                  'w0 + w1 > G',
                  [ 1 0 0 ]    1                                  'w2 = G',
                  [ 1 0 1 ]    0                                  'w1 + w2 + J12 > G',
                  [ 1 1 0 ]    0                                  'w1 + w2 + J12 > G',
                  [ 1 1 1 ]]   1                                  'w0 + w1 + w2 + J01 + J02 + J12 = G'] 

    The system of inequalities is generated as a list of strings by the get_ineq_from_truthtable() function
    in converter/qiskit/get_annealer_encoding.py 

7) This list of inequalities is then passed to the solver. The solver works by extracting symbols and their 
   constraints from the equations, and iterating over the constraints to tighten the bounds of the 
   symbols. When bounds converge, a value is picked for the symbol having a constraint composed of the 
   least amount of unknown symbols and the tightest bounds. After a value is picked, the constraints of 
   all symbols are iterated over again and their bounds are tightened further. This is repeated until all 
   symbols have values.

   If a valid solution cannot be found, as in the case of the 3-bit XNOR truthtable above, an ancilla is 
   added. All 1's in the output are placed on ancilla 0's except for the last 1 in the output which is 
   placed on an ancilla 1. If the system still cannot be solved another ancilla is added, this time all 
   1's in the output are placed on ancilla 0's except for the second-to-last output 1 which is placed on 
   an ancilla 1. This can be continued until all output ones are on rows corresponding to 1's of different 
   ancillas.

   This works well for smaller systems of inequalities or simpler large systems of inequalities but does not 
   work on larger, more complicated systems yet. The solver still needs alot of work.
   
   Once the system is solved, qubit and coupler weights are reported:
		
		Annealer Encoding:
			J02 	 -364.5
			w0 	 831.3
			J23 	 141.8
			w3 	 -43.3
			w1 	 -43.3	
			G 	 -43.3
			J01 	 -517.9
			J12 	 120.3
			J03 	 -426.6
			J13 	 302.2
			w2 	 -43.3

		Check:
			True 	-	 0 > G
			True 	-	 w0 > G
			True 	-	 w1 = G
			True 	-	 w1 + J01 + w0 > G
			True 	-	 w2 = G
			True 	-	 w2 + J02 + w0 > G
			True 	-	 w2 + J12 + w1 > G
			True 	-	 w2 + J12 + J02 + w1 + J01 + w0 > G
			True 	-	 w3 = G
			True 	-	 w3 + J03 + w0 > G
			True 	-	 w3 + J13 + w1 > G
			True 	-	 w3 + J13 + J03 + w1 + J01 + w0 > G
			True 	-	 w3 + J23 + w2 > G
			True 	-	 w3 + J23 + J03 + w2 + J02 + w0 > G
			True 	-	 w3 + J23 + J13 + w2 + J12 + w1 > G
			True 	-	 w3 + J23 + J13 + J03 + w2 + J12 + J02 + w1 + J01 + w0 = G

		Ancillas added: 1

   Solver functions and classes are implemented in converter/qiskit/solve_sys_multivar_ineq.py

8) *Not yet implemented* After this general embedding is found, it will be adjusted to correspond to 
   actual Dwave connectivity 
 
9) *Not yet implemented* Last, a script which runs the found embedding on an annealer will be written by 
   execute().
   
TODO:
1) Get solver into a place where it can determine in one shot if system is solvable or not (hopefully in 
   correct implementation, disjoint bounds will be the indicator of an unsolvable system)

2) Truthtable attribute of QuantumCircuit class gets too massive for even moderately sized circuits
	- Find out how to do gate operations and truthtable reduction on output column without the crutch 
	  of the gray code
		- Investigate how fourier transform of output column changes under gate operations
	- Look into perrforming truthtable reduction before gate operations. As currently implemented,
	  gate operations take a long time on large truthtables
	- Find way to encode output bits position on bloch sphere

3) After system of inequalities are solved, adjust found embedding to represent actual Dwave connectivity 
	  
4) Write script in execute() that creates dwave script with the embedding that was found

5) Implement Fredkin and swap gates.

6) Add truthtable class method: randomly_permute_columns() because the column order needed for 
   reduce_truthtable() isn't necessarily the best one in when it comes to solving the 
   system of inequalities the truth table generates. 

-----------------------------------------------------------------------------------------------------
(II) BLOCH SPHERE TRUTH TABLE REPRESENTATION OF QUBIT
-----------------------------------------------------------------------------------------------------

Notes:

    File locations are described assuming the base directory is 
    ~/path/to/Lump-Annealer-Encoding-From-Gate-Circuit/blochsphere/
    
    Truth table could be used to represent position of qubit on Bloch sphere instead of representing
    a bits logical value which would allow implementation of Hadamard and phase gates. This would 
    result in massive truth tables and as such, the best approach would be to determine annealer 
    embeddings of single gates and from those, find a way to create a lump annealer embeddingas a 
    composite of these.
    
   	                   theta bits <---,-,     ,-,---> phi bits  
   	                                   \ \   / / 
   	theta = 0,      phi = 0          [[ 0 0 0 0 ]    1 <------ output vector = 1 to
	theta = 0,      phi = pi/2        [ 0 0 0 1 ]    0 <-,      indicate where a given bit is
	theta = 0,      phi = pi          [ 0 0 1 0 ]    0 <--,         
	theta = 0,	phi = 3*pi/2      [ 0 0 1 1 ]    0 <---,
	theta = pi/2,	phi = 0	          [ 0 1 0 0 ]    0      ,
	theta = pi/2,	phi = pi/2        [ 0 1 0 1 ]    0       ,       ,--------------
	theta = pi/2,	phi = pi          [ 0 1 1 0 ]    0        ,     | These rows don't
	theta = pi/2,	phi = 3*pi/2      [ 0 1 1 1 ]    0         ,    | correspond to 
	theta = pi,	phi = 0	          [ 1 0 0 0 ]    0          :---| anything so   
	theta = pi,	phi = pi/2        [ 1 0 0 1 ]    0 <-------'    | they will always
	theta = pi,	phi = pi          [ 1 0 1 0 ]    0 <------'     | be 0.         
	theta = pi,	phi = 3*pi/2      [ 1 0 1 1 ]    0 <-----'      | I guess that means 
	theta = 3*pi/2,	phi = 0	          [ 1 1 0 0 ]    0 <----'       | the truth table  
	theta = 3*pi/2,	phi = pi/2        [ 1 1 0 1 ]    0 <---'        | can be reduced to  
        theta = 3*pi/2, phi = pi          [ 1 1 1 0 ]    0 <--'         | 3 bits.      
	theta =	3*pi/2, phi = 3*pi/2      [ 1 1 1 1 ]]   0 <-'           '--------------
		                                                        
    Rows in truth table represent discrete points on the Bloch sphere and 
    the output vector indicates the position of a qubit
    
    The phi bits go from 0=2*pi (where all phi bits are 0) 
    to 2*pi-2*pi/(2**num_of_phi_bits) (where all phi bits are 1)
    Not having the row where all phi bits are 1 equal to 2*pi allows
    for there to be discrete points at phi = 0, pi and pi/2.
   
    Right now, I'm thinking the theta bits should represent the same discretization
    as phi. That is, theta is in the interval (0=2*pi, 2*pi/(2**num_of_theta_bits)).
    The reason is: Even though any position on the bloch sphere can be described
    by theta on the continous interval (0, pi), if theta is descritized by 
    a power of two, there will be nothing corresponding to the point
    theta = pi/2. 

    The size of the truth table can expand as finer resolution is needed.
    									
                                                    z
                                                    .
                                                   /|\ theta = [0 0]
                                                    |  phi   = [0 0]    
                                             ,,,-'''|'''-,,,            __,
                                         ,,''       |       '',,        ,'|
                                     ,,''           |           '',,  ,'
                                  ,''               |               '',
                                ,'                  |             ,'   ',
                               '                    |           ,'       '
                              /                     |         ,' <--------\------ theta = [0 1] 
                             ,                  ,,,,|----''';'''-.,        ,      phi =   [1 0] 
                            ,         ,,,,-'''''    |     ,'       ''.,     ,
                            ,    ..'''              |   ,'             '.,  ,
                      ,    , ,,''                   | ,'                  ', ,   ,
                    ,'_____,'_______________________|'______________________',____', y
                     ',    ,,                     ,'|                       ,,   ,'
             theta = [0 1]  ,'-                 ,'  |                   ,,'',  theta = [0 1] 
             phi   = [1 1]  ,  '.             ,'    |              ,,,''    ,  phi   = [0 1]  
                             ,   '',,       ,'      |    ,,,,,-''''         ,
                              \      ''-,,,;,,,,----|''''                  /
           theta = [0 1] ------',-----> ,'          |                    ,'
           phi   = [0 0]         ',   ,'            |                  ,'
                                   ','              |               ,,'
                                  ,' '',,           |           ,,''
                                ,'       '',,       |       ,,''
                             |,'             '''-,,,|,,,-'''
                             '--                    |
                            x                      \|/ theta = [1 0]
                                                    '  phi   = [0 0] 
    
    Annealer embeddings for single gates using crude 4-bit bloch sphere truth table representation 
    of qubit:
    
	Hadamard: 
	
		Hadamard gate is very inelegantly implemented in
		converter/qiskit/extensions/standard/h.py for the 4-bit Bloch sphere qubit
		representation shown above. I will change this once a better way to represent 
		a qubit is implemented.
		
		Right now it just changes the truthtable.outputs vector by mapping 
		a 1 on a given row to a different row as follows:
		        
	            'Circ_Input' 'Circ_Output'       'Circ_Input' 'Circ_Output'
			'q0_0'	  'q0_0_out'             'q0_0'    'q0_0_out'
                     t1 t0 p1 p0 t1 t0 p1 p0    H     t1 t0 p1 p0 t1 t0 p1 p0
                         	 0  0  0  0   ====>                0  1  0  0
                       		 0  1  0  0   ====>                0  0  0  0
                                 0  1  0  1   ====>                0  1  1  1
                                 0  1  1  0   ====>                1  0  0  0
                                 0  1  1  1   ====>                0  1  0  1 
                                 1  0  0  0   ====>                0  1  1  0 
			
			
		 	Input columns are blank because they can be anything and 
			the Hadamard operation does not affect them.
                                                                                               
		Running examples/Hadamard.py returns coupler and qubit weights for an annealer 
		Hadamard gate using a 4-bit discretization of the bloch sphere (assuming full 
		connectivity): 		
		
			J67 	 -47.3                                          
			J16 	 115.0			                
			w7 	 546.6                                                      
			J01 	 -246.7                                                           
			J25 	 342.3			                                           
			J02 	 -108.4
			w0 	 320.2
			J26 	 978.9
			J12 	 96.9
			J56 	 -514.3                 
			J36 	 -201.9
			J06 	 53.6
			J34 	 667.0
			J24 	 -499.6
			J35 	 -821.9
			w2 	 -747.1		        
			w3 	 627.7
			J17 	 -564.1
			w1 	 38.1	      
			J07 	 880.6
			J03 	 938.0
			w5 	 910.4
			J57 	 837.0
			w6 	 -747.1
			J14 	 -240.1
			w4 	 984.6
			J04 	 -48.2
			J05 	 -595.6
			J45 	 -379.6
			G 	 -747.1
			J47 	 708.5
			J15 	 547.5
			J46 	 -697.2
			J37 	 -312.2
			J13 	 651.5
			J27 	 -117.5
			J23 	 -548.1
			
		The above embedding is setup to run on a Dwave simulator in 
		examples/Hadamard_dwave.py
 	   					
	Z:
	
	Y:
	
	X:
	
	Controlled-X:
	
	Toffoli:
	
	Swap:
	
	Fredkin:

    Need 6 bit truth table representation of single qubit to do T gate
    
    	

TODO:

    1) Change reduce_truthtable() of truthtable class in
       blochsphere/converter/qiskit/get_annealer_encoding.py to work with Bloch sphere truthtable
    2) Think about how add_ancilla() of truthtable class in
       blochsphere/converter/qiskit/get_annealer_encoding.py needs to change if at all and change
       it if it does
    3) Implement gate operations for bloch sphere truth table representation of qubit

-----------------------------------------------------------------------------------------------------
(III) LUMP ANNEALER EMBEDDING AS COMPOSITE OF SINGLE GATE ANNEALER EMBEDDINGS
-----------------------------------------------------------------------------------------------------

File locations are described assuming the base directory is 
~/path/to/Lump-Annealer-Encoding-From-Gate-Circuit/composite/

Notes:
    Below are a number of different manually composed embeddings. From these, general rules for
    embedding composition will be discerned.
    
       i) Composing the below circuit from 2 identical XORS
	    #                                              
	    #                           a b c | out         
	    #     a --o------- a        0 0 0 | 0           
            #         |                 0 0 1 | 1           
            #         |out1             0 1 0 | 1           
            #     b --x----o-- b        0 1 1 | 0           
            #              |            1 0 0 | 1           
            #              |            1 0 1 | 0             
            #     c -------x-- out      1 1 0 | 0            
            #                           1 1 1 | 1 
            # XOR embedding:
            # 
            #             Ancilla         J01 = 3263.6        Output
            #           w0 = 500.0 O------------------------O w1 = 50.0            
            #                      |'.    J03 =           .'|                     
            #                      |  ''. -380.0       .''  |                     
            #                      |     ''.        .''     |                      
            #                      |        ''.  .''        |                       
            #          J02 =-300.0 |          .''.          | J13 = -100.0          
            #                      |       .''    ''.       |                      
            #                      |    .''J12 =     ''.    |                      
            #                      |,.''  -100.0        ''.,|                      
            #            w2 = 50.0 O------------------------O w3 = 50.0   
            #              Input          J23 = 80.0          Input    
	    #		  
	    #		              Ground State = 0
            # 
            # Combined embedding:
            # 
            #                                                 'out1' 
            #             Ancilla         J01 = 3263.6        Output
            #           w0 = 500.0 O------------------------O w1 = 100               
            #                      |'.    J03 =           .'|',                   
            #                      |  ''. -380.0       .''  |  '--------------.   
            #                      |     ''.        .''     |                 |    
            #                      |        ''.  .''        |                 |      
            #          J02 =-300.0 |          .''.          | J13 = -100.0    |      
            #                      |       .''    ''.       |                 |     
            #                      |    .''J12 =     ''.    |                 |         
            #            'a'       |,.''  -100.0        ''.,| 'b'             |     
            #            w2 = 50.0 O------------------------O w3 = 50.0       |
            #              Input           J23 = 80.0          Input          |
            #                                                                 |
            #                                                                 | 
            #                                                                 |
            #                                                                 |
            #                                                                 |
            #                                                'out'            | J16 = -100
            #            Ancilla         J45 = 3263.6        Output           |
            #          w4 = 500.0 O------------------------O w5 = 50.0        |   
            #                     |'.    J47 =           .'|                  |  
            #                     |  ''. -380.0       .''  |                  |  
            #                     |     ''.        .''     |                  |   
            #                     |        ''.  .''        |                  |    
            #         J46 =-300.0 |          .''.          | J57 = -100.0     |    
            #                     |       .''    ''.       |                  |   
            #                     |    .''J56 =     ''.    |                  |   
            #           'out1'    |,.''  -100.0        ''.,| 'c'              |   
            #           w6 = 100  O------------------------O w7 = 50.0        |
            #             Input   |      J67 = 80.0          Input            |
            #                     ',                                          |
            #                       '-----------------------------------------'
            #
	    # 			      Ground State = 0
	    #
	    #   manuallycomposed/two_identical_XORs.py
	    #
	    #-----------------------------------------------------------------------------------

      ii) Composing the below circuit from 2 different XORS
	    #                                              
	    #                           a b c | out         
	    #     a --o------- a        0 0 0 | 0           
            #         |                 0 0 1 | 1           
            #         |out1             0 1 0 | 1           
            #     b --x----o-- b        0 1 1 | 0           
            #              |            1 0 0 | 1           
            #              |            1 0 1 | 0             
            #     c -------x-- out      1 1 0 | 0            
            #                           1 1 1 | 1 
            # XOR embedding 1:
            #
            #                                                  'out1'
            #              Ancilla         J01 = 6141.6        Output
            #           w0 = 9534.0 O------------------------O w1 = 65.4        
            #                       |'.    J03 =           .'|                     
            #                       |  ''. -6708.1      .''  |                     
            #                       |     ''.        .''     |                      
            #                       |        ''.  .''        |                        
            #         J02 = -8974.5 |          .''.          | J13 = -2222.2          
            #                       |       .''    ''.       |                       
            #                       |    .''J12 =     ''.    |                           
            #            'a'        |,.''  -3474.2       ''.,| 'b'                    
            #           w2 = 3408.8 O------------------------O w3 = 2156.8      
            #             Input            J23 = 583.0         Input            
            #                                                                   
            #                          Ground State = 0                          
            #                                                                   
            #                                                                    
            # XOR embedding 2:                                                                  
            #                                                 'out'                      
            #             Ancilla         J45 = 3263.6        Output            
            #           w4 = 500.0 O------------------------O w5 = 50.0            
            #                      |'.    J47 =           .'|                     
            #                      |  ''. -380.0       .''  |                     
            #                      |     ''.        .''     |                      
            #                      |        ''.  .''        |                       
            #          J46 =-300.0 |          .''.          | J57 = -100.0          
            #                      |       .''    ''.       |                      
            #                      |    .''J56 =     ''.    |                      
            #            'out1'    |,.''  -100.0        ''.,| 'c'                  
            #            w6 = 50.0 O------------------------O w7 = 50.0         
            #              Input          J67 = 80.0          Input             
            #                                                                   
            #                            Ground State = 0  
            #
	    #
            # Combined embedding:           
            #                                                  'out1'
            #              Ancilla         J01 = 6141.6        Output
            #           w0 = 9534.0 O------------------------O w1 = 130.8            
            #                       |'.    J03 =           .'|',                   
            #                       |  ''. -6708.1      .''  |  '--------------.   
            #                       |     ''.        .''     |                 |     
            #                       |        ''.  .''        |                 |      
            #         J02 = -8974.5 |          .''.          | J13 = -2222.2   |      
            #                       |       .''    ''.       |                 |     
            #                       |    .''J12 =     ''.    |                 |         
            #           'a'         |,.''  -3474.2       ''.,| 'b'             |     
            #           w2 = 3408.8 O------------------------O w3 = 2156.8     |
            #             Input            J23 = 583.0         Input           |
            #                                                                  |
            #                                                                  | 
            #                                                                  |
            #                                                                  |
            #                                                                  |
            #                                                 'out'            | J16 = -115.4
            #             Ancilla         J45 = 3263.6        Output           |                
            #           w4 = 500.0 O------------------------O w5 = 50.0        |   
            #                      |'.    J47 =           .'|                  |  
            #                      |  ''. -380.0       .''  |                  |  
            #                      |     ''.        .''     |                  |   
            #                      |        ''.  .''        |                  |     
            #          J46 =-300.0 |          .''.          | J57 = -100.0     |    
            #                      |       .''    ''.       |                  |   
            #                      |    .''J56 =     ''.    |                  |   
            #            'out1'    |,.''  -100.0        ''.,| 'c'              |   
            #            w6 = 100  O------------------------O w7 = 50.0        |
            #              Input   |    J67 = 80.0          Input              |
            #                      ',                                          |
            #                        '-----------------------------------------'
            #                             
	    #                            Ground State = 0
	    #
	    #   manuallycomposed/two_different_XORs.py
	    #
            #---------------------------------------------------------------------------------

     iii) Composing XNOR from XOR and NOT	
	    #
            #                             XOR Embedding                         NOT Embedding
	    #                            ---------------                       --------------- 
            # 
            #             Ancilla         J01 = 3263.6        Output                Input
            #           w0 = 500.0 O------------------------O w1 = 50.0           O w4 =-50.0            
            #                      |'.    J03 =           .'|                     |
            #                      |  ''. -380.0       .''  |                     |
            #                      |     ''.        .''     |                     | 
            #                      |        ''.  .''        |                     |  
            #          J02 =-300.0 |          .''.          | J13 = -100.0        | J45 = 500
            #                      |       .''    ''.       |                     | 
            #                      |    .''J12 =     ''.    |                     | 
            #                      |,.''  -100.0        ''.,|                     | Output
            #            w2 = 50.0 O------------------------O w3 = 50.0           O w5 = -50.0
            #              Input          J23 = 80.0          Input    
	    #		  
	    #		              Ground State = 0                       Ground State = -50
	    #
	    #                                            XNOR Embedding
	    #                                           ----------------
	    #
	    #                                                     J14 = -100.0
	    #                                                ,-------------------.
            #             Ancilla         J01 = 3263.6      | Ancilla             | Ancilla
            #           w0 = 500.0 O------------------------O,w1 = 50.0           O w4 =-50.0            
            #                      |'.    J03 =           .'| ',                  |
            #                      |  ''. -380.0       .''  |   ',                |
            #                      |     ''.        .''     |     '',, J15 =      | 
            #                      |        ''.  .''        |         '', 500.0   |  
            #          J02 =-300.0 |          .''.          | J13 =      ',       | J45 = 500
            #                      |       .''    ''.       | -100.0       ',     | 
            #                      |    .''J12 =     ''.    |                ',   | 
            #                      |,.''  -100.0        ''.,|                  ', | Output
            #            w2 = 50.0 O------------------------O w3 = 50.0          'O w5 = -150.0
            #              Input          J23 = 80.0          Input    
	    #		  
	    #		                               Ground State = -150
	    #
	    #                                    - OR - (better)
	    #
	    #                                                     J14 = -50.0
	    #                                                ,-------------------.
            #             Ancilla         J01 = 3263.6      | Ancilla             | Ancilla
            #           w0 = 500.0 O------------------------O w1 = 75.0           O w4 = -25.0            
            #                      |'.    J03 =           .'|                     |
            #                      |  ''. -380.0       .''  |                     |
            #                      |     ''.        .''     |                     | 
            #                      |        ''.  .''        |                     |  
            #          J02 =-300.0 |          .''.          | J13 =               | J45 = 500
            #                      |       .''    ''.       | -100.0              | 
            #                      |    .''J12 =     ''.    |                     | 
            #                      |,.''  -100.0        ''.,|                     | Output
            #            w2 = 50.0 O------------------------O w3 = 50.0           O w5 = 50.0
            #              Input          J23 = 80.0          Input    
	    #		  
	    #		                               Ground State = -50
	    #   
	    #   manuallycomposed/XORandNOT.py
	    #
	    #-------------------------------------------------------------------------------------
	    
      iv) Composing an adder sum function from identical XORs
	    #
	    # a --o-------------- a        a b c | S       
	    #     |                       -------|---     
	    #     |                        0 0 0 | 0        
	    # b --|-----o-------- b        0 0 1 | 1               
	    #     |     |                  0 1 0 | 1               
	    #     |     |                  0 1 1 | 0             
	    # c --|-----|-----o-- c        1 0 0 | 1
	    #     |     |     |            1 0 1 | 0
	    #     |out1 |out2 |            1 1 0 | 0
	    # i --x-----x-----x-- S        1 1 1 | 1
	    #                             (for i = 0)
	    #  XOR embedding:
	    # 
            #             Ancilla        J0,1 = 3263.6        Output
            #           w0 = 500.0 O------------------------O w1 = 50.0            
            #                      |'.   J0,3 =           .'|                     
            #                      |  ''. -380.0       .''  |                     
            #                      |     ''.        .''     |                      
            #                      |        ''.  .''        |                       
            #         J0,2 =-300.0 |          .''.          | J1,3 = -100.0          
            #                      |       .''    ''.       |                      
            #                      |    .''J1,2 =    ''.    |                      
            #                      |,.''  -100.0        ''.,|                      
            #            w2 = 50.0 O------------------------O w3 = 50.0   
            #              Input          J2,3 = 80.0         Input    
	    #		  
	    #		              Ground State = 0
	    #
	    # Combined embedding:
	    #                                                 'out1'
	    #             Ancilla         J0,1 = 3263.6       Output
            #           w0 = 500.0 O------------------------O,w1 = 100.0         
            #                      |'.   J0,3 =           .'| '',,            
            #                      |  ''. -380.0       .''  |     '',,            
            #                      |     ''.        .''     |         '',,         
            #                      |        ''.  .''        |             '',       
            #         J0,2 =-300.0 |          .''.          | J1,3 = -100.0  |      
            #                      |       .''    ''.       |                |     
            #                      |    .''J1,2 =    ''.    |                |     
            #            'a'       |,.''  -100.0        ''.,| 'i'            |     
            #            w2 = 50.0 O------------------------O w3 = 50.0      |
            #              Input          J2,3 = 80.0         Input          |
	    #                                                                |
	    #                                                 'out2'         | J1,7 = -100.0
	    #             Ancilla         J4,5= 3263.6        Output         |
            #           w4 = 500.0 O------------------------O,w5 = 100.0     |     
            #                      |'.    J4,7 =          .'| ',             |    
            #                      |  ''. -380.0       .''  |   ',           |    
            #                      |     ''.        .''     |     ',         |     
            #                      |        ''.  .''        |       ',       |      
            #         J4,6 =-300.0 |          .''.          | J5,7 =  ',  ,,'       
            #                      |       .''    ''.       | -100.0  ,,';         
            #                      |    .''J5,6 =    ''.    |     ,,''    ',                
            #            'b'       |,.''  -100.0        ''.,| ,,''          ',      
            #            w6 = 50.0 O------------------------O' 'out1'        |
            #              Input         J6,7 = 80.0          w7 = 100.0     |
	    #                                                 Input          |
	    #                                                                |
	    #                                                 'S'            |
	    #             Ancilla        J8,9 = 3263.6        Output         | J5,11 = -100.0
            #           w8 = 500.0 O------------------------O w9 = 50.0      |      
            #                      |'.   J8,11 =          .'|                |     
            #                      |  ''. -380.0       .''  |                |     
            #                      |     ''.        .''     |                |      
            #                      |        ''.  .''        |                |       
            #         J8,10=-300.0 |          .''.          | J9,11 =     ,,'    
            #                      |       .''    ''.       | -100.0  ,,''             
            #                      |    .''J9,10 =   ''.    |     ,,''                 
            #            'c'       |,.''  -100.0        ''.,| ,,''              
            #            w10= 50.0 O------------------------O' 'out2'   
            #              Input         J10,11 = 80.0          w11 = 100.0
	    #		                                        Input
            #
	    #                           Ground State = 0
	    #
	    #   manuallycomposed/adder_sum.py
	    #
	    #--------------------------------------------------------------------------
	    
       v) Composing an adder carry function from identical Toffoli embeddings
	    #                                               
            # x --o-----------o----- x      x y z | C       
	    #     |           |            -------|---      
	    #     |           |             0 0 0 | 0       
	    # y --o-----o-----|----- y      0 0 1 | 0       
	    #     |     |     |             0 1 0 | 0       
	    #     |     |     |             0 1 1 | 1       
	    # z --|-----o-----o----- z      1 0 0 | 0       
	    #     |     |     |             1 0 1 | 1       
	    #     |out1 |out2 |             1 1 0 | 1    
	    # i --x-----x-----x----- C      1 1 1 | 1                
	    #                              (for i = 0)
	    # Toffoli embedding:
	    #
	    #                                Ancilla
	    #                               w0 = 8463.2 
	    #    ,-----------------------------,o,----------------------------,
	    #    |         J0,1 = 8625.9 ,,,'''   ''',,,J0,2 = -9566.3        |
	    #    |                    ,'                ',                    |
            #    |        Output    ,'   J1,2 = -8244.1   ',  Input (target)  |
            #    |     w1 = 1930.2 O------------------------O w2 = 6313.9     |    
            #    |                 |'. J1,4 =             .'|                 |   
            #    |J0,3 =           |  ''. -1926.5      .''  |                 |J0,4 =   
            #    | -1503.0         |     ''.        .''     |                 | -5659.2   
            #    |                 |        ''.  .''        |                 |     
            #    |    J1,3 = -14.3 |          .''.          | J2,4 = 1926.5   |     
            #    '---,             |       .''    ''.       |             ,---'
            #         ''',,,       |    .''J2,3 =    ''.    |       ,,,'''         
            #               ''',,, |,.''   14.3         ''.,| ,,,'''           
            #            w3 = 0   'O------------------------O'w4 = 0      
            #         Input (control)    J3,4 = 10.6      Input (control)
	    #		  
	    #		              Ground State = 0
            # 
	    #   
	    # Combined embedding:
	    #                                                  J1,7 = -8244.1
	    #                   ,-----------------------------------------------------------------,
	    #                  |                     Ancilla                                      |
	    #                  |                    w0 = 8463.2                                   |
	    #            ,-----|-----------------------,o,----------------------------,           |
	    #            |     |   J0,1 = 8625.9 ,,,'''   ''',,,J0,2 = -9566.3        |           |
	    #            |     '-------,      ,'                ',                    |           |
            #            |     'out1'   ',  ,'   J1,2 = -8244.1   ',      'i'         |           |
            #            |     w1 = 3860.4'O------------------------O w2 = 6313.9     |           |
            #            |                 |'. J1,4 =             .'|                 |           |
            #            |J0,3 =           |  ''. -1926.5      .''  |                 |J0,4 =     |
            #            | -1503.0         |     ''.        .''     |                 | -5659.2   |
            #            |                 |        ''.  .''        |                 |           |
            #            |    J1,3 = -14.3 |          .''.          | J2,4 = 1926.5   |           |
            #            '---,             |       .''    ''.       |             ,---'           |
            #                 ''',,,       |    .''J2,3 =    ''.    |       ,,,'''                |
            #                       ''',,, |,.''   14.3         ''.,| ,,,'''                      |
            #                    w3 = 10  'O------------------------O'w4 = 10                     |
            #                     'x'    ,'       J3,4 = 10.6       |  'y'                        |
	    #      J3,13 = -20         ,'                          ,'                             | 
	    #  ,----------------------'    J4,8 = -20            ,'                               |
	    # |     ,-------------------------------------------'                                 |
	    # |    |                                                                              | 
	    # |    |                                          J6,12 = -8244.1                     |
	    # |    |            ,-----------------------------------------------------------------|--.
	    # |    |           |                     Ancilla                                      |  |
	    # |    |           |                    w5 = 8463.2                                   |  |
	    # |    |     ,-----|-----------------------,o,----------------------------,           |  |
	    # |    |     |     |   J5,6 = 8625.9 ,,,'''   ''',,,J5,7 = -9566.3        |           |  |
	    # |    |     |     '-------,      ,'                ',        ,,----------|-----------'  |
            # |    |     |     'out2'   ',  ,'   J1,2 = -8244.1   ',  ,,''            |              |
            # |    |     |     w6 = 3860.4'O------------------------O'w7 = -12627.8   |              |
            # |    |     |                 |'. J6,9 =             .'|      'out1'     |              |
            # |    |     |J5,8 =           |  ''. -1926.5      .''  |                 |J5,9 =        |
            # |    |     | -1503.0         |     ''.        .''     |                 | -5659.2      |
            # |    |     |                 |        ''.  .''        |                 |              |
            # |    |     |    J6,8 = -14.3 |          .''.          | J7,9 = 1926.5   |              | 
            # |    |     '---,             |       .''    ''.       |             ,---'              |
            # |    |          ''',,,       |    .''J7,8 =    ''.    |       ,,,'''                   |
            # |    |                ''',,, |,.''   14.3         ''.,| ,,,'''                         |
            # |    |             w8 = 10  'O------------------------O'w9 = 10                        |
            # |    |               'y'     |      J8,9 = 10.6       |  'z'                           | 
	    # |    |                      ,'                        ',                               |
	    # |    |                    ,'                            ',    J9,14 = -20              | 
	    # |     '------------------'                                '------------------,         |
	    # |                                      Ancilla                                ',       |
	    # |                                    w10 = 8463.2                               ',     |
	    # |          ,-----------------------------,o,----------------------------,         ',   |
	    # |          |       J10,11 = 8625.9 ,,,'''   ''',,,J10,12 = -9566.3      |          |   |
	    # |          |                    ,'                ',        ,,----------|----------|--'
            # |          |        'C'       ,'   J1,2 = -8244.1   ',  ,,''            |          |
            # |          |    w11 = 1930.2 O------------------------O'w12 = -12627.8  |          |
            # |          |                 |'. J11,14 =           .'|       'out2'    |          | 
            # |          |J10,13 =         |  ''. -1926.5      .''  |                 |J10,14 =  | 
            # |          | -1503.0         |     ''.        .''     |                 | -5659.2  | 
            # |          |                 |        ''.  .''        |                 |          |
            # |          |       J11,13 =  |          .''.          | J12,14 =        |          |
            # |          '---,       -14.3 |       .''    ''.       |  1926.5     ,---'          |
            # |               ''',,,       |    .''J12,13 =  ''.    |       ,,,'''               |
            # |                     ''',,, |,.''   14.3         ''.,| ,,,'''                     |
            # |                  w13 = 10 'O------------------------O'w14 = 10                   |
            # |                     'x'    |    J13,14 = 10.6       |   'z'                      | 
            #  '--------------------------'                          '--------------------------'    
	    #
	    #                                Ground State = 0
            #
            #   manuallycomposed/adder_carry.py
	    #
	    #-------------------------------------------------------------------------------------------


      vi) Composing an identity function from 2 NOTS
            #
	    # NOT embedding: 
	    #
            #          Input
            #        O w0 = -50.0            
            #        |
            #        |
            #        | 
            #        |  
            #        | J01 = 500
            #        | 
            #        | 
            #        | Output
            #        O w1 = -50.0
            #                                                          
	    #    Ground State = -50.0
	    #
            #
	    # Identity embedding: 
	    #
            #          Input                              Input
            #        O w0 = -25.0                      ,O w2 = -20.0
            #        |                             ,,'' |
            #        |                         ,,''     |
            #        | J01 = 500           ,,''         |
            #        |                 ,,''             |
            #        |             ,,'' J12 = -10.0     | J23 = 500
            #        |         ,,''                     |
            #        |     ,,''                         |
            #        | ,,''                             |       
            #        O'w1 = -20.0                       O w3 = -25.0
            #          Output                             Output
	    #
	    #                   Ground State = -50.0
	    #
	    #                        -OR-
	    #
            #          Input                              Input
            #        O w0 = -50.0                      ,O w2 = -25.0
            #        |                             ,,'' |
            #        |                         ,,''     |
            #        | J01 = 500           ,,''         |
            #        |                 ,,''             |
            #        |             ,,'' J12 = -50.0     | J23 = 500
            #        |         ,,''                     |
            #        |     ,,''                         |
            #        | ,,''                             |       
            #        O'w1 = -25.0                       O w3 = -50.0
            #          Output                             Output
	    #
	    #                   Ground State = -100.0
	    #
	    #   manuallycomposed/identity.py
	    #
	    #------------------------------------------------------------------------------------

    Rules for composing embeddings:
	To join two qubits together (say, q1 and q2), add a positive offset to each of their weights 
	(w1_new = w1_old + d1, w2_new = w2_old + d2) and set the coupler weight between them equal to 
	the sum of the negatives of the offsets (J1,2 = -d1 - d2).
	    ==> The offsets which can be added may be bounded by the rest of the embedding
	        but I haven't ran into this yet.
		
    Composing embeddings on a Dwave-compatible graph:
    	Once the embedding is for the gate circuit is found as above, the qubits can be mapped
	to qubits having identical connectivity on the dwave graph.
	If identical connectivity is not available for a given qubit, its connectivity can be 
	extended by joining the annealer qubit with another in the same way qubits are joined 
	when composing embeddings
    	
    
    
TODO:

   1) Figure out scheme to simplify annealer embedding graphs
   2) Implement to work in Qiskit class structure:
   	- graph composition
	- graph simplification/reduction
	- qubit splitting so it will work on Dwave hardware
```
