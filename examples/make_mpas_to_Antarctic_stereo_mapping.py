#!/usr/bin/env python
# This software is open source software available under the BSD-3 license.
#
# Copyright (c) 2019 Triad National Security, LLC. All rights reserved.
# Copyright (c) 2019 Lawrence Livermore National Security, LLC. All rights
# reserved.
# Copyright (c) 2019 UT-Battelle, LLC. All rights reserved.
#
# Additional copyright and license information can be found in the LICENSE file
# distributed with this code, or at
# https://raw.githubusercontent.com/MPAS-Dev/MPAS-Analysis/master/LICENSE

'''
Creates a mapping file that can be used with ncremap (NCO) to remap MPAS files
to a latitude/longitude grid.

Usage: Copy this script into the main MPAS-Analysis directory (up one level).
Modify the grid name, the path to the MPAS grid file and the output grid
resolution.
'''

import xarray

from pyremap import MpasMeshDescriptor, Remapper, get_polar_descriptor


# replace with the MPAS mesh name
inGridName = 'oQU240'

# replace with the path to the desired mesh or restart file
# As an example, use:
# https://web.lcrc.anl.gov/public/e3sm/inputdata/ocn/mpas-o/oQU240/ocean.QU.240km.151209.nc
inGridFileName = 'ocean.QU.240km.151209.nc'

inDescriptor = MpasMeshDescriptor(inGridFileName, inGridName)

# modify the size and resolution of the Antarctic grid as desired
outDescriptor = get_polar_descriptor(Lx=6000., Ly=6000., dx=10., dy=10.,
                                     projection='antarctic')
outGridName = outDescriptor.meshName

mappingFileName = 'map_{}_to_{}_conserve.nc'.format(inGridName, outGridName)

remapper = Remapper(inDescriptor, outDescriptor, mappingFileName)

# conservative remapping with 4 MPI tasks (using mpirun)
remapper.build_mapping_file(method='conserve', mpiTasks=4)

outFileName = 'temp_{}.nc'.format(outGridName)
ds = xarray.open_dataset(inGridFileName)
dsOut = xarray.Dataset()
dsOut['temperature'] = ds['temperature']
dsOut = remapper.remap(dsOut)
dsOut.to_netcdf(outFileName)
