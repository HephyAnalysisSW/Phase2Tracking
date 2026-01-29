#include "Phase2Tracking/HitAnalyzer/interface/RecHitInfo.h"
#include "DataFormats/DetId/interface/DetId.h"
#include "DataFormats/Phase2TrackerCluster/interface/Phase2TrackerCluster1D.h"
#include "SimDataFormats/Track/interface/SimTrackContainer.h"
#include "DataFormats/GeometrySurface/interface/LocalError.h"
#include "DataFormats/GeometryVector/interface/LocalPoint.h"


void RecHitInfo::setBranches(TTree& tree) {
  tree.Branch("Hit_cluster_global_y",                   &recHitData.Hit_cluster_global_y);
  tree.Branch("Hit_cluster_global_z",                   &recHitData.Hit_cluster_global_z);
  tree.Branch("Hit_layer",                              &recHitData.Hit_layer);
  tree.Branch("Hit_ModuleType",                         &recHitData.Hit_ModuleType);
  tree.Branch("Hit_cluster_size",                       &recHitData.Hit_cluster_size);
  tree.Branch("Hit_cluster_SimTrack_size",              &recHitData.Hit_cluster_SimTrack_size);
  tree.Branch("Hit_cluster_local_x",                    &recHitData.Hit_cluster_local_x);
  tree.Branch("Hit_cluster_local_y",                    &recHitData.Hit_cluster_local_y);
  tree.Branch("Hit_cluster_local_z",                    &recHitData.Hit_cluster_local_z);
  tree.Branch("Hit_cluster_haveSimHit",                 &recHitData.Hit_cluster_haveSimHit);
  tree.Branch("Hit_cluster_closestSimHit_local_x",      &recHitData.Hit_cluster_closestSimHit_local_x);
  tree.Branch("Hit_cluster_closestSimHit_local_y",      &recHitData.Hit_cluster_closestSimHit_local_y);
  tree.Branch("Hit_cluster_closestSimHit_local_z",      &recHitData.Hit_cluster_closestSimHit_local_z);
  tree.Branch("Hit_det_rawid",                          &recHitData.Hit_det_rawid);
  tree.Branch("Hit_cluster_firstStrip",                 &recHitData.Hit_cluster_firstStrip);
  tree.Branch("Hit_cluster_firstRow",                   &recHitData.Hit_cluster_firstRow);
  tree.Branch("Hit_cluster_column",                     &recHitData.Hit_cluster_column);
  tree.Branch("Hit_cluster_edge",                       &recHitData.Hit_cluster_edge);
  tree.Branch("Hit_cluster_threshold",                  &recHitData.Hit_cluster_threshold);
  tree.Branch("localPos",	&recHitData.localPos);
  tree.Branch("globalPos",	&recHitData.globalPos);
  tree.Branch("localDir",	&recHitData.localDir);
  tree.Branch("globalDir",	&recHitData.globalDir);
  tree.Branch("path",	&recHitData.path);
  tree.Branch("theta",	&recHitData.theta);
  tree.Branch("phi",	&recHitData.phi);
  tree.Branch("pabs",	&recHitData.pabs);
  tree.Branch("tof",	&recHitData.tof);
  tree.Branch("energyLoss",	&recHitData.energyLoss);
  tree.Branch("processType",	&recHitData.processType);
  tree.Branch("particleType",	&recHitData.particleType);
  tree.Branch("layer",   &recHitData.layer);
  tree.Branch("moduleType",      &recHitData.moduleType);
  tree.Branch("detNormal",       &recHitData.detNormal);
  tree.Branch("trackId",	&recHitData.trackId);
  tree.Branch("nSimTracks",	&recHitData.nSimTracks);
};

std::vector<unsigned int> RecHitInfo::getSimTrackId(
    edm::Handle<edm::DetSetVector<PixelDigiSimLink> >& pixelSimLinks,
    const DetId& detId, unsigned int channel) {
  std::vector<unsigned int> retvec;
  edm::DetSetVector<PixelDigiSimLink>::const_iterator DSViter(pixelSimLinks->find(detId));
  if (DSViter == pixelSimLinks->end())
    return retvec;
  for (edm::DetSet<PixelDigiSimLink>::const_iterator it = DSViter->data.begin(); it != DSViter->data.end(); ++it) {
    if (channel == it->channel()) {
      retvec.push_back(it->SimTrackId());
    }
  }
  return retvec;
}

void RecHitInfo::fillSimHitInfo(const PSimHit& simHit) {
  //
  // Get the detector unit's id
  //
  DetId detId(simHit.detUnitId());
  unsigned int layer = (tTopo->side(detId) != 0) * 1000;  // don't split up endcap sides
  layer += tTopo->layer(detId);
  TrackerGeometry::ModuleType mType = tkGeom->getDetectorType(detId);
  // Get the geomdet
  const GeomDetUnit* geomDetUnit(tkGeom->idToDetUnit(detId));
  if (!geomDetUnit) {
	std::cout << "*** did not find geomDetUnit ***" << std::endl;
	return;
  }
  ROOT::Math::XYZPointF localPos(simHit.localPosition().x(),simHit.localPosition().y(),
				 simHit.localPosition().z());
  recHitData.localPos.push_back(localPos);
  GlobalPoint globalPosition(geomDetUnit->toGlobal(simHit.localPosition()));
  ROOT::Math::XYZPointF globalPos(globalPosition.x(),globalPosition.y(),globalPosition.z());
  recHitData.globalPos.push_back(globalPos);
  ROOT::Math::XYZVectorF localDir(simHit.localDirection().x(),simHit.localDirection().y(),
				  simHit.localDirection().z());
  recHitData.localDir.push_back(localDir);
  GlobalVector globalDirection(geomDetUnit->toGlobal(simHit.localDirection()));
  ROOT::Math::XYZVectorF globalDir(globalDirection.x(),globalDirection.y(),globalDirection.z());
  recHitData.globalDir.push_back(globalDir);
  ROOT::Math::XYZVectorF path(simHit.exitPoint().x()-simHit.entryPoint().x(),
			      simHit.exitPoint().y()-simHit.entryPoint().y(),
			      simHit.exitPoint().z()-simHit.entryPoint().z());
  recHitData.path.push_back(path);
  recHitData.theta.push_back(simHit.thetaAtEntry());
  recHitData.phi.push_back(simHit.phiAtEntry());
  recHitData.pabs.push_back(simHit.pabs());
  recHitData.tof.push_back(simHit.timeOfFlight());
  recHitData.energyLoss.push_back(simHit.energyLoss());
  recHitData.processType.push_back(simHit.processType());
  recHitData.particleType.push_back(simHit.particleType());
  recHitData.layer.push_back(layer);
  recHitData.moduleType.push_back((unsigned short)mType);
  GlobalVector detNormalGlobal(geomDetUnit->toGlobal(LocalVector(0.,0.,1.)));
  ROOT::Math::XYZVectorF detNormal(detNormalGlobal.x(),detNormalGlobal.y(),detNormalGlobal.z());
  recHitData.detNormal.push_back(detNormal);
  recHitData.trackId.push_back(simHit.trackId());
};


void RecHitInfo::fillRecHitInfo(const Phase2TrackerRecHit1D& recHit, unsigned int rawid,
				const GeomDetUnit* geomDetUnit,
				edm::Handle<edm::DetSetVector<PixelDigiSimLink> >* pixelSimLinks,
				std::map<unsigned int, SimTrack>& simTracks,
				edm::Handle<edm::PSimHitContainer>* simHitsRaw,
				bool debugHitMatch) {
  // get DetUnit
  DetId detId(rawid);
  unsigned int layer = (tTopo->side(detId) != 0) * 1000;  // don't split up endcap sides
  layer += tTopo->layer(detId);
  // determine the position
  LocalPoint localPosClu = recHit.localPosition();
  Global3DPoint globalPosClu = geomDetUnit->surface().toGlobal(localPosClu);
  const Bounds& bounds = geomDetUnit->surface().bounds();

  // Get the cluster from the rechit
  const Phase2TrackerCluster1D* clustIt = &*recHit.cluster();

  // Get all the simTracks that form the cluster
  std::vector<unsigned int> clusterSimTrackIds;
  for (unsigned int i(0); i < clustIt->size(); ++i) {
    unsigned int channel(Phase2TrackerDigi::pixelToChannel(clustIt->firstRow() + i, clustIt->column()));
    std::vector<unsigned int> simTrackIds_unselected(getSimTrackId(*pixelSimLinks, detId, channel));
    std::vector<unsigned int> simTrackIds;
    for (auto istId : simTrackIds_unselected) {
      std::map<unsigned int, SimTrack>::const_iterator istfind(simTracks.find(istId));
      if (istfind != simTracks.end())
	simTrackIds.push_back(istId);
    }
    for (unsigned int i = 0; i < simTrackIds.size(); ++i) {
      bool add = true;
      for (unsigned int j = 0; j < clusterSimTrackIds.size(); ++j) {
	// only save simtrackids that are not present yet
	if (simTrackIds.at(i) == clusterSimTrackIds.at(j))
	  add = false;
      }
      if (add)
	clusterSimTrackIds.push_back(simTrackIds.at(i));
    }
  }
  
  // find the closest simhit
  // this is needed because otherwise you get cases with simhits and clusters being swapped
  // when there are more than 1 cluster with common simtrackids
  const PSimHit* simhit = 0;  // bad naming to avoid changing code below. This is the closest simhit in x
  float minx = 10000;
  std::vector<const PSimHit*> trackSimHits;
  for (unsigned int simhitidx = 0; simhitidx < 2; ++simhitidx) {  // loop over both barrel and endcap hits
    for (edm::PSimHitContainer::const_iterator simhitIt(simHitsRaw[simhitidx]->begin());
	 simhitIt != simHitsRaw[simhitidx]->end();
	 ++simhitIt) {
      // check SimHit detId is the same with the RecHit
      if (rawid == simhitIt->detUnitId()) {
	auto it = std::lower_bound(clusterSimTrackIds.begin(), clusterSimTrackIds.end(), simhitIt->trackId());
	// check SimHit track id is included in the cluster
	if (it != clusterSimTrackIds.end() && *it == simhitIt->trackId()) {
	  trackSimHits.push_back(&*simhitIt);
	  if (!simhit || fabs(simhitIt->localPosition().x() - localPosClu.x()) < minx) {
	    minx = fabs(simhitIt->localPosition().x() - localPosClu.x());
	    simhit = &*simhitIt;
	  }
	}
      }
    }
  }
  if ( debugHitMatch ) {
    if ( trackSimHits.size()==0 || trackSimHits.size()>1 ) {
      TrackerGeometry::ModuleType mType = tkGeom->getDetectorType(detId);
      std::cout << "RecHit on rawid " << rawid <<", layer " << layer
		<< ", mType "<< (unsigned int)mType << std::endl;
      std::cout << "  localPos " << localPosClu.x() << " / " << localPosClu.y() << std::endl;
      LocalError localPosErr(recHit.localPositionError());
      std::cout << "  localErr " << sqrt(localPosErr.xx()) << " / " << sqrt(localPosErr.yy())
		<< " / " << localPosErr.xy()/sqrt(localPosErr.xx()*localPosErr.yy()) << std::endl;
      std::cout << "  width " << bounds.width() << ", length " << bounds.length()
		<< ", thickness " << bounds.thickness() << std::endl;
      std::cout << "  cluster size = " << recHit.cluster()->size() << std::endl;
      std::cout << "  track ids:";
      for ( auto itct=clusterSimTrackIds.begin(); itct!=clusterSimTrackIds.end(); ++itct )
	std::cout << " " << *itct;
      std::cout << std::endl;
      for ( auto itsh=trackSimHits.begin(); itsh!=trackSimHits.end(); ++itsh ) {
	std::cout << "  SimHit";
	if ( (*itsh)==simhit )  std::cout << "*";
	std::cout << ": track id " << (**itsh).trackId() << ", pabs = " << (**itsh).pabs()
		  << " loss " << (**itsh).energyLoss() << ", pdgId " << (**itsh).particleType()
		  << ", entry-exit (x) " << (**itsh).entryPoint().x() << " / " << (**itsh).exitPoint().x() << ", "
		  << ", entry-exit (y) " << (**itsh).entryPoint().y() << " / " << (**itsh).exitPoint().y() << std::endl;
      }
      if ( trackSimHits.size()==0 ) {
	for (unsigned int simhitidx = 0; simhitidx < 2; ++simhitidx) {  // loop over both barrel and endcap hits
	  for (edm::PSimHitContainer::const_iterator simhitIt(simHitsRaw[simhitidx]->begin());
	       simhitIt != simHitsRaw[simhitidx]->end(); ++simhitIt) {
	    // check SimHit detId is the same with the RecHit
	    if (rawid == simhitIt->detUnitId()) {
	      std::cout << " SimHit: pabs = " << simhitIt->pabs()
			<< " loss " << simhitIt->energyLoss() << ", pdgId " << simhitIt->particleType()
			<< ", entry-exit (x) " << simhitIt->entryPoint().x()
			<< " / " << simhitIt->exitPoint().x() << ", "
			<< ", entry-exit (y) " << simhitIt->entryPoint().y()
			<< " / " << simhitIt->exitPoint().y() << std::endl;
	    }
	  }
	}
      }
    }
  }

  recHitData.Hit_cluster_global_x.push_back(globalPosClu.x());
  recHitData.Hit_cluster_global_y.push_back(globalPosClu.y());
  recHitData.Hit_cluster_global_z.push_back(globalPosClu.z());
  recHitData.Hit_layer.push_back(layer);
  recHitData.Hit_ModuleType.push_back((unsigned short)(tkGeom->getDetectorType(detId)));
  recHitData.Hit_cluster_size.push_back(clustIt->size());
  recHitData.Hit_cluster_SimTrack_size.push_back(clusterSimTrackIds.size());
  recHitData.Hit_cluster_local_x.push_back(localPosClu.x());
  recHitData.Hit_cluster_local_y.push_back(localPosClu.y());
  recHitData.Hit_cluster_local_z.push_back(localPosClu.z());
  
  if (!simhit){
    recHitData.Hit_cluster_haveSimHit.push_back(false);
    recHitData.Hit_cluster_closestSimHit_local_x.push_back(999);
    recHitData.Hit_cluster_closestSimHit_local_y.push_back(999);
    recHitData.Hit_cluster_closestSimHit_local_z.push_back(999);
    ROOT::Math::XYZPointF emptyPoint(0.,0.,0.);
    ROOT::Math::XYZVectorF emptyVector(0.,0.,0.);
    recHitData.localPos.push_back(emptyPoint);
    recHitData.globalPos.push_back(emptyPoint);
    recHitData.localDir.push_back(emptyVector);
    recHitData.globalDir.push_back(emptyVector);
    recHitData.path.push_back(emptyVector);
    recHitData.theta.push_back(0.);
    recHitData.phi.push_back(0.);
    recHitData.pabs.push_back(0.);
    recHitData.tof.push_back(0.);
    recHitData.energyLoss.push_back(0.);
    recHitData.processType.push_back(0);
    recHitData.particleType.push_back(0);
    recHitData.layer.push_back(0);
    recHitData.moduleType.push_back(0);
    recHitData.detNormal.push_back(emptyVector);
    recHitData.trackId.push_back(0);
  }
  else {
    recHitData.Hit_cluster_haveSimHit.push_back(true);
    recHitData.Hit_cluster_closestSimHit_local_x.push_back(simhit->localPosition().x());
    recHitData.Hit_cluster_closestSimHit_local_y.push_back(simhit->localPosition().y());
    recHitData.Hit_cluster_closestSimHit_local_z.push_back(simhit->localPosition().z());
    fillSimHitInfo(*simhit);
  }
  recHitData.nSimTracks.push_back(clusterSimTrackIds.size());
  recHitData.Hit_det_rawid.push_back(rawid);
  recHitData.Hit_cluster_firstStrip.push_back(clustIt->firstStrip());
  recHitData.Hit_cluster_firstRow.push_back(clustIt->firstRow());
  recHitData.Hit_cluster_column.push_back(clustIt->column());
  recHitData.Hit_cluster_edge.push_back(clustIt->edge());
  recHitData.Hit_cluster_threshold.push_back(clustIt->threshold());
  
};
  
void RecHitInfo::clear() {
  recHitData.Hit_cluster_global_x.clear();
  recHitData.Hit_cluster_global_y.clear();
  recHitData.Hit_cluster_global_z.clear();
  recHitData.Hit_layer.clear();
  recHitData.Hit_ModuleType.clear();
  recHitData.Hit_cluster_size.clear();
  recHitData.Hit_cluster_SimTrack_size.clear();
  recHitData.Hit_cluster_local_x.clear();
  recHitData.Hit_cluster_local_y.clear();
  recHitData.Hit_cluster_local_z.clear();
  recHitData.Hit_cluster_haveSimHit.clear();
  recHitData.Hit_cluster_closestSimHit_local_x.clear();
  recHitData.Hit_cluster_closestSimHit_local_y.clear();
  recHitData.Hit_cluster_closestSimHit_local_z.clear();
  recHitData.Hit_det_rawid.clear();
  recHitData.Hit_cluster_firstStrip.clear();
  recHitData.Hit_cluster_firstRow.clear();
  recHitData.Hit_cluster_column.clear();
  recHitData.Hit_cluster_edge.clear();
  recHitData.Hit_cluster_threshold.clear();
  recHitData.localPos.clear();
  recHitData.globalPos.clear();
  recHitData.localDir.clear();
  recHitData.globalDir.clear();
  recHitData.path.clear();
  recHitData.theta.clear();
  recHitData.phi.clear();
  recHitData.pabs.clear();
  recHitData.tof.clear();
  recHitData.energyLoss.clear();
  recHitData.processType.clear();
  recHitData.particleType.clear();
  recHitData.layer.clear();
  recHitData.moduleType.clear();
  recHitData.detNormal.clear();
  recHitData.trackId.clear();
  recHitData.nSimTracks.clear();
};
