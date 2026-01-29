#ifndef HITANALYZER_RECHITINFO_H
#define HITANALYZER_RECHITINFO_H


#include "DataFormats/Common/interface/DetSetVector.h"
#include "DataFormats/TrackerRecHit2D/interface/Phase2TrackerRecHit1D.h"
#include "DataFormats/TrackerCommon/interface/TrackerTopology.h"

#include "Geometry/CommonDetUnit/interface/GeomDet.h"
#include "Geometry/CommonDetUnit/interface/PixelGeomDetUnit.h"
#include "Geometry/TrackerGeometryBuilder/interface/TrackerGeometry.h"
#include "SimDataFormats/Track/interface/SimTrackContainer.h"
#include "SimDataFormats/TrackerDigiSimLink/interface/PixelDigiSimLink.h"
#include "SimDataFormats/TrackingHit/interface/PSimHitContainer.h"

#include "DataFormats/Math/interface/Point3D.h"
#include "DataFormats/Math/interface/Vector3D.h"

#include "TTree.h"

class RecHitInfo {

public:
  struct RecHitData
  {
    std::vector<float> Hit_cluster_global_x;
    std::vector<float> Hit_cluster_global_y;
    std::vector<float> Hit_cluster_global_z;
    std::vector<unsigned short> Hit_layer;
    std::vector<unsigned short> Hit_ModuleType;
    std::vector<unsigned short> Hit_cluster_size;
    std::vector<int> Hit_cluster_SimTrack_size;
    std::vector<float> Hit_cluster_local_x;
    std::vector<float> Hit_cluster_local_y;
    std::vector<float> Hit_cluster_local_z;
    std::vector<bool> Hit_cluster_haveSimHit;
    std::vector<float> Hit_cluster_closestSimHit_local_x;
    std::vector<float> Hit_cluster_closestSimHit_local_y;
    std::vector<float> Hit_cluster_closestSimHit_local_z;
    std::vector<unsigned int> Hit_det_rawid;
    std::vector<unsigned short> Hit_cluster_firstStrip;
    std::vector<unsigned short> Hit_cluster_firstRow;
    std::vector<unsigned short> Hit_cluster_column;
    std::vector<unsigned short> Hit_cluster_edge;
    std::vector<unsigned short> Hit_cluster_threshold;
    std::vector<ROOT::Math::XYZPointF> localPos;
    std::vector<ROOT::Math::XYZPointF> globalPos;
    std::vector<ROOT::Math::XYZVectorF> localDir;
    std::vector<ROOT::Math::XYZVectorF> globalDir;
    std::vector<ROOT::Math::XYZVectorF> path;
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
    std::vector<unsigned int> trackId;
    std::vector<unsigned int> nSimTracks;
  };

  RecHitData recHitData;

  RecHitInfo() {
    tTopo = 0;
    tkGeom = 0;
  };

  ~RecHitInfo() {}

  void setBranches(TTree& tree);
  
  std::vector<unsigned int> getSimTrackId(
    edm::Handle<edm::DetSetVector<PixelDigiSimLink> >& pixelSimLinks,
    const DetId& detId, unsigned int channel);
  
  void fillSimHitInfo(const PSimHit& simHit);

  void fillRecHitInfo(const Phase2TrackerRecHit1D& recHit, unsigned int rawid, const GeomDetUnit* geomDetUnit,
		      edm::Handle<edm::DetSetVector<PixelDigiSimLink> >* pixelSimLinks,
		      std::map<unsigned int, SimTrack>& simTracks, edm::Handle<edm::PSimHitContainer>* simHitsRaw,
		      bool debugHitMatch);
  
  void clear();
  
  void setTopology(const TrackerTopology* topo) {
    tTopo = topo;
  }

  void setGeometry(const TrackerGeometry* geom) {
    tkGeom = geom;
  }  
  

 private:
  const TrackerTopology* tTopo;
  const TrackerGeometry* tkGeom;
};

#endif
