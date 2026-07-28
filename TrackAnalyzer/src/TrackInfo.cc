#include "Phase2Tracking/TrackAnalyzer/interface/TrackInfo.h"
// #include "DataFormats/DetId/interface/DetId.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "SimDataFormats/Track/interface/SimTrack.h"
#include "DataFormats/BeamSpot/interface/BeamSpot.h"

void TrackInfo::setBranches(TTree& tree) {
    tree.Branch("Track_chi2", &trackData.Track_chi2);
    tree.Branch("Track_ndof", &trackData.Track_ndof);
    tree.Branch("Track_validHits", &trackData.Track_validHits);
    tree.Branch("Track_lostHits", &trackData.Track_lostHits);
    tree.Branch("Track_missInnerHits", &trackData.Track_missInnerHits);
    tree.Branch("Track_missOuterHits", &trackData.Track_missOuterHits);
    tree.Branch("Track_algo", &trackData.Track_algo);
    // tree.Branch("Track_quality", &trackData.Track_quality);
    tree.Branch("Track_charge", &trackData.Track_charge);
    tree.Branch("Track_dxy", &trackData.Track_dxy);
    tree.Branch("Track_dz", &trackData.Track_dz);
    tree.Branch("Track_pt", &trackData.Track_pt);
    tree.Branch("Track_eta", &trackData.Track_eta);
    tree.Branch("Track_phi", &trackData.Track_phi);
    tree.Branch("Track_dxyErr", &trackData.Track_dxyErr);
    tree.Branch("Track_dzErr", &trackData.Track_dzErr);
    tree.Branch("Track_ptErr", &trackData.Track_ptErr);
    tree.Branch("Track_etaErr", &trackData.Track_etaErr);
    tree.Branch("Track_phiErr", &trackData.Track_phiErr);
    tree.Branch("Track_refPos", &trackData.Track_refPos);
    tree.Branch("Track_momentum", &trackData.Track_momentum);
    
    // tree.Branch("SimTrack_posTk", &trackData.SimTrack_posTk);
    // tree.Branch("SimTrack_momTk", &trackData.SimTrack_momTk);
    tree.Branch("SimTrack_momentum", &trackData.SimTrack_momentum);    
    tree.Branch("SimTrack_type", &trackData.SimTrack_type);
    tree.Branch("SimTrack_charge", &trackData.SimTrack_charge);
    tree.Branch("SimTrack_trackInfo", &trackData.SimTrack_trackInfo);
    tree.Branch("SimTrack_trackId", &trackData.SimTrack_trackId);

};


void TrackInfo::fillTrackInfo(const reco::Track* track, const SimTrack* simTrack, const SimVertex* simVertex) {
    //
    // define reference point for impacts (default = origin)
    // TO BE IMPROVED:
    //    reference point (=simVertex) only used for dxy and dz ( not for the uncertainties or momentum) !!!!
    //
    math::XYZPoint refPoint(0.,0.,0.);
    if ( simVertex!=nullptr ) {
      refPoint.SetX(simVertex->position().x());
      refPoint.SetY(simVertex->position().y());
      refPoint.SetZ(simVertex->position().z());
    }
    trackData.Track_refPos.push_back(ROOT::Math::XYZPointF(refPoint.x(),refPoint.y(),refPoint.z()));
  
    trackData.Track_chi2.push_back(track->chi2());
    trackData.Track_ndof.push_back(track->ndof());
    trackData.Track_validHits.push_back(track->numberOfValidHits());
    trackData.Track_lostHits.push_back(track->numberOfLostHits());
    trackData.Track_missInnerHits.push_back(track->missingInnerHits());
    trackData.Track_missOuterHits.push_back(track->missingOuterHits());
    trackData.Track_algo.push_back(track->algo());
    // trackData.Track_quality.push_back(track->quality());
    trackData.Track_charge.push_back(track->charge());
    trackData.Track_dxy.push_back(track->dxy(refPoint));
    trackData.Track_dz.push_back(track->dz(refPoint));
    trackData.Track_pt.push_back(track->pt());
    trackData.Track_eta.push_back(track->eta());
    trackData.Track_phi.push_back(track->phi());
    trackData.Track_dxyErr.push_back(track->dxyError());
    trackData.Track_dzErr.push_back(track->dzError());
    trackData.Track_ptErr.push_back(track->ptError());
    trackData.Track_etaErr.push_back(track->etaError());
    trackData.Track_phiErr.push_back(track->phiError());

    ROOT::Math::XYZVectorF tkMom(track->momentum().x(),track->momentum().y(),track->momentum().z());
    trackData.Track_momTk.push_back(tkMom);

    
    // ROOT::Math::XYZPointF tkPos(simTrack->trackerSurfacePosition().x(),
    // 				simTrack->trackerSurfacePosition().y(),
    // 				simTrack->trackerSurfacePosition().z());
    // trackData.SimTrack_posTk.push_back(tkPos);
    
    // ROOT::Math::XYZVectorF tkMom(simTrack->trackerSurfaceMomentum().px(),
    // 				 simTrack->trackerSurfaceMomentum().py(),
    // 				 simTrack->trackerSurfaceMomentum().pz());
    // trackData.SimTrack_momTk.push_back(tkMom);
  // std::cout << "Adding simtrack mom pt " << simTrack.trackerSurfaceMomentum().pt() 
  // 	    << " " << simTrack.momentum().pt() << std::endl;
  
    ROOT::Math::XYZVectorF mom(simTrack->momentum().px(),simTrack->momentum().py(),simTrack->momentum().pz());
    trackData.SimTrack_momentum.push_back(mom);
  
    trackData.SimTrack_type.push_back(simTrack->type());
    trackData.SimTrack_charge.push_back(simTrack->charge());
    trackData.SimTrack_trackInfo.push_back(simTrack->getTrackInfo());
    trackData.SimTrack_trackId.push_back(simTrack->trackId());
};

void TrackInfo::clear() {
    trackData.Track_chi2.clear();
    trackData.Track_ndof.clear();
    trackData.Track_validHits.clear();
    trackData.Track_lostHits.clear();
    trackData.Track_missInnerHits.clear();
    trackData.Track_missOuterHits.clear();
    trackData.Track_algo.clear();
    // trackData.Track_quality.clear();
    trackData.Track_charge.clear();
    trackData.Track_dxy.clear();
    trackData.Track_dz.clear();
    trackData.Track_pt.clear();
    trackData.Track_eta.clear();
    trackData.Track_phi.clear();
    trackData.Track_dxyErr.clear();
    trackData.Track_dzErr.clear();
    trackData.Track_ptErr.clear();
    trackData.Track_etaErr.clear();
    trackData.Track_phiErr.clear();
    trackData.Track_refPos.clear();
    trackData.Track_momTk.clear();
    
    // trackData.SimTrack_posTk.clear();
    // trackData.SimTrack_momTk.clear();
    trackData.SimTrack_momentum.clear();    
    trackData.SimTrack_type.clear();
    trackData.SimTrack_charge.clear();
    trackData.SimTrack_trackInfo.clear();
    trackData.SimTrack_trackId.clear();
    

};
