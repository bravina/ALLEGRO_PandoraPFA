# steering file for the ALLEGRO reconstruction

import os
from k4FWCore.parseArgs import parser

# Logger
from Gaudi.Configuration import INFO, DEBUG, WARNING  # , VERBOSE


parser_group = parser.add_argument_group("ALLEGROReconstruction.py custom options")
parser_group.add_argument("--inputFiles", action="extend", nargs="+", metavar=("file1", "file2"), help="One or multiple input files")
parser_group.add_argument("--outputFile", help="Output file name", default="output.root")
parser_group.add_argument("--compactFile", help="Compact detector file to use", type=str, default=os.environ["K4GEO"] + "FCCee/ALLEGRO/compact/ALLEGRO_o1_v04/ALLEGRO_o1_v04.xml")
reco_args = parser.parse_known_args()[0]



#
# SETTINGS
#

# - general settings
#
Nevts = -1                                # -1 means all events
doSWClustering = False
doTopoClustering = False

#
# ALGORITHMS AND SERVICES SETUP
#
TopAlg = []  # alg sequence
ExtSvc = []  # list of external services


# CPU information
from Configurables import AuditorSvc, ChronoAuditor
chra = ChronoAuditor()
audsvc = AuditorSvc()
audsvc.Auditors = [chra]
ExtSvc += [audsvc]


# Detector geometry
# prefix all xmls with path_to_detector
# if K4GEO is empty, this should use relative path to working directory
from Configurables import GeoSvc
import os
geoservice = GeoSvc("GeoSvc")
path_to_detector = os.environ.get("K4GEO", "")
detectors_to_use = [
    'FCCee/ALLEGRO/compact/ALLEGRO_o1_v04/ALLEGRO_o1_v04.xml'
]

if reco_args.compactFile:
  geoservice.detectors = [reco_args.compactFile]
else:
  geoservice.detectors = [ os.path.join(path_to_detector, _det) for _det in detectors_to_use ]
geoservice.OutputLevel = INFO
ExtSvc += [geoservice]

# Input/Output handling
from Configurables import k4DataSvc, PodioInput
evtsvc = k4DataSvc('EventDataSvc')
ExtSvc += [evtsvc]

from k4MarlinWrapper.inputReader import create_reader, attach_edm4hep2lcio_conversion
read = create_reader(reco_args.inputFiles,evtsvc)
read.OutputLevel = INFO
TopAlg.append(read)

from Configurables import PodioOutput
out = PodioOutput("PodioOutput", filename = reco_args.outputFile)
out.outputCommands = ["keep *"]

# ECAL barrel parameters for digitisation
ecalBarrelSamplingFraction = [0.3800493723322256] * 1 + [0.13494147915064658] * 1 + [0.142866851721152] * 1 + [0.14839315921940666] * 1 + [0.15298362570665006] * 1 + [0.15709704561942747] * 1 + [0.16063717490147533] * 1 + [0.1641723795419055] * 1 + [0.16845490287689746] * 1 + [0.17111520115997653] * 1 + [0.1730605163148862] * 1
ecalBarrelUpstreamParameters = [[0.028158491043365624, -1.564259408365951, -76.52312805346982, 0.7442903558010191, -34.894692961350195, -74.19340877431723]]
ecalBarrelDownstreamParameters = [[0.00010587711361028165, 0.0052371999097777355, 0.69906696456064, -0.9348243433360095, -0.0364714212117143, 8.360401126995626]]
ecalBarrelLayers = len(ecalBarrelSamplingFraction)

# - ECAL readouts
ecalBarrelReadoutName = "ECalBarrelModuleThetaMerged"      # barrel, original segmentation (baseline)
ecalEndcapReadoutName = "ECalEndcapTurbine"                # endcap, turbine-like (baseline)

from Configurables import CellPositionsECalBarrelModuleThetaSegTool
cellPositionEcalBarrelTool = CellPositionsECalBarrelModuleThetaSegTool(
    "CellPositionsECalBarrel",
    readoutName=ecalBarrelReadoutName,
    OutputLevel=INFO
)


# - EM scale calibration (sampling fraction)
from Configurables import CalibrateInLayersTool
#   * ECAL barrel
calibEcalBarrel = CalibrateInLayersTool("CalibrateECalBarrel",
                                        samplingFraction=ecalBarrelSamplingFraction,
                                        readoutName=ecalBarrelReadoutName,
                                        layerFieldName="layer")
#   * ECAL endcap
calibEcalEndcap = CalibrateInLayersTool("CalibrateECalEndcap",
                                        samplingFraction=[0.16419] * 1 + [0.192898] * 1 + [0.18783] * 1 + [0.193203] * 1 + [0.193928] * 1 + [0.192286] * 1 + [0.199959] * 1 + [0.200153] * 1 + [0.212635] * 1 + [0.180345] * 1 + [0.18488] * 1 + [0.194762] * 1 + [0.197775] * 1 + [0.200504] * 1 + [0.205555] * 1 + [0.203601] * 1 + [0.210877] * 1 + [0.208376] * 1 + [0.216345] * 1 + [0.201452] * 1 + [0.202134] * 1 + [0.207566] * 1 + [0.208152] * 1 + [0.209889] * 1 + [0.211743] * 1 + [0.213188] * 1 + [0.215864] * 1 + [0.22972] * 1 + [0.192515] * 1 + [0.0103233] * 1,
                                        readoutName=ecalEndcapReadoutName,
                                        layerFieldName="layer")

# - HCAL readouts
hcalBarrelReadoutName = "HCalBarrelReadout"            # barrel, original segmentation (row-phi)
hcalEndcapReadoutName = "HCalEndcapReadout"            # endcap, original segmentation

from Configurables import CalibrateCaloHitsTool

# HCAL barrel
calibHCalBarrel = CalibrateCaloHitsTool(
        "CalibrateHCalBarrel", invSamplingFraction="29.4202")
# HCAL endcap
calibHCalEndcap = CalibrateCaloHitsTool(
        "CalibrateHCalEndcap", invSamplingFraction="29.4202")  # FIXME: to be updated for ddsim

from Configurables import CellPositionsHCalPhiThetaSegTool
cellPositionHCalBarrelTool = CellPositionsHCalPhiThetaSegTool(
        "CellPositionsHCalBarrel",
        readoutName=hcalBarrelReadoutName,
        OutputLevel=INFO
    )
cellPositionHCalEndcapTool = CellPositionsHCalPhiThetaSegTool(
        "CellPositionsHCalEndcap",
        readoutName=hcalEndcapReadoutName,
        OutputLevel=INFO
    )


from Configurables import CreatePositionedCaloCells

# Create cells in ECal barrel (calibrated and positioned - optionally with xtalk and noise added)
# from uncalibrated cells (+cellID info) from ddsim
ecalBarrelPositionedCellsName = ecalBarrelReadoutName + "Positioned"
createEcalBarrelCells = CreatePositionedCaloCells("CreatePositionedECalBarrelCells",
                                                  doCellCalibration=True,
                                                  positionsTool=cellPositionEcalBarrelTool,
                                                  calibTool=calibEcalBarrel,
                                                  crosstalkTool=None,
                                                  addCrosstalk=False,
                                                  addCellNoise=False,
                                                  filterCellNoise=False,
                                                  OutputLevel=INFO,
                                                  hits=ecalBarrelReadoutName,
                                                  cells=ecalBarrelPositionedCellsName)
TopAlg += [createEcalBarrelCells]


# Apply calibration and positioning to cells in HCal barrel
hcalBarrelPositionedCellsName = hcalBarrelReadoutName + "Positioned"
createHCalBarrelCells = CreatePositionedCaloCells("CreatePositionedHCalBarrelCells",
                                                      doCellCalibration=True,
                                                      calibTool=calibHCalBarrel,
                                                      positionsTool=cellPositionHCalBarrelTool,
                                                      addCellNoise=False,
                                                      filterCellNoise=False,
                                                      hits=hcalBarrelReadoutName,
                                                      cells=hcalBarrelPositionedCellsName,
                                                      OutputLevel=INFO)
TopAlg += [createHCalBarrelCells]

# Create cells in HCal endcap
hcalEndcapPositionedCellsName = hcalEndcapReadoutName + "Positioned"
createHCalEndcapCells = CreatePositionedCaloCells("CreatePositionedHCalEndcapCells",
                                                      doCellCalibration=True,
                                                      calibTool=calibHCalEndcap,
                                                      addCellNoise=False,
                                                      filterCellNoise=False,
                                                      positionsTool=cellPositionHCalEndcapTool,
                                                      OutputLevel=INFO,
                                                      hits=hcalEndcapReadoutName,
                                                      cells=hcalEndcapPositionedCellsName)
TopAlg += [createHCalEndcapCells]



# Tracking
# Create tracks from gen particles
from Configurables import TracksFromGenParticles
tracksFromGenParticles = TracksFromGenParticles("CreateTracksFromGenParticles",
                                                    InputGenParticles = "MCParticles",
                                                    InputSimTrackerHits = "DCHCollection",
                                                    OutputTracks = "TracksFromGenParticles",
                                                    OutputMCRecoTrackParticleAssociation = "TracksFromGenParticlesAssociation",
                                                    Bz = 2.0,
                                                    OutputLevel = INFO)
TopAlg += [tracksFromGenParticles]

### Muon Hits (disabled - MuonCaloHitDigi not available in current nightly)
#from Configurables import MuonCaloHitDigi
#MuonCaloHitDigitizer = MuonCaloHitDigi("MuonCaloHitDigitizer",
#    inputSimHits = "MuonTaggerPhiTheta",
#    outputDigiHits = "MuonCaloHitCollection",
#    readoutName = "MuonTaggerPhiTheta",
#    OutputLevel = INFO,
#)
#TopAlg += [MuonCaloHitDigitizer]

## Clustering
if doSWClustering or doTopoClustering:
    from Configurables import CreateEmptyCaloCellsCollection
    createemptycells = CreateEmptyCaloCellsCollection("CreateEmptyCaloCells")
    createemptycells.cells.Path = "emptyCaloCells"
    TopAlg += [createemptycells]


# Function that sets up the sequence for producing SW clusters given an input cell collection
def setupSWClusters(inputCells,
                    inputReadouts,
                    outputClusters,
                    clusteringThreshold,
                    applyUpDownstreamCorrections,
                    applyMVAClusterEnergyCalibration,
                    addShapeParameters,
                    runPhotonIDTool):

    global TopAlg

    from Configurables import CaloTowerToolFCCee
    from Configurables import CreateCaloClustersSlidingWindowFCCee

    # Clustering parameters
    # - phi-theta window sizes
    windT = 9
    windP = 17
    posT = 5
    posP = 11
    dupT = 7
    dupP = 13
    finT = 9
    finP = 17
    # - minimal energy to create a cluster in GeV (FCC-ee detectors have to reconstruct low energy particles)
    threshold = clusteringThreshold

    from Configurables import CaloTowerToolFCCee
    from Configurables import CreateCaloClustersSlidingWindowFCCee

    towerTool = CaloTowerToolFCCee(outputClusters + "TowerTool",
                                   deltaThetaTower=4 * 0.009817477 / 4, deltaPhiTower=2 * 2 * pi / 1536.,
                                   ecalBarrelReadoutName=inputReadouts.get("ecalBarrel", ""),
                                   ecalEndcapReadoutName=inputReadouts.get("ecalEndcap", ""),
                                   ecalFwdReadoutName=inputReadouts.get("ecalFwd", ""),
                                   hcalBarrelReadoutName=inputReadouts.get("hcalBarrel", ""),
                                   hcalExtBarrelReadoutName=inputReadouts.get("hcalExtBarrel", ""),
                                   hcalEndcapReadoutName=inputReadouts.get("hcalEndcap", ""),
                                   hcalFwdReadoutName=inputReadouts.get("hcalFwd", ""),
                                   OutputLevel=INFO)
    towerTool.ecalBarrelCells.Path = inputCells.get("ecalBarrel", "emptyCaloCells")
    towerTool.ecalEndcapCells.Path = inputCells.get("ecalEndcap", "emptyCaloCells")
    towerTool.ecalFwdCells.Path = inputCells.get("ecalFwd", "emptyCaloCells")
    towerTool.hcalBarrelCells.Path = inputCells.get("hcalBarrel", "emptyCaloCells")
    towerTool.hcalExtBarrelCells.Path = inputCells.get("hcalExtBarrel", "emptyCaloCells")
    towerTool.hcalEndcapCells.Path = inputCells.get("hcalEndcap", "emptyCaloCells")
    towerTool.hcalFwdCells.Path = inputCells.get("hcalFwd", "emptyCaloCells")

    clusterAlg = CreateCaloClustersSlidingWindowFCCee("Create" + outputClusters,
                                                      towerTool=towerTool,
                                                      nThetaWindow=windT, nPhiWindow=windP,
                                                      nThetaPosition=posT, nPhiPosition=posP,
                                                      nThetaDuplicates=dupT, nPhiDuplicates=dupP,
                                                      nThetaFinal=finT, nPhiFinal=finP,
                                                      energyThreshold=threshold,
                                                      energySharingCorrection=False,
                                                      attachCells=True,
                                                      OutputLevel=INFO
                                                      )
    clusterAlg.clusters.Path = outputClusters
    clusterAlg.clusterCells.Path = outputClusters.replace("Clusters", "Cluster") + "Cells"
    TopAlg += [clusterAlg]
    clusterAlg.AuditExecute = True

if doSWClustering:
    # HCAL clusters
    if runHCal:
        CaloClusterInputs = {
            "hcalBarrel": hcalBarrelPositionedCellsName,
            "hcalEndcap": hcalEndcapPositionedCellsName,
        }
        CaloClusterReadouts = {
            "hcalBarrel": hcalBarrelReadoutName,
            "hcalEndcap": hcalEndcapReadoutName,
        }
        setupSWClusters(CaloClusterInputs,
                        CaloClusterReadouts,
                        "CaloClusters",
                        0.04,
                        False,
                        False,
                        False,
                        False)

# Function that sets up the sequence for producing Topo clusters given an input cell collection
def setupTopoClusters(inputCells,
                      inputReadouts,
                      inputPositioningTools,  # TODO: check if we still need these since the cells are positioned..
                      outputClusters,
                      neighboursMap,
                      noiseMap,
                      applyUpDownstreamCorrections,
                      applyMVAClusterEnergyCalibration,
                      addShapeParameters,
                      runPhotonIDTool):

    global TopAlg

    from Configurables import CaloTopoClusterInputTool
    from Configurables import TopoCaloNeighbours
    from Configurables import TopoCaloNoisyCells
    from Configurables import CaloTopoClusterFCCee


    # Clustering parameters
    seedSigma = 4
    neighbourSigma = 2
    lastNeighbourSigma = 0

    # tool collecting the input cells
    topoClusterInputTool = CaloTopoClusterInputTool(outputClusters + "InputTool",
                                                    ecalBarrelReadoutName=inputReadouts.get("ecalBarrel", ""),
                                                    ecalEndcapReadoutName=inputReadouts.get("ecalEndcap", ""),
                                                    ecalFwdReadoutName=inputReadouts.get("ecalFwd", ""),
                                                    hcalBarrelReadoutName=inputReadouts.get("hcalBarrel", ""),
                                                    hcalExtBarrelReadoutName=inputReadouts.get("hcalExtBarrel", ""),
                                                    hcalEndcapReadoutName=inputReadouts.get("hcalEndcap", ""),
                                                    hcalFwdReadoutName=inputReadouts.get("hcalFwd", ""),
                                                    OutputLevel=INFO)
    topoClusterInputTool.ecalBarrelCells.Path = inputCells.get("ecalBarrel", "emptyCaloCells")
    topoClusterInputTool.ecalEndcapCells.Path = inputCells.get("ecalEndcap", "emptyCaloCells")
    topoClusterInputTool.ecalFwdCells.Path = inputCells.get("ecalFwd", "emptyCaloCells")
    topoClusterInputTool.hcalBarrelCells.Path = inputCells.get("hcalBarrel", "emptyCaloCells")
    topoClusterInputTool.hcalExtBarrelCells.Path = inputCells.get("hcalExtBarrel", "emptyCaloCells")
    topoClusterInputTool.hcalEndcapCells.Path = inputCells.get("hcalEndcap", "emptyCaloCells")
    topoClusterInputTool.hcalFwdCells.Path = inputCells.get("hcalFwd", "emptyCaloCells")

    # tool providing the map of cell neighbours
    neighboursTool = TopoCaloNeighbours(outputClusters + "NeighboursMap",
                                        fileName=neighboursMap,
                                        OutputLevel=INFO)

    # tool providing expected noise levels per cell
    noiseTool = TopoCaloNoisyCells(outputClusters + "NoiseMap",
                                   fileName=noiseMap,
                                   OutputLevel=INFO)

    # algorithm creating the topoclusters
    clusterAlg = CaloTopoClusterFCCee("Create" + outputClusters,
                                      TopoClusterInput=topoClusterInputTool,
                                      # expects neighbours map from cellid->vec < neighbourIds >
                                      neigboursTool=neighboursTool,
                                      # tool to get noise level per cellid
                                      noiseTool=noiseTool,
                                      # cell positions tools for all sub - systems
                                      positionsECalBarrelTool=inputPositioningTools.get('ecalBarrel', None),
                                      # positionsEMECTool=inputPositioningTools.get('ecalEndcap', None),
                                      # positionsEMFwdTool=inputPositioningTools.get('ecalFwd', None),
                                      positionsHCalBarrelTool=inputPositioningTools.get('hcalBarrel', None),
                                      positionsHCalBarrelNoSegTool=None,
                                      positionsHCalExtBarrelTool=inputPositioningTools.get('hcalEndcap', None),
                                      # positionsHECTool=inputPositioningTools.get('hcalEndcap', None),
                                      # positionsHFwdTool=inputPositioningTools.get('hcalFwd', None),
                                      noSegmentationHCal=False,
                                      # algorithm parameters
                                      seedSigma=seedSigma,
                                      neighbourSigma=neighbourSigma,
                                      lastNeighbourSigma=lastNeighbourSigma,
                                      OutputLevel=INFO)
    clusterAlg.clusters.Path = outputClusters
    clusterAlg.clusterCells.Path = outputClusters.replace("Clusters", "Cluster") + "Cells"
    TopAlg += [clusterAlg]


if doTopoClustering:
    # HCAL clusters
    CaloTopoClusterInputs = {
            "ecalBarrel": ecalBarrelPositionedCellsName,
            "hcalBarrel": hcalBarrelPositionedCellsName,
            "hcalEndcap": hcalEndcapPositionedCellsName
        }
    CaloTopoClusterReadouts = {
            "ecalBarrel": ecalBarrelReadoutName,
            "hcalBarrel": hcalBarrelReadoutName,
            "hcalEndcap": hcalEndcapReadoutName
        }
    CaloTopoClusterPositioningTools = {
            "ecalBarrel" : cellPositionEcalBarrelTool,
            "hcalBarrel": cellPositionHCalBarrelTool,
            "hcalEndcap": cellPositionHCalEndcapTool,
        }
    setupTopoClusters(CaloTopoClusterInputs,
                          CaloTopoClusterReadouts,
                          CaloTopoClusterPositioningTools,
                          "CaloTopoClusters",
                          "neighbours_map_ecalB_thetamodulemerged_hcalB_hcalEndcap_phitheta.root",
                          "cellNoise_map_electronicsNoiseLevel_ecalB_thetamodulemerged.root",
                          False,
                          False,
                          False,
                          False)

################################################
##  Pandora
################################################
from Configurables import MarlinProcessorWrapper
pandora = MarlinProcessorWrapper('DDMarlinPandora')
pandora.OutputLevel = INFO
pandora.ProcessorType = 'DDPandoraPFANewProcessor'
pandora.Parameters = {
                                      "PandoraSettingsXmlFile": ["PandoraSettingsDefault.xml"],
                                      "ECalMipThreshold": ["0."],
                                      "HCalMipThreshold": ["0."],
                                      "ECalToHadGeVCalibrationBarrel": ["1."], # this must be calculated for ALLEGRO
                                      "ECalToHadGeVCalibrationEndCap": ["1."], # this must be calculated for ALLEGRO
                                      "HCalToHadGeVCalibration": ["1."], # this must be calculated for ALLEGRO
                                      "ECalToMipCalibration": ["175.439"], # value is from CLD -> this must be calculated for ALLEGRO
                                      "HCalToMipCalibration": ["49.7512"], # value is from CLD -> this must be calculated for ALLEGRO
                                      "DigitalMuonHits": ["0"],
                                      "MaxHCalHitHadronicEnergy": ["10000000."],
                                      "MuonToMipCalibration": ["20703.9"], # value is from CLD -> this must be calculated for ALLEGRO
                                      "ECalToEMGeVCalibration": ["1.0"], # this seems to be an EM scale factor for ECAL: set to 1 since input cell energy is already calibrated at EM scale
                                      "HCalToEMGeVCalibration": ["1.0"], # this seems to be an EM scale factor for HCAL: set to 1 since input cell energy is already calibrated at EM scale
                                      "DetectorName" : ["ALLEGRO"],
                                      "UseDD4hepField" : ["1"],
                                      "MCParticleCollections" : ["MCParticle"],
                                      "ECalCaloHitCollections" : ["ECalBarrelModuleThetaMergedPositioned"],
                                      #"HCalCaloHitCollections" : ["HCalBarrelReadoutPositioned","HCalEndcapReadoutPositioned"],
                                      "HCalCaloHitCollections" : ["HCalBarrelReadoutPositioned"],
                                      #"MuonCaloHitCollections" : ["MuonCaloHitCollection"],
                                      "TrackCollections" : ["TracksFromGenParticles"],

                      }

TopAlg += [pandora]
################################################

# For converters
from Configurables import Lcio2EDM4hepTool, EDM4hep2LcioTool


from Configurables import Lcio2EDM4hepTool
lcioConvTool = Lcio2EDM4hepTool("lcio2EDM4hep")
lcioConvTool.convertAll = True
lcioConvTool.collNameMapping = {
        "MCParticle": "MCParticles",
        "TrackCollection" : "TracksFromGenParticles",
}
pandora.Lcio2EDM4hepTool=lcioConvTool

# We need to convert the inputs in case we have EDM4hep input
attach_edm4hep2lcio_conversion(TopAlg, read)

TopAlg += [out]

# configure the application
print(TopAlg)
print(ExtSvc)
from k4FWCore import ApplicationMgr
applicationMgr = ApplicationMgr(
    TopAlg=TopAlg,
    EvtSel='NONE',
    EvtMax=Nevts,
    ExtSvc=ExtSvc,
    StopOnSignal=True,
)

for algo in applicationMgr.TopAlg:
    algo.AuditExecute = True
