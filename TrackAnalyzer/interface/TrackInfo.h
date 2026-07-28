#ifndef HITANALYZER_SIMTRACKINFO_H
#define HITANALYZER_SIMTRACKINFO_H

#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "CommonTools/Utils/interface/TFileDirectory.h"

#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "SimDataFormats/Track/interface/SimTrackContainer.h"
#include "SimDataFormats/Vertex/interface/SimVertexContainer.h"
// #include "SimDataFormats/Track/interface/SimTrackFwd.h"
// #include "SimDataFormats/Vertex/interface/SimVertexFwd.h"

#include "DataFormats/Math/interface/Point3D.h"
#include "DataFormats/Math/interface/Vector3D.h"

#include "TTree.h"

class TrackInfo {

public:
  struct TrackData {
    std::vector<float> Track_chi2;
    std::vector<unsigned short> Track_ndof;
    std::vector<unsigned short> Track_validHits;
    std::vector<unsigned short> Track_lostHits;
    std::vector<unsigned short> Track_missInnerHits;
    std::vector<unsigned short> Track_missOuterHits;
    std::vector<unsigned short> Track_algo;
    // std::vector<short> Track_quality;
    std::vector<short> Track_charge;
    std::vector<float> Track_dxy;
    std::vector<float> Track_dz;
    std::vector<float> Track_pt;
    std::vector<float> Track_eta;
    std::vector<float> Track_phi;
    std::vector<float> Track_dxyErr;
    std::vector<float> Track_dzErr;
    std::vector<float> Track_ptErr;
    std::vector<float> Track_etaErr;
    std::vector<float> Track_phiErr;
    std::vector<ROOT::Math::XYZVectorF> Track_momTk;
    std::vector<ROOT::Math::XYZVectorF> Track_momentum;
    std::vector<ROOT::Math::XYZPointF> Track_refPos;

    
    /* std::vector<ROOT::Math::XYZPointF> SimTrack_posTk; */
    /* std::vector<ROOT::Math::XYZVectorF> SimTrack_momTk; */
    std::vector<ROOT::Math::XYZVectorF> SimTrack_momentum;    
    std::vector<int> SimTrack_type;
    std::vector<int> SimTrack_charge;
    std::vector<unsigned short> SimTrack_trackInfo;
    std::vector<int> SimTrack_trackId;
  };
  TrackData trackData;

  TrackInfo() {}

  ~TrackInfo() {}

  void setBranches(TTree& tree);
  
  void fillTrackInfo(const reco::Track* track, const SimTrack* simTrack, const SimVertex* simVertex);
  
  void clear();
  
};

#endif
