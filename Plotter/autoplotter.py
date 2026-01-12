import os,sys
import math
import uuid
import shutil
import Phase2Tracking.Plotter.python.plotter as p

import argparse

def partition(lst, n):
    ''' Partition list into chunks of approximately equal size'''
    # http://stackoverflow.com/questions/2659900/python-slicing-a-list-into-n-nearly-equal-length-partitions
    n_division = len(lst) / float(n)
    return [ lst[int(round(n_division * i)): int(round(n_division * (i + 1)))] for i in range(n) ]

def getFileList(inputdir):
    filelist = []
    if os.path.exists( inputdir ) and os.path.isdir( inputdir ):
        for root, dirs, files in os.walk(inputdir):
            for filename in files:
                if filename.endswith('.root'):
                    if 'eos' in root:
                      filelist.append('root://eos.grid.vbc.ac.at/'+os.path.join( root, filename ))
                    else:
                      filelist.append(os.path.join( root, filename ))
    return filelist

parser = argparse.ArgumentParser()
parser.add_argument('--name', type=str, 
                        help='job name')
parser.add_argument('--treeName', type=str, 
                        help='tree name')
parser.add_argument('--output', type=str,
                        help='output dir')
parser.add_argument('--config', type=str,
                        help='config to use') 
parser.add_argument('--filelist', type=str,default='',
                        help='path of the txt file that include the list of files to run') 
parser.add_argument('--postfix', type=str,default='',
                        help='postfix of the output file') 
parser.add_argument('--data', action='store_true', default=False,
                        help='Whether the input is data') 
parser.add_argument('--submit', action='store_true', default=False,
                        help='Whether to submit jobs')
parser.add_argument('--njobs', type=int, default=1,
                        help='The number of jobs to submit for each sample. Could be a list of a single value.')
parser.add_argument('--nfiles', type=int, default=-1,
                        help='The number of files per job to submit for each sample. Could be a list of a single value.')
parser.add_argument('--loadMacro', type=str, nargs='*', default=[ ], \
                        help='File name for C++ macro(s) to be loaded (can be repeated)')
args = parser.parse_args()


if __name__=="__main__":

  input_dict = {
          "SingleMuPt10_noPU": "/eos/vbc/experiments/cms/store/user/lian/RelValSingleMuPt10/SingleMuPt10_noPU_2_lian/250916_143902/",
          "SingleMuPt10_PU": "/eos/vbc/experiments/cms/store/user/lian/RelValSingleMuPt10/SingleMuPt10_PU_2_lian/250916_143949/",
          "TTbar_noPU": "/eos/vbc/experiments/cms/store/user/lian/RelValTTbar_14TeV/RelValTTbar_noPU_2_lian/250916_143751/",
          "TTbar_PU": "/eos/vbc/experiments/cms/store/user/lian/RelValTTbar_14TeV/RelValTTbar_PU_2_lian/250916_143706/",
      }

  print("Using config {}".format(args.config))

  if args.submit:
    inputdir = args.output+'/input'
    if os.path.exists(args.output):
      print("WARNING! {} already exists! Continuing...".format(args.output))
    else:
      os.makedirs(args.output)
    if os.path.exists(os.path.join(args.output,'input')):
      print("WARNING! Input dir already exists! Continuing...".format(args.output))
    else:
      os.makedirs(inputdir)
    if os.path.exists(os.path.join(inputdir,os.path.basename(args.config))):
      print("WARNING! Config {} already exists! Reusing for plotting...".format(os.path.basename(args.config)))
    else:
      shutil.copy2(args.config,inputdir)
    if os.path.exists(os.path.join(inputdir,'autoplotter.py')):
      print("WARNING! File autoplotter.py already exists! Reusing for plotting...")
    else:
      shutil.copy2(os.path.join(os.getcwd(),'autoplotter.py'),inputdir)

    jobf = open('jobs.sh',"w")
    if args.data:
      data = '--data'
    else:
      data=''
    for s in input_dict:
      outputdir_sample = os.path.join(args.output,s)
      if os.path.exists(outputdir_sample):
        print("Path {} already exists! Skipping...".format(outputdir_sample))
        continue
      inputdir_sample = outputdir_sample+'/input'
      os.makedirs(inputdir_sample)
      files = getFileList(input_dict[s])
      njobs = min(args.njobs, len(files))
      if args.nfiles>0:
        njobs = int(math.ceil(len(files)/float(args.nfiles)))
      chunks = partition( files, min(njobs , len(files) ) ) 
      print("Got %i files and n_split into %i jobs of %3.2f files/job on average." % ( len(files), len(chunks), len(files)/float(len(chunks))))
      for ic in range(len(chunks)):
        with open("{}_fn{}.txt".format(s,ic),"w") as fns:
          fns.write("\n".join(chunks[ic]))
        shutil.copy2("{}_fn{}.txt".format(s,ic),inputdir_sample)
        os.remove("{}_fn{}.txt".format(s,ic))

      for ij in range(len(chunks)):
        flname = "{}_fn{}.txt".format(s,ij)
        uuid_ =  str(uuid.uuid4())
        command = "set -e;mkdir /tmp/%s;" % (uuid_)
        command += "cd /tmp/%s;" %(uuid_)
        if 'eos' in inputdir:
          command += "xrdcp -r root://eos.grid.vbc.ac.at/%s /tmp/%s/.;" %(inputdir,uuid_)
          command += "cp /tmp/%s/input/* /tmp/%s/.;" %(uuid_,uuid_)
          command += "xrdcp -r root://eos.grid.vbc.ac.at/%s /tmp/%s/input/.;" %(inputdir_sample,uuid_)
          command += "cp /tmp/%s/input/input/* /tmp/%s/.;" %(uuid_,uuid_)
        else:
          command += "cp %s /tmp/%s/.;" %(inputdir+'/*',uuid_)
          command += "cp %s /tmp/%s/.;" %(inputdir_sample+'/*',uuid_)
        command += "python3 autoplotter.py --name {} --treeName {} --output ./ --config ./{} --filelist ./{} --postfix _{} {};".format(s,args.treeName,os.path.basename(args.config),flname,ij,data)
        if 'eos' in outputdir_sample:
          fname = "{}_hist_{}".format(samp.name,ij)
          command += "eoscp ./{0}.root {1}/{0}.root;".format(fname,outputdir_sample)
          command += "eoscp ./{0}.pkl {1}/{0}.pkl;".format(fname,outputdir_sample)
        else:
          command += "cp ./*.root {}/.;".format(outputdir_sample)
          command += "cp ./*.pkl {}/.;".format(outputdir_sample)
        command += "\n"
        jobf.write(command)
    jobf.close()
    jbfn = 'jobs{}.sh'
    ij = ''
    if os.path.exists(os.path.join(inputdir,jbfn.format(ij))):
      ij=1
      while os.path.exists(os.path.join(inputdir,jbfn.format(ij))):
        ij += 1
    shutil.copy2('jobs.sh',os.path.join(inputdir,jbfn.format(ij)))

  else:
    if not os.path.exists(args.filelist):
        raise Exception("file list not given for plotting")
    plotter = p.Plotter(name=args.name,treeName=str(args.treeName),outputDir=args.output,input_filelist=args.filelist,config=args.config,isData=args.data,postfix=args.postfix,macros=args.loadMacro)
    plotter.makeHistFiles()

