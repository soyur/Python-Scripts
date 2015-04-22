'''
Purpose:    Download compressed Lidar (.laz) from NOAA Digital Coast ftp and convert to raster grids (.tif)
            Visit http://coast.noaa.gov/htdata/lidar1_z/geoid12a/data/

Requirements:   Python 2.7+ for LAZ download *Can be used on its own, just comment out the rest
                LAStools-LAS2LAS for LAZ to LAS conversion, download for free @ http://rapidlasso.com/lastools/
                ArcGIS-ArcPY for LAS to LASD to DEM conversion, LAStools can do this if you have only a few files or if you buy a license

Author: Sawyer Stippa, USGS
email: sstippa@usgs.gov
date: 2/26/15
'''

import os, time, subprocess, arcpy
from ftplib import FTP
start = time.clock()

lcPath = r'H:/PostSandy_2012/USACE_MA_RI'  # Path to local folder,
ftpSite = 'ftp.coast.noaa.gov'  # ftp site for lidar, shouldn't need to be changed
ftpDir = 'pub/DigitalCoast/lidar1_z/geoid12a/data/1434/'  # Lidar directory *Depends on area of interest, see link in purpose
las2las_path = "C:/LAStools/bin/las2las.exe"  # full path to the las2las executable
# if creating multiple LASD's, strip name for DEM if over 13 char !!!!!!!

##################### Check paths

folders = ['FTP','LAS','LASD','DEM']
for folder in folders:
    if os.path.isdir(lcPath+'/'+ folder) == True:
        print "%s folder ok" %folder
    else:
        os.mkdir(lcPath+'/'+ folder)
        print "%s folder created" %folder

##################### Download files from NOAA ftp

startDownload = time.clock()
ftp = FTP(ftpSite)  # connect to host, default port
ftp.login()  # user anonymous, passwd anonymous@
ftp.cwd(ftpDir)  # change ftp directory
for filename in ftp.nlst('*.*'):  # list directory contents
    if os.path.exists(lcPath+'/FTP/'+filename) == True:
        print "skipping, file already exists"
    else:
        file = open(lcPath+'/FTP/'+filename, 'wb')  # prep file to download
        print 'Downloading ' + filename
        ftp.retrbinary('RETR %s' %filename,file.write)  # retrieving file
        file.close()

ftp.quit()
endDownload = time.clock()
duration = endDownload - startDownload
hours, remainder = divmod(duration, 3600)
minutes, seconds = divmod(remainder, 60)
print "Download completed in %dh:%dm:%fs" % (hours, minutes, seconds)

################### Create file list of laz's

included_extenstions = ['laz']
filenames = [fn for fn in os.listdir(lcPath+'/FTP') if any([fn.endswith(ext) for ext in included_extenstions])]
lazListName = 'file_list.txt'
laz_list = open(lcPath+'/FTP/'+lazListName,'wb')
print "Creating list of LAZs"
for filename in filenames:
    string = '%s/FTP/%s\n' %(lcPath, filename)
    laz_list.write(string)
laz_list.close()
print "List file created"

###################### Convert all LAZ to LAS

if os.path.exists(las2las_path) == True:  # Double Checking for las2las.exe tool
    start2las = time.clock()
    print "las2las tool ok"
    ### Create command for las2las conversion
    command = ['"'+las2las_path+'"']  # create the command string for las2las.exe
    command.append("-lof")  # add list of files
    lazList = lcPath+'/FTP/'+lazListName
    command.append('"'+lazList+'"')  # List of laz files
    command.append("-cores")
    command.append("16")  # Number of cores to use - can be adjusted to more or less
    command.append("-odir")
    lasOut = lcPath+'/'+'LAS'  # output dir
    command.append('"'+lasOut+'"')
    command.append("-olas")  # to convert to las

    ### report command string
    print "LAStools command line:"
    command_length = len(command)
    command_string = str(command[0])
    command[0] = command[0].strip('"')
    for i in range(1, command_length):
        command_string = command_string + " " + str(command[i])
        command[i] = command[i].strip('"')
    print command_string

    print "Converting files to las"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)  # LAZ to LAZ conversion
    print process.communicate()
    print process.poll()
    print "Conversion Complete"
    end2las = time.clock()
    duration = end2las - start2las
    hours, remainder = divmod(duration, 3600)
    minutes, seconds = divmod(remainder, 60)
    print "LAS conversion completed in %dh:%dm:%fs" % (hours, minutes, seconds)
else:
    print "error: las2las tool doesn't exist or is in the wrong place"

###################### Convert LAS to LASD to DEM (tiff)

start2dem = time.clock()
arcpy.env.workspace = lcPath + '/LAS'  # LAS folder

lasdPath = lcPath + '/LASD/lidar.lasd'
print "Converting to LASD"
arcpy.CreateLasDataset_management(lcPath+'/LAS', lasdPath, "", "", arcpy.SpatialReference("WGS 1984 UTM Zone 18N"))  # Create Lidar Dataset (.lasd)
demPath = lcPath + '/DEM/dem.tif'  # dem file
print "Converting to TIFF"
arcpy.LasDatasetToRaster_conversion(lasdPath,  # Path to LASD
                                    demPath,  # Path to DEM
                                    "ELEVATION",  # Value field
                                    'TRIANGULATION LINEAR NO_THINNING MAXIMUM 1',  # Interpolation method/Point thinning type/Point selection method/resolution
                                    "FLOAT",  # Data type
                                    "CELLSIZE",  # Sampling type
                                    1,  # Sampling value - resolution of output raster
                                    1  # Z factor
                                    )

# Create separate LASDs and DEMs if LAS coverage is not continuous. Change DEM naming convention according to LAS filenames
# lasList = arcpy.ListFiles('*.las') # LAS list
# count = 1
# for las in lasList:
#     total = len(lasList)
#     lasPath = lcPath + '/LAS/' + las #las file
#     lasd = las.strip('.las') + '.lasd' #lasd name
#     lasdPath = lcPath + '/LASD/' + lasd # lasd file
#     try:
#         arcpy.CreateLasDataset_management(lasPath,lasdPath,"","",arcpy.SpatialReference("WGS 1984 UTM Zone 18N")) # Create Lidar Dataset (.lasd)
#         DEM = lasd.strip('.lasd') + '.tif'
#     #DEM = lasd.split('_md_va18')[1].strip('.lasd') + '.tif'
#     #DEM = lasd.strip('.lasd') + '.tif'
#     #DEM = lasd.strip('_GeoClassified.las').split('PostSandy_')[1] + '.tif' # dem name
#         demPath = lcPath + '/DEM/' + DEM # dem file
#         arcpy.LasDatasetToRaster_conversion(lasdPath,demPath,"ELEVATION",'TRIANGULATION LINEAR NO_THINNING MAXIMUM 1',"FLOAT","CELLSIZE",1,1) # Create dem from Lidar Dataset
#         print "%s/%s complete" %(count,total)
#     except:
#         print "skipping %s" %lasd
#     count+=1


end2dem = time.clock()
duration = end2dem - start2dem
hours, remainder = divmod(duration, 3600)
minutes, seconds = divmod(remainder, 60)
print "DEM conversion completed in %dh:%dm:%fs" % (hours, minutes, seconds)

end = time.clock()
duration = end - start
hours, remainder = divmod(duration, 3600)
minutes, seconds = divmod(remainder, 60)
print "Process completed in %dh:%dm:%fs" % (hours, minutes, seconds)
