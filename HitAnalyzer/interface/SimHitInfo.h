#ifndef HITANALYZER_SIMHITINFO_H
#define HITANALYZER_SIMHITINFO_H

#include "Phase2Tracking/HitAnalyzer/interface/CommonHitInfo.h"
#include "DataFormats/TrackerCommon/interface/TrackerTopology.h"

#include "Geometry/TrackerGeometryBuilder/interface/TrackerGeometry.h"
#include "SimDataFormats/TrackingHit/interface/PSimHitContainer.h"
#include "SimDataFormats/TrackerDigiSimLink/interface/PixelDigiSimLink.h"
#include "DataFormats/TrackerRecHit2D/interface/Phase2TrackerRecHit1D.h"
#include "SimDataFormats/Track/interface/SimTrack.h"

#include "DataFormats/Math/interface/Point3D.h"
#include "DataFormats/Math/interface/Vector3D.h"
#include <Math/DisplacementVector2D.h>

#include "TTree.h"

/// spatial vector with cartesian internal representation
typedef ROOT::Math::DisplacementVector2D<ROOT::Math::Cartesian2D<float> > XYVectorF;

class SimHitInfo : public CommonHitInfo {

  /* typedef std::map< unsigned int, std::vector<const PSimHit*> > DetSimHitsMap; */
  /* typedef std::pair< unsigned int, std::vector<const PSimHit*> > DetSimHitsPair; */
  /* typedef std::map< unsigned int, std::vector<const Phase2TrackerRecHit1D*> > DetRecHitsMap; */
  /* typedef std::pair< unsigned int, std::vector<const Phase2TrackerRecHit1D*> > DetRecHitsPair; */

  /* typedef std::pair<const Phase2TrackerRecHit1D*, float> RecHitDistancePair; */
  /* typedef std::vector<RecHitDistancePair> RecHitDistancePairs; */

  /* typedef std::map<unsigned int, SimTrack> TrackIdSimTrackMap; */
  
 public:
  struct SimHitData {
    std::vector<ROOT::Math::XYZPointF> localPos;
    std::vector<ROOT::Math::XYZPointF> globalPos;
    std::vector<ROOT::Math::XYZVectorF> localDir;
    std::vector<ROOT::Math::XYZVectorF> globalDir;
    std::vector<ROOT::Math::XYZVectorF> path;
    /* std::vector<ROOT::Math::XYZPointF> localEntry; */
    /* std::vector<ROOT::Math::XYZPointF> localExit; */
    std::vector<float> theta;
    std::vector<float> phi;
    std::vector<float> pabs;
    std::vector<float> tof;
    std::vector<float> energyLoss;
    std::vector<unsigned short> processType;
    std::vector<int>   particleType;
    std::vector<unsigned short> layer;
    std::vector<unsigned short> moduleType;
    std::vector<ROOT::Math::XYZVectorF> detNormal;
    std::vector<bool> hasRecHit;

    std::vector<unsigned int> trackId;
    std::vector<int> trackType;
    std::vector<ROOT::Math::XYZVectorF> trackMom;

    std::vector<unsigned int> rhNMatched;
    std::vector<ROOT::Math::XYZPointF> rhLocalPos;
    std::vector<ROOT::Math::XYZVectorF> rhLocalErr;
    std::vector<ROOT::Math::XYZPointF> rhGlobalPos;
    /* std::vector<unsigned short> Hit_layer; */
    /* std::vector<unsigned short> Hit_ModuleType; */
    std::vector<unsigned short> clusterSize;
    std::vector<int> clusterNSimTracks;
    std::vector<unsigned int> detRawId;
    std::vector<unsigned short> clusterFirstStrip;
    std::vector<unsigned short> clusterFirstRow;
    std::vector<unsigned short> clusterColumn;
    std::vector<unsigned short> clusterEdge;
    std::vector<unsigned short> clusterThreshold;

    
  };
  SimHitData simHitData;

  SimHitInfo() {
    /* tTopo_ = 0; */
    /* tkGeom_ = 0; */
    /* simTracksById_ = 0; */
  };

  ~SimHitInfo() {}

  void setBranches(TTree& tree);
  
  /* std::vector<unsigned int> getSimTrackId(const DetId&, unsigned int); */
  
  /* void fillSimHitsPerDet(const std::vector<const edm::PSimHitContainer*>& simHitsRaw); */

  /* void fillRecHitsPerDet(const Phase2TrackerRecHit1DCollectionNew& rechits); */

  //  const Phase2TrackerRecHit1D* matchRecHitOnDet(const PSimHit* simHit, const DetId& detId,
  //  						const std::vector<const Phase2TrackerRecHit1D*>& detRecHits);
  /* RecHitDistancePairs matchRecHitOnDet(const PSimHit* simHit, const DetId& detId, */
  /* 				      const std::vector<const Phase2TrackerRecHit1D*>& detRecHits); */

 
  void fillSimHitInfo(const PSimHit& simHit);
  
  void clear();

  /* void setupEvent(const TrackerTopology* topo, const TrackerGeometry* geom, */
  /* 		  const edm::DetSetVector<PixelDigiSimLink>* links, */
  /* 		  const std::vector<const edm::PSimHitContainer*>& simHitsRaw, */
  /* 		  const Phase2TrackerRecHit1DCollectionNew& rechits, */
  /* 		  const TrackIdSimTrackMap* simTrackMap) { */

  /*   commonHitInfo.setupEvent(topo,geom,links,simHitsRaw,rechits,simTrackMap); */
    
  /*   tTopo_ = topo; */
  /*   tkGeom_ = geom; */
  /*   pixelSimLinks = links; */
  /*   simTracksById_ = simTrackMap; */
  /*   /\* // fill SimHit map *\/ */
  /*   /\* // *\/ */
  /*   /\* // simHitsPerDet_.clear(); *\/ */
  /*   /\* fillSimHitsPerDet(simHitsRaw); *\/ */
  /*   /\* // *\/ */
  /*   /\* // fill RecHit map (uses SimHit map!) *\/ */
  /*   /\* // *\/ */
  /*   /\* // recHitsPerDet_.clear(); *\/ */
  /*   /\* fillRecHitsPerDet(rechits); *\/ */
  /* } */
  
 private:
  /* const TrackerTopology* tTopo_; */
  /* const TrackerGeometry* tkGeom_; */
  /* const edm::DetSetVector<PixelDigiSimLink>* pixelSimLinks; */

  /* DetSimHitsMap simHitsPerDet_; */
  /* DetRecHitsMap recHitsPerDet_; */

  /* const TrackIdSimTrackMap* simTracksById_; */

  CommonHitInfo commonHitInfo_;
};

#endif
