#ifndef HITANALYZER_COMMONHITINFO_H
#define HITANALYZER_COMMONHITINFO_H

#include "DataFormats/TrackerCommon/interface/TrackerTopology.h"

#include "Geometry/TrackerGeometryBuilder/interface/TrackerGeometry.h"
#include "SimDataFormats/TrackingHit/interface/PSimHitContainer.h"
#include "SimDataFormats/TrackerDigiSimLink/interface/PixelDigiSimLink.h"
#include "DataFormats/TrackerRecHit2D/interface/Phase2TrackerRecHit1D.h"
#include "SimDataFormats/Track/interface/SimTrack.h"
#include "Phase2Tracking/HitAnalyzer/interface/ClusterSimTracks.h"

#include "DataFormats/Math/interface/Point3D.h"
#include "DataFormats/Math/interface/Vector3D.h"
#include <Math/DisplacementVector2D.h>

#include "TTree.h"

/// spatial vector with cartesian internal representation
typedef ROOT::Math::DisplacementVector2D<ROOT::Math::Cartesian2D<float> > XYVectorF;

class CommonHitInfo {
  
 public:

  typedef std::map< unsigned int, std::vector<const PSimHit*> > DetSimHitsMap;
  typedef std::pair< unsigned int, std::vector<const PSimHit*> > DetSimHitsPair;
  typedef std::map< unsigned int, std::vector<const Phase2TrackerRecHit1D*> > DetRecHitsMap;
  typedef std::pair< unsigned int, std::vector<const Phase2TrackerRecHit1D*> > DetRecHitsPair;
  typedef std::map<const Phase2TrackerRecHit1D*, const Phase2TrackerCluster1D*> RecHitClusterMap;

  typedef std::pair<const Phase2TrackerRecHit1D*, float> RecHitDistancePair;
  typedef std::vector<RecHitDistancePair> RecHitDistancePairs;

  typedef std::map<unsigned int, SimTrack> TrackIdSimTrackMap;

  typedef std::map<const Phase2TrackerCluster1D*, ClusterSimTracks> ClusterSimTracksMap;

  CommonHitInfo() {
    tTopo_ = 0;
    tkGeom_ = 0;
    simTracksById_ = 0;
  };

  ~CommonHitInfo() {}

  std::vector<unsigned int> getSimTrackId(const DetId&, unsigned int);
  
  void fillSimHitsPerDet(const std::vector<const edm::PSimHitContainer*>& simHitsRaw);

  void fillRecHitsPerDet(const Phase2TrackerRecHit1DCollectionNew& rechits);

  RecHitDistancePairs matchRecHitOnDet(const PSimHit* simHit, const DetId& detId,
				       const std::vector<const Phase2TrackerRecHit1D*>& detRecHits);

 
  void setupEvent(const TrackerTopology* topo, const TrackerGeometry* geom,
  		  const edm::DetSetVector<PixelDigiSimLink>* links,
  		  const std::vector<const edm::PSimHitContainer*>& simHitsRaw,
  		  const Phase2TrackerRecHit1DCollectionNew& rechits,
  		  const TrackIdSimTrackMap* simTrackMap) {
    tTopo_ = topo;
    tkGeom_ = geom;
    pixelSimLinks = links;
    simTracksById_ = simTrackMap;
    //
    // fill SimHit map
    //
    fillSimHitsPerDet(simHitsRaw);
    //
    // fill RecHit map (uses SimHit map!)
    //
    fillRecHitsPerDet(rechits);
    //
    // reset cluster map
    //
    clustersByHit_.clear();
  }

  const DetSimHitsMap& simHitsPerDet() {
    return simHitsPerDet_;
  }

  const DetRecHitsMap& recHitsPerDet() {
    return recHitsPerDet_;
  }
  
 protected:
  const TrackerTopology* tTopo_;
  const TrackerGeometry* tkGeom_;
  const edm::DetSetVector<PixelDigiSimLink>* pixelSimLinks;
  const TrackIdSimTrackMap* simTracksById_;

 private:
  DetSimHitsMap simHitsPerDet_;
  DetRecHitsMap recHitsPerDet_;
  RecHitClusterMap clustersByHit_;
  ClusterSimTracksMap cstByCluster_;
};

#endif
