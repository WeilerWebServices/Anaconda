"""Small but quite comprehensive example showing the use of PyTables.

The program creates an output file, 'tutorial1.h5'.  You can view it
with any HDF5 generic utility.

"""

from numpy import *
from tables import *


        #'-**-**-**-**-**-**- user record definition  -**-**-**-**-**-**-**-'

# Define a user record to characterize some kind of particles
class Particle(IsDescription):
    name      = StringCol(16)   # 16-character String
    idnumber  = Int64Col()      # Signed 64-bit integer
    ADCcount  = UInt16Col()     # Unsigned short integer
    TDCcount  = UInt8Col()      # unsigned byte
    grid_i    = Int32Col()      # integer
    grid_j    = Int32Col()      # integer
    pressure  = Float32Col()    # float  (single-precision)
    energy    = Float64Col()    # double (double-precision)

print
print   '-**-**-**-**-**-**- file creation  -**-**-**-**-**-**-**-'

# The name of our HDF5 filename
filename = "tutorial1.h5"

print "Creating file:", filename

# Open a file in "w"rite mode
h5file = openFile(filename, mode = "w", title = "Test file")

print
print   '-**-**-**-**-**- group and table creation  -**-**-**-**-**-**-**-'

# Create a new group under "/" (root)
group = h5file.createGroup("/", 'detector', 'Detector information')
print "Group '/detector' created"

# Create one table on it
table = h5file.createTable(group, 'readout', Particle, "Readout example")
print "Table '/detector/readout' created"

# Print the file
print h5file
print
print repr(h5file)

# Get a shortcut to the record object in table
particle = table.row

# Fill the table with 10 particles
for i in xrange(10):
    particle['name']  = 'Particle: %6d' % (i)
    particle['TDCcount'] = i % 256
    particle['ADCcount'] = (i * 256) % (1 << 16)
    particle['grid_i'] = i
    particle['grid_j'] = 10 - i
    particle['pressure'] = float(i*i)
    particle['energy'] = float(particle['pressure'] ** 4)
    particle['idnumber'] = i * (2 ** 34)
    particle.append()

# Flush the buffers for table
table.flush()

print
print   '-**-**-**-**-**-**- table data reading & selection  -**-**-**-**-**-'

# Read actual data from table. We are interested in collecting pressure values
# on entries where TDCcount field is greater than 3 and pressure less than 50
pressure = [ x['pressure'] for x in table.iterrows()
             if x['TDCcount'] > 3 and 20 <= x['pressure'] < 50 ]
print "Last record read:"
print repr(x)
print "Field pressure elements satisfying the cuts:"
print repr(pressure)

# Read also the names with the same cuts
names = [ x['name'] for x in table.where(
    """(TDCcount > 3) & (20 <= pressure) & (pressure < 50)""" ) ]
print "Field names elements satisfying the cuts:"
print repr(names)

print
print   '-**-**-**-**-**-**- array object creation  -**-**-**-**-**-**-**-'

print "Creating a new group called '/columns' to hold new arrays"
gcolumns = h5file.createGroup(h5file.root, "columns", "Pressure and Name")

print "Creating an array called 'pressure' under '/columns' group"
h5file.createArray(gcolumns, 'pressure', array(pressure),
                   "Pressure column selection")
print repr(h5file.root.columns.pressure)

print "Creating another array called 'name' under '/columns' group"
h5file.createArray(gcolumns, 'name', names, "Name column selection")
print repr(h5file.root.columns.name)

print "HDF5 file:"
print h5file

# Close the file
h5file.close()
print "File '"+filename+"' created"