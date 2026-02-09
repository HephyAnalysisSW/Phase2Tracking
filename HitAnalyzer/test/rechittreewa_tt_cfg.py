# Imports
import FWCore.ParameterSet.Config as cms

# Create a new CMS process
process = cms.Process('hittree')

# Import all the necessary files
process.load('Configuration.StandardSequences.Services_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.Geometry.GeometryExtendedRun4D110Reco_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:phase2_realistic_T33', '')


# Number of events (-1 = all)
process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
    #input = cms.untracked.int32(100)
)

# Input file
# dataset: /RelValTTbar_14TeV/CMSSW_15_0_0-141X_mcRun4_realistic_v3_STD_RegeneratedGS_Run4D110_noPU-v2/GEN-SIM-RECO
process.source = cms.Source('PoolSource',

    #fileNames = cms.untracked.vstring('file:/afs/cern.ch/work/l/lian/public/Phase2Tracker/CMSSW_15_0_0_pre3/src/29617.0_SingleMuPt1Extended+Run4D110/step3.root')
    #fileNames = cms.untracked.vstring('file:/eos/user/a/adamwo/CMS/Phase2DPG/Data/0b0d313e-56e1-4e64-aa58-8a2e61767bf5.root')
    #fileNames = cms.untracked.vstring(
    #    '/store/relval/CMSSW_15_0_0/RelValTTbar_14TeV/GEN-SIM-RECO/141X_mcRun4_realistic_v3_STD_RegeneratedGS_Run4D110_noPU-v2/2580000/061404ed-7c65-4f6e-88e9-b45a468f1cbe.root', \
    #    '/store/relval/CMSSW_15_0_0/RelValTTbar_14TeV/GEN-SIM-RECO/141X_mcRun4_realistic_v3_STD_RegeneratedGS_Run4D110_noPU-v2/2580000/162e0007-7588-46d8-9c93-a2b4b243885e.root')
    fileNames = cms.untracked.vstring(
        '/store/relval/CMSSW_15_0_0/RelValTTbar_14TeV/GEN-SIM-RECO/141X_mcRun4_realistic_v3_STD_RegeneratedGS_Run4D110_noPU-v2/2580000/061404ed-7c65-4f6e-88e9-b45a468f1cbe.root', \
        '/store/relval/CMSSW_15_0_0/RelValTTbar_14TeV/GEN-SIM-RECO/141X_mcRun4_realistic_v3_STD_RegeneratedGS_Run4D110_noPU-v2/2580000/162e0007-7588-46d8-9c93-a2b4b243885e.root', \
        '/store/relval/CMSSW_15_0_0/RelValTTbar_14TeV/GEN-SIM-RECO/141X_mcRun4_realistic_v3_STD_RegeneratedGS_Run4D110_noPU-v2/2580000/1bb480aa-0bad-439e-a6a4-a75780d0be9c.root', \
        '/store/relval/CMSSW_15_0_0/RelValTTbar_14TeV/GEN-SIM-RECO/141X_mcRun4_realistic_v3_STD_RegeneratedGS_Run4D110_noPU-v2/2580000/3db44076-4bb3-415b-b3a9-feb742460636.root', \
    #    '/store/relval/CMSSW_15_0_0/RelValTTbar_14TeV/GEN-SIM-RECO/141X_mcRun4_realistic_v3_STD_RegeneratedGS_Run4D110_noPU-v2/2580000/41d76683-9927-42e5-8c22-dfa056c56294.root', \
    #    '/store/relval/CMSSW_15_0_0/RelValTTbar_14TeV/GEN-SIM-RECO/141X_mcRun4_realistic_v3_STD_RegeneratedGS_Run4D110_noPU-v2/2580000/4bfe3713-82f0-43ac-8bd6-b16afd9d93e5.root', \
    #    '/store/relval/CMSSW_15_0_0/RelValTTbar_14TeV/GEN-SIM-RECO/141X_mcRun4_realistic_v3_STD_RegeneratedGS_Run4D110_noPU-v2/2580000/4c1b3277-7e2b-48c1-83b2-36ca12ea1a81.root', \
    #    '/store/relval/CMSSW_15_0_0/RelValTTbar_14TeV/GEN-SIM-RECO/141X_mcRun4_realistic_v3_STD_RegeneratedGS_Run4D110_noPU-v2/2580000/739566a2-723b-4c45-a40b-9d7a0f9e5434.root', \
    #    '/store/relval/CMSSW_15_0_0/RelValTTbar_14TeV/GEN-SIM-RECO/141X_mcRun4_realistic_v3_STD_RegeneratedGS_Run4D110_noPU-v2/2580000/75a2a485-cea5-4b7c-ab46-f08964fd9ac0.root', \
    #    '/store/relval/CMSSW_15_0_0/RelValTTbar_14TeV/GEN-SIM-RECO/141X_mcRun4_realistic_v3_STD_RegeneratedGS_Run4D110_noPU-v2/2580000/8490e1fb-3678-42b9-8010-d82ee3ec2a88.root', \
    #    '/store/relval/CMSSW_15_0_0/RelValTTbar_14TeV/GEN-SIM-RECO/141X_mcRun4_realistic_v3_STD_RegeneratedGS_Run4D110_noPU-v2/2580000/99ee730a-ec1c-4c3e-a345-71c82d1f2f41.root', \
    #    '/store/relval/CMSSW_15_0_0/RelValTTbar_14TeV/GEN-SIM-RECO/141X_mcRun4_realistic_v3_STD_RegeneratedGS_Run4D110_noPU-v2/2580000/a448fde4-b759-45ad-8c7e-45e1ec9d5f6e.root', \
    #    '/store/relval/CMSSW_15_0_0/RelValTTbar_14TeV/GEN-SIM-RECO/141X_mcRun4_realistic_v3_STD_RegeneratedGS_Run4D110_noPU-v2/2580000/b3c656c1-6e89-4491-b70d-2003eeb7fa72.root', \
    #    '/store/relval/CMSSW_15_0_0/RelValTTbar_14TeV/GEN-SIM-RECO/141X_mcRun4_realistic_v3_STD_RegeneratedGS_Run4D110_noPU-v2/2580000/c0f20d8b-f32b-40b5-bc5f-86fe17e90525.root', \
    #    '/store/relval/CMSSW_15_0_0/RelValTTbar_14TeV/GEN-SIM-RECO/141X_mcRun4_realistic_v3_STD_RegeneratedGS_Run4D110_noPU-v2/2580000/d7b6f571-25f9-44c4-812b-d040281b9d6a.root', \
    #    '/store/relval/CMSSW_15_0_0/RelValTTbar_14TeV/GEN-SIM-RECO/141X_mcRun4_realistic_v3_STD_RegeneratedGS_Run4D110_noPU-v2/2580000/db97a912-0690-46a1-80e7-ea6759b771ef.root', \
    #    '/store/relval/CMSSW_15_0_0/RelValTTbar_14TeV/GEN-SIM-RECO/141X_mcRun4_realistic_v3_STD_RegeneratedGS_Run4D110_noPU-v2/2580000/f542885d-c2a0-4a1f-9189-30a3995bcd61.root', \
    #    '/store/relval/CMSSW_15_0_0/RelValTTbar_14TeV/GEN-SIM-RECO/141X_mcRun4_realistic_v3_STD_RegeneratedGS_Run4D110_noPU-v2/2580000/fb22dfc2-87a5-40d5-b8c3-feb1e6df4047.root', \
    #    '/store/relval/CMSSW_15_0_0/RelValTTbar_14TeV/GEN-SIM-RECO/141X_mcRun4_realistic_v3_STD_RegeneratedGS_Run4D110_noPU-v2/2580000/fb6db36e-f813-4f25-92ea-afd7ed1ac961.root', \
    #    '/store/relval/CMSSW_15_0_0/RelValTTbar_14TeV/GEN-SIM-RECO/141X_mcRun4_realistic_v3_STD_RegeneratedGS_Run4D110_noPU-v2/2580000/fc0a3df9-3f08-4355-9a91-12c1b3bd74ef.root'
    )
)

# Output
process.TFileService = cms.Service('TFileService',
    fileName = cms.string('file:rechits_tree_tt.root')
)

process.load('RecoLocalTracker.SiPhase2Clusterizer.phase2TrackerClusterizer_cfi')
process.load('RecoLocalTracker.Phase2TrackerRecHits.Phase2StripCPEESProducer_cfi')
#process.load('RecoLocalTracker.Phase2TrackerRecHits.Phase2StripCPEGeometricESProducer_cfi')
process.load('RecoLocalTracker.Phase2TrackerRecHits.Phase2TrackerRecHits_cfi')
#process.siPhase2RecHits.Phase2StripCPE = cms.ESInputTag("phase2StripCPEESProducer", "Phase2StripCPE")
#process.siPhase2RecHits.Phase2StripCPE = cms.ESInputTag("phase2StripCPEGeometricESProducer", "Phase2StripCPEGeometric")


# Analyzer
process.analysis = cms.EDAnalyzer('RecHitTreeWA',
    rechits = cms.InputTag("siPhase2RecHits"),
    clusters = cms.InputTag("siPhase2Clusters"),
    links = cms.InputTag("simSiPixelDigis", "Tracker"),
    simhitsbarrel = cms.InputTag("g4SimHits", "TrackerHitsPixelBarrelLowTof"),
    simhitsendcap = cms.InputTag("g4SimHits", "TrackerHitsPixelEndcapLowTof"),
    simtracks = cms.InputTag("g4SimHits"),
    #ECasRings = cms.bool(True),
    SimTrackMinPt = cms.double(0.5),
    #MakeEtaPlots = cms.bool(False),
    #MinEta = cms.double(0.),
    #MaxEta = cms.double(10.)
    debugHitMatch = cms.bool(False)
)

# Processes to run
#process.rechits_step = cms.Path(process.siPhase2Clusters + process.siPhase2RecHits)
process.rechits_step = cms.Path(process.siPhase2RecHits)
process.analyze_step = cms.Path(process.analysis)

process.schedule = cms.Schedule(process.rechits_step, process.analyze_step)


