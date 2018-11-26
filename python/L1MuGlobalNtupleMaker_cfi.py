import FWCore.ParameterSet.Config as cms

L1MuGlobalNtupleMaker = cms.EDAnalyzer('L1MuGlobalNtupleMaker',
                                  RunningOnData      = cms.bool(False),
                                  PileUpScenario     = cms.int(200),
                                  PileupSrc          = cms.InputTag("slimmedAddPileupInfo"),
                                  triggerbits        = cms.InputTag("TriggerResults","","HLT"),
                                  L1muon             = cms.InputTag("gmtStage2Digis","Muon"),
                                  bmtfMuon           = cms.InputTag("bmtfDigis","BMTF"),
                                  omtfMuon           = cms.InputTag("omtfDigis","OMTF"),
                                  emtfMuon           = cms.InputTag("emtfDigis","EMTF"),
                                  KbmtfMuon          = cms.InputTag("kbmtfDigis","BMTF"),
                                  bmtfInputPhMuon    = cms.InputTag("bmtfDigis",""),
                                  bmtfInputThMuon    = cms.InputTag("bmtfDigis",""),
                                  maxL1Muons         = cms.int(8),
                                  maxBMTFMuons       = cms.int(8),
                                  maxOMTFMuons       = cms.int(8),
                                  maxEMTFMuons       = cms.int(8),
                                  maxKBMTFMuons      = cms.int(8),
                                  maxDTPrimitives    = cms.int(32),
                                 )
