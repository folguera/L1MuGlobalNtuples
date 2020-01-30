from WMCore.Configuration import Configuration
from CRABClient.UserUtilities import config, getUsernameFromSiteDB
config = Configuration()

config.section_('General')
config.General.transferOutputs = True
config.General.workArea = 'crab_projects/samples_MC_omtf_P2TP/'

config.section_('JobType')
config.JobType.psetName = '../run_L1MuNtuple_P2TP.py'
config.JobType.pluginName = 'Analysis'
config.JobType.outputFiles = ['L1MuPhase2Ntuple_P2TP.root']
config.JobType.pyCfgParams = ['doPhase2Emul=True']
config.JobType.allowUndistributedCMSSW = True

config.section_('Data')
config.Data.splitting = 'FileBased'
config.JobType.maxMemoryMB = 2500
config.Data.outLFNDirBase = '/store/user/folguera/GlobalMuNtuples/Jan20_displaced/'
config.Data.publication = False

config.section_('Site')
config.Site.storageSite = 'T2_CH_CERN'

if __name__ == '__main__':

    from CRABAPI.RawCommand import crabCommand
    from CRABClient.ClientExceptions import ClientException
    from httplib import HTTPException
    from multiprocessing import Process

    def submit(config):
        try:
            crabCommand('submit', config = config)
        except HTTPException as hte:
            print "Failed submitting task: %s" % (hte.headers)
        except ClientException as cle:
            print "Failed submitting task: %s" % (cle)

    #############################################################################################
    ## From now on that's what users should modify: this is the a-la-CRAB2 configuration part. ##
    #############################################################################################
    #############################################################################    MUONGUN=True
    DISPLACED=False

    #### Muon Guns
    if MUONGUN:
        config.General.requestName = 'L1MuPhase2Ntuples_Mu_FlatPt2to100'    
        config.Data.inputDataset = '/Mu_FlatPt2to100-pythia8-gun/PhaseIITDRSpring19DR-PU200_106X_upgrade2023_realistic_v3-v2/GEN-SIM-DIGI-RAW'
        p = Process(target=submit, args=(config,))
        p.start()
        p.join()

    #### DISPLACED MUON Guns
    if DISPLACED:
        config.General.requestName = 'L1MuPhase2Ntuples_DisplacedMuonGun_Pt30To100_Dxy_0_1000'
        config.Data.unitsPerJob = 5
        config.Data.inputDataset = '/DisplacedMuons_Pt30to100_Dxy0to3000-pythia8-gun/PhaseIITDRSpring19DR-PU200_106X_upgrade2023_realistic_v3-v1/GEN-SIM-DIGI-RAW'
        p = Process(target=submit, args=(config,))
        p.start()
        p.join()
        
        config.General.requestName = 'L1MuPhase2Ntuples_DisplacedMuonGun_Pt2To10_Dxy_0_1000'
        config.Data.unitsPerJob = 5
        config.Data.inputDataset = '/DisplacedMuons_Pt2to10_Dxy0to3000-pythia8-gun/PhaseIITDRSpring19DR-PU200_106X_upgrade2023_realistic_v3-v1/GEN-SIM-DIGI-RAW'
        p = Process(target=submit, args=(config,))
        p.start()
        p.join()
        
        config.General.requestName = 'L1MuPhase2Ntuples_DisplacedMuonGun_Pt10To30_Dxy_0_1000'
        config.Data.unitsPerJob = 5
        config.Data.inputDataset = '/DisplacedMuons_Pt10to30_Dxy0to3000-pythia8-gun/PhaseIITDRSpring19DR-PU200_106X_upgrade2023_realistic_v3-v1/GEN-SIM-DIGI-RAW'
        p = Process(target=submit, args=(config,))
        p.start()
        p.join()








