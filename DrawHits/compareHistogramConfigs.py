import sys,os
import subprocess
import csv

allFiles = { }
allDirs = set()
#
# loop over directories with text files
#
for d in sys.argv[1:]:
    #
    # assume last part of directory name is unique
    #
    dn = os.path.basename(os.path.normpath(d))
    assert not dn in allDirs
    allDirs.add(dn)
    #
    # retrieve cksums for all text files
    #
    filePattern = os.path.join(d,"*.txt")
    result = subprocess.run("cksum "+filePattern, text=True, capture_output=True, shell=True)
    result.check_returncode()
    #
    # loop over output
    #
    for l in result.stdout.split(chr(10)):
        if l=="":
            continue
        #
        # decode output line
        #
        fields = l.split()
        assert len(fields)==3
        cksum = int(fields[0])
        size = int(fields[1])
        name = os.path.splitext(os.path.basename(fields[2]))[0]
        #
        # store result by name ( directory, cksum, and size )
        #
        if not name in allFiles:
            allFiles[name] = [ ( dn, cksum, size ) ]
        else:
            allFiles[name].append( ( dn, cksum, size ) )
#
allDirs = sorted(allDirs)
#
# write result to output file
#
with open("compareHistogramConfigs.csv","wt") as csvFile:
    csvwriter = csv.writer(csvFile)
    # header row 1
    row = [ "Name" ]
    for d in allDirs:
        row.extend([ d, "", "" ])
    row.append("#ids")
    row.append("#dirs")
    csvwriter.writerow(row)
    # header row 2
    row = [ "" ]
    for d in allDirs:
        row.extend([ "size", "cksum", "id" ])
    row.append("")
    row.append("")
    csvwriter.writerow(row)
    #
    # loop over all definitions
    #
    for n in sorted(allFiles.keys()):
        #
        row = [ n ]
        #
        # create list of all unique file ids (defined by size and cksum)
        #
        cksums = set([ ( x[2], x[1] ) for x in allFiles[n] ])
        cksums = sorted(cksums)
        #
        # add information for each directory
        #
        for dn in allDirs:
            rowExt = [ "", "", "" ]
            #
            # (try to) find directory in list for this name
            #
            for d,c,s in allFiles[n]:
                if d==dn:
                    idx = cksums.index((s,c))
                    rowExt = [s,c,idx]
                    break
            row.extend(rowExt)
        #
        row.append(len(cksums))
        row.append(len(allFiles[n]))
        csvwriter.writerow(row)
    csvFile.close()
            
