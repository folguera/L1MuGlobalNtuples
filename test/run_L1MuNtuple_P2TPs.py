
import FWCore.ParameterSet.Config as cms

# General config options
import FWCore.ParameterSet.VarParsing as VarParsing
import sys

options = VarParsing.VarParsing()

options.register('globalTag',
                 '106X_upgrade2023_realistic_v2', #default value 
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "Global Tag")

options.register('reEmulation',
                 True, #default value
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.bool,
                 "Run re-emulation")

options.register('doPhase2Emul',
                 True, #default value
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.bool,
                 "Run the phase 2 re-emulation")

options.register('redoPrimitives',
                 False, #default value
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.bool,
                 "Redo the primitives")

options.register('runOnMC',
                 True, #default value
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.bool,
                 "Set to True when running on MC")

options.parseArguments()


from Configuration.ProcessModifiers.convertHGCalDigisSim_cff import convertHGCalDigisSim
from Configuration.StandardSequences.Eras import eras


if options.doPhase2Emul :
    print "Using track trigger"
    process = cms.Process('L1',eras.Phase2_trigger,convertHGCalDigisSim)
else :
    process = cms.Process('L1',eras.Phase2_timing,convertHGCalDigisSim)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.Geometry.GeometryExtended2023D17Reco_cff')
process.load('Configuration.Geometry.GeometryExtended2023D17_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load('Configuration.StandardSequences.SimL1Emulator_cff')
process.load('L1Trigger.TrackFindingTracklet.L1TrackletTracks_cff')


process.L1TrackTrigger_step = cms.Path(process.L1TrackletTracksWithAssociators)
process.VertexProducer.l1TracksInputTag = cms.InputTag("TTTracksFromTracklet", "Level1TTTracks")



# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('step2 nevts:1'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

#Import the emulation configuration
from L1Trigger.L1MuGlobalNtuples.customL1Emu_cff import *
customL1Emu(process, options)

print "Using GlobalTag", options.globalTag
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, options.globalTag, '')

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )

# input source
process.source = cms.Source("PoolSource",
                              fileNames = cms.untracked.vstring (
                                  '/store/mc/PhaseIITDRSpring19DR/Mu_FlatPt2to100-pythia8-gun/GEN-SIM-DIGI-RAW/PU200_106X_upgrade2023_realistic_v3-v2/70000/FFCFF986-ED0B-B74F-B253-C511D19B8249.root'
#                                  "/store/relval/CMSSW_9_3_7/RelValBsToMuMu_14TeV/GEN-SIM-DIGI-RAW/93X_upgrade2023_realistic_v5_2023D17noPU-v2/10000/E0FE0A62-B13A-E911-9DFF-AC1F6BAC8158.root"
                              ),
#                             fileNames = cms.untracked.vstring ("/store/mc/PhaseIIFall17D/SingleMu_FlatPt-2to100/GEN-SIM-DIGI-RAW/L1TPU140_93X_upgrade2023_realistic_v5-v1/00000/FEB81F89-2239-E811-8D78-0CC47A4DEDD0.root"),
#                             fileNames = cms.untracked.vstring ("/store/group/upgrade/sandhya/SMP-PhaseIIFall17D-00001.root"),
                             inputCommands = cms.untracked.vstring("keep *", 
                                                                   "drop l1tHGCalTowerMapBXVector_hgcalTriggerPrimitiveDigiProducer_towerMap_HLT",
                                                                   "drop l1tEMTFHit2016Extras_simEmtfDigis_CSC_HLT",
                                                                   "drop l1tEMTFHit2016Extras_simEmtfDigis_RPC_HLT",
                                                                   "drop l1tEMTFHit2016s_simEmtfDigis__HLT",
                                                                   "drop l1tEMTFTrack2016Extras_simEmtfDigis__HLT",
                                                                   "drop l1tEMTFTrack2016s_simEmtfDigis__HLT",
                                                                   "drop *_hgcalTriggerPrimitiveDigiProducer_*_*",  
                                                                   )
                             )
 


#Import the ntuplizer
process.load("L1Trigger.L1MuGlobalNtuples.L1MuGlobalNtupleMaker_cfi")

#Import Phase-2 TPs
#process.load("Phase2L1Trigger.CalibratedDigis.CalibratedDigis_cfi") 
#process.load("L1Trigger.DTPhase2Trigger.dtTriggerPhase2PrimitiveDigis_cfi")

process.CalibratedDigis.dtDigiTag = "simMuonDTDigis"
process.CalibratedDigis.scenario = 0
process.dtTriggerPhase2PrimitiveDigis.scenario = 0

#Produce RPC clusters from RPCDigi
process.rpcRecHits.rpcDigiLabel = cms.InputTag('simMuonRPCDigis')

# Use RPC
process.dtTriggerPhase2PrimitiveDigis.useRPC = False
process.dtTriggerPhase2PrimitiveDigis.max_quality_to_overwrite_t0 = 10 # strict inequality
process.dtTriggerPhase2PrimitiveDigis.scenario = 0 # 0 for mc, 1 for data, 2 for slice test

# Load  patterns file
#process.simOmtfDigis.patternsXMLFile = cms.FileInPath("L1Trigger/L1TMuon/data/omtf_config/Patterns_0x0005_1.xml")
process.simBayesOmtfDigis.srcDTPh = cms.InputTag('dtTriggerPhase2PrimitiveDigis')
process.simBayesOmtfDigis.srcDTTh = cms.InputTag('simDtTriggerPrimitiveDigis')
process.simBayesOmtfDigis.srcRPC  = cms.InputTag('simMuonRPCDigis')
process.simBayesMuCorrelatorTrackProducer.srcDTPh = cms.InputTag('dtTriggerPhase2PrimitiveDigis')

# We don't have emtfDigis yet, use unpacked input payloads of GMT
#process.L1MuGlobalNtupleMaker.emtfMuon = cms.InputTag("gmtStage2Digis","EMTF") 

process.ntuplizer = cms.Path(process.L1MuGlobalNtupleMaker)

# Output file
process.TFileService = cms.Service("TFileService",
                                   fileName = cms.string("L1MuPhase2Ntuple_P2TP.root")
                                   )


# print log
process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 1000
process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )



if options.reEmulation :
    if options.doPhase2Emul : 
        print "Using Phase-2 emulation"
        process.L1simulation_step = cms.Path(process.phase2_SimL1Emulator)
    else : 
        print "Using Phase-1 emulation"
        process.L1simulation_step = cms.Path(process.SimL1Emulator)


process.endjob_step = cms.EndPath(process.endOfProcess)



# Schedule definition
process.schedule = cms.Schedule()

if options.redoPrimitives :
    print "Regenerating trigger primitives"
    process.schedule.append(process.redoPrimitives_step)

if options.doPhase2Emul :
    process.schedule.append(process.L1TrackTrigger_step)

if options.reEmulation :
    process.schedule.append(process.L1simulation_step)

process.schedule.append(process.ntuplizer)
process.schedule.append(process.endjob_step)

# --- save emulated objects in a root file 
# process.schedule.append(process.outprova_step)