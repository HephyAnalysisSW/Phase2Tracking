#include "Phase2Tracking/HitAnalyzer/interface/SimHitInfo.h"
#include "DataFormats/DetId/interface/DetId.h"

// #include <iostream>

// #include <stacktrace>

void SimHitInfo::setBranches(TTree& tree) {
  tree.Branch("localPos",&simHitData.localPos);
  tree.Branch("globalPos",&simHitData.globalPos);
  tree.Branch("localDir",&simHitData.localDir);
  tree.Branch("globalDir",&simHitData.globalDir);
  tree.Branch("path",&simHitData.path);
  tree.Branch("theta",&simHitData.theta);
  tree.Branch("phi",&simHitData.phi);
  tree.Branch("pabs",&simHitData.pabs);
  tree.Branch("tof",&simHitData.tof);
  tree.Branch("energyLoss",&simHitData.energyLoss);
  tree.Branch("processType",&simHitData.processType);
  tree.Branch("particleType",&simHitData.particleType);
  tree.Branch("layer",&simHitData.layer);
  tree.Branch("moduleType",&simHitData.moduleType);
  tree.Branch("detNormal",&simHitData.detNormal);
  tree.Branch("trackId",&simHitData.trackId);
  tree.Branch("trackType",&simHitData.trackType);
  tree.Branch("trackMom",&simHitData.trackMom);
  tree.Branch("hasRecHit",&simHitData.hasRecHit);

  tree.Branch("rhNMatched",&simHitData.rhNMatched);
  tree.Branch("rhLocalPos",&simHitData.rhLocalPos);
  tree.Branch("rhLocalErr",&simHitData.rhLocalErr);
  tree.Branch("rhGlobalPos",&simHitData.rhGlobalPos);
  // tree.Branch("Hit_layer",                              &simHitData.Hit_layer);
  // tree.Branch("Hit_ModuleType",                         &simHitData.Hit_ModuleType);
  tree.Branch("clusterSize",                       &simHitData.clusterSize);
  tree.Branch("detRawId",                          &simHitData.detRawId);
  tree.Branch("clusterFirstStrip",                 &simHitData.clusterFirstStrip);
  tree.Branch("clusterFirstRow",                   &simHitData.clusterFirstRow);
  tree.Branch("clusterColumn",                     &simHitData.clusterColumn);
  tree.Branch("clusterEdge",                       &simHitData.clusterEdge);
  tree.Branch("clusterThreshold",                  &simHitData.clusterThreshold);
};

std::vector<unsigned int> SimHitInfo::getSimTrackId(const DetId& detId, unsigned int channel) {
  std::vector<unsigned int> retvec;
  edm::DetSetVector<PixelDigiSimLink>::const_iterator DSViter(pixelSimLinks->find(detId));
  if (DSViter == pixelSimLinks->end())  return retvec;
  for (edm::DetSet<PixelDigiSimLink>::const_iterator it = DSViter->data.begin(); it != DSViter->data.end(); ++it) {
    if (channel == it->channel()) {
      retvec.push_back(it->SimTrackId());
    }
  }
  return retvec;
};

void SimHitInfo::fillSimHitsPerDet(edm::Handle<edm::PSimHitContainer> *simHitsRaw) {
  //
  // fill map of SimHits / detId
  //
  simHitsPerDet_.clear();
  for (unsigned int simhitidx = 0; simhitidx < 2; ++simhitidx) {  // loop over both barrel and endcap hits
    // std::cout << simhitidx << " " << simHitsRaw[simhitidx]->size() << std::endl;
    for (edm::PSimHitContainer::const_iterator simhitIt(simHitsRaw[simhitidx]->begin());
	 simhitIt != simHitsRaw[simhitidx]->end(); ++simhitIt) {
      const PSimHit* simhit(&*simhitIt);
      unsigned int rawid(simhit->detUnitId());
      DetSimHitsMap::iterator idet(simHitsPerDet_.find(rawid));
      if ( idet!=simHitsPerDet_.end() ) {
	// std::cout << "SimHitInfoadding sim entry for det id " << rawid << std::endl;
	idet->second.push_back(simhit);
      }
      else {
	// std::cout << "SimHitInfonew sim entry for det id " << rawid << std::endl;
	simHitsPerDet_.insert(DetSimHitsPair(rawid,std::vector<const PSimHit*>{simhit}));
      }
    }
  }
  // for (auto it(simHitsPerDet_.begin()); it!=simHitsPerDet_.end(); ++it ) {
  //   std::cout << it->second.size() << " sim hits for det id "<< it->first << std::endl;
  // }
  // std::cout << std::endl;

};

void SimHitInfo::fillRecHitsPerDet(const Phase2TrackerRecHit1DCollectionNew& rechits) {
  //
  // create map of RecHits
  //
  recHitsPerDet_.clear();
  for (Phase2TrackerRecHit1DCollectionNew::const_iterator DSViter = rechits.begin();
       DSViter != rechits.end(); ++DSViter) {
    // Get the detector unit's id
    unsigned int rawid(DSViter->detId());
    // only consider dets with SimHits
    if ( simHitsPerDet_.find(rawid)!=simHitsPerDet_.end() ) {
      // Loop over the rechits in the detector unit
      for (edmNew::DetSet<Phase2TrackerRecHit1D>::const_iterator rechitIt = DSViter->begin();
	   rechitIt != DSViter->end(); ++rechitIt) {
	const Phase2TrackerRecHit1D* rechit(&*rechitIt);
	DetRecHitsMap::iterator idet(recHitsPerDet_.find(rawid));
	if ( idet!=recHitsPerDet_.end() ) {
	  // std::cout << "SimHitInfoadding rec entry for det id " << rawid << std::endl;
	  idet->second.push_back(rechit);
	}
	else {
	  // std::cout << "SimHitInfonew rec entry for det id " << rawid << std::endl;
	  recHitsPerDet_.insert(DetRecHitsPair(rawid,std::vector<const Phase2TrackerRecHit1D*>{rechit}));
	}
      }
      
    }
  }
  // for (auto it(recHitsPerDet_.begin()); it!=recHitsPerDet_.end(); ++it ) {
  //   std::cout << it->second.size() << " rec hits for det id "<< it->first << std::endl;
  // }
  // std::cout << std::endl;

};

//const Phase2TrackerRecHit1D* SimHitInfo::matchRecHitOnDet(const PSimHit* simHit, const DetId& detId,
//							  const std::vector<const Phase2TrackerRecHit1D*>& detRecHits) {
SimHitInfo::RecHitDistancePairs
SimHitInfo::matchRecHitOnDet(const PSimHit* simHit, const DetId& detId,
			     const std::vector<const Phase2TrackerRecHit1D*>& detRecHits) {
  //
  // loop over RecHits (assumes simHit and detRecHits are on the same DetUnit!!)
  //
  // std::cout << "SimHitInfo  Checking SimHit at " << simHit << " detid " << simHit->detUnitId() << " loc pos "
  // 		<< simHit->localPosition().x() << " / " << simHit->localPosition().y() << std::endl;
  //  const Phase2TrackerRecHit1D* rechit(0);
  //  std::vector< const Phase2TrackerRecHit1D* rechit(0);
  SimHitInfo::RecHitDistancePairs matchedRecHits;
  
  // float dxmin(1.e30);
  for ( std::vector<const Phase2TrackerRecHit1D*>::const_iterator irh=detRecHits.begin();
	irh!=detRecHits.end(); ++irh ) {
    // std::cout << "SimHitInfo    Checking RecHit at " << *irh
    // 	      << " 1st strip " << (**irh).cluster()->firstStrip()
    // 	      << " 1st row " << (**irh).cluster()->firstRow()
    // 	      << " columns "<< (**irh).cluster()->column()
    // 	      << " detid " << (**irh).geographicalId() << std::endl;
    bool matched(false);
    // Get the cluster from the rechit and loop over channels
    const Phase2TrackerCluster1D& cluster = *(**irh).cluster();
    // std::cout << "SimHitInfo      cluster size " << cluster.size() << std::endl;
    for (unsigned int i(0); i < cluster.size(); ++i) {
      // std::cout << "SimHitInfo        channel " << i << std::endl;
      // find SimTracks contributing to the channel
      unsigned int channel(Phase2TrackerDigi::pixelToChannel(cluster.firstRow() + i, cluster.column()));
      std::vector<unsigned int> simTrackIds = getSimTrackId(detId,channel);
      // // std::cout << "SimHitInfo          " << simTrackIds.size() << " simTracks" << std::endl;
      matched = std::find(simTrackIds.begin(),simTrackIds.end(),(*simHit).trackId())!=simTrackIds.end();
      // if match was found: consider RecHit
      // std::cout << "SimHitInfo        matched : " << matched << std::endl;
      if ( matched ) break;
    }
    //
    // select closest RecHit
    //
    if ( matched ) {
      float dx = fabs((**irh).localPosition().x()-(*simHit).localPosition().x());
      matchedRecHits.push_back(RecHitDistancePair(&(**irh),dx));
      // // std::cout << "SimHitInfo      dx, dxmin " << dx << " " << dxmin;
      // if ( !rechit || dx<dxmin ) {
      // 	dxmin = dx;
      // 	rechit = &(**irh);
      // 	// std::cout << " ***";
      // }
      // // std::cout << std::endl;
    }
  }
  //
  // sort result
  //
  std::sort(matchedRecHits.begin(),matchedRecHits.end(),[](const RecHitDistancePair& a, const RecHitDistancePair& b)
	    {
	      return a.second<b.second;
	    });
  return matchedRecHits;
};

void SimHitInfo::fillSimHitInfo(const PSimHit& simHit) {
  //
  // Get the detector unit's id
  //
  unsigned int rawid(simHit.detUnitId());
  DetId detId(rawid);
  unsigned int layer = (tTopo_->side(detId) != 0) * 1000;  // don't split up endcap sides
  layer += tTopo_->layer(detId);
  TrackerGeometry::ModuleType mType = tkGeom_->getDetectorType(detId);
  // Get the geomdet
  const GeomDetUnit* geomDetUnit(tkGeom_->idToDetUnit(detId));
  if (!geomDetUnit) {
    std::cout << "SimHitInfo*** did not find geomDetUnit ***" << std::endl;
    return;
  }
  ROOT::Math::XYZPointF localPos(simHit.localPosition().x(),simHit.localPosition().y(),
				 simHit.localPosition().z());
  simHitData.localPos.push_back(localPos);
  GlobalPoint globalPosition(geomDetUnit->toGlobal(simHit.localPosition()));
  ROOT::Math::XYZPointF globalPos(globalPosition.x(),globalPosition.y(),globalPosition.z());
  simHitData.globalPos.push_back(globalPos);
  ROOT::Math::XYZVectorF localDir(simHit.localDirection().x(),simHit.localDirection().y(),
				  simHit.localDirection().z());
  simHitData.localDir.push_back(localDir);
  GlobalVector globalDirection(geomDetUnit->toGlobal(simHit.localDirection()));
  ROOT::Math::XYZVectorF globalDir(globalDirection.x(),globalDirection.y(),globalDirection.z());
  simHitData.globalDir.push_back(globalDir);
  ROOT::Math::XYZVectorF path(simHit.exitPoint().x()-simHit.entryPoint().x(),
			      simHit.exitPoint().y()-simHit.entryPoint().y(),
			      simHit.exitPoint().z()-simHit.entryPoint().z());
  simHitData.path.push_back(path);
  simHitData.theta.push_back(simHit.thetaAtEntry());
  simHitData.phi.push_back(simHit.phiAtEntry());
  simHitData.pabs.push_back(simHit.pabs());
  simHitData.tof.push_back(simHit.timeOfFlight());
  simHitData.energyLoss.push_back(simHit.energyLoss());
  simHitData.processType.push_back(simHit.processType());
  simHitData.particleType.push_back(simHit.particleType());
  simHitData.layer.push_back(layer);
  simHitData.moduleType.push_back((unsigned short)mType);
  GlobalVector detNormalGlobal(geomDetUnit->toGlobal(LocalVector(0.,0.,1.)));
  ROOT::Math::XYZVectorF detNormal(detNormalGlobal.x(),detNormalGlobal.y(),detNormalGlobal.z());
  simHitData.detNormal.push_back(detNormal);
  
  simHitData.trackId.push_back(simHit.trackId());
  TrackIdSimTrackMap::const_iterator itSimTrack(simTracksById_->find(simHit.trackId()));
  if ( itSimTrack!=simTracksById_->end() ) {
    // std::cout << "trackIds " << simHit.trackId() << " " << itSimTrack->first << " / "
    //      << "types " << simHit.particleType() << " " << itSimTrack->second.type() << std::endl;
    simHitData.trackType.push_back(itSimTrack->second.type());
    const math::XYZTLorentzVectorD& tkMom(itSimTrack->second.momentum());
    simHitData.trackMom.push_back(ROOT::Math::XYZVectorF(tkMom.x(),tkMom.y(),tkMom.z()));
  }
  else {
    simHitData.trackType.push_back(0);
    simHitData.trackMom.push_back(ROOT::Math::XYZVectorF(0.,0.,0.));
  }


  const Phase2TrackerRecHit1D* rechit(0);
  DetRecHitsMap::const_iterator ivrh = recHitsPerDet_.find(rawid);
  // if ( ivrh==recHitsPerDet_.end() ) {
    // std::cout << "SimHitInfo- Skipping det - no RecHits" << std::endl;
  // }
  // else {
  unsigned int nMatched(0);
  if ( ivrh!=recHitsPerDet_.end() ) {
    //
    // find all rechits with contributions from the SimTrack related to simHit
    //
    RecHitDistancePairs matchedRecHits = matchRecHitOnDet(&simHit,detId,ivrh->second);
    // ////
    // if ( matchedRecHits.size()>50 ) {
    //   std::cout << "SimHit with " << matchedRecHits.size() << " matched hits" << std::endl;
    //   std::cout << "   " << "at " << &simHit << " detid " << simHit.detUnitId() << " loc pos "
    // 	   << simHit.localPosition().x() << " / " << simHit.localPosition().y() << std::endl;
    //   std::cout << "   " << "entry " << simHit.entryPoint().x() << " / " << simHit.entryPoint().y()
    // 		<< " ; exit "  << simHit.exitPoint().x() << " / " << simHit.exitPoint().y() << std::endl;
    //   std::cout << "   " << "trackId " << simHit.trackId() << " ; pType "  << simHit.particleType()
    // 		<< " ; pabs " << simHit.pabs() << std::endl;
    //   for ( SimHitInfo::RecHitDistancePairs::const_iterator irrr=matchedRecHits.begin();
    // 	    irrr!=matchedRecHits.end(); ++irrr ) {
    // 	std::cout << "  RecHit on detid " << irrr->first->geographicalId() << " loc pos "
    // 	   << irrr->first->localPosition().x() << " / " << irrr->first->localPosition().y() << std::endl;
    // 	const Phase2TrackerCluster1D& cluster = *(irrr->first->cluster());
    // 	std::cout << "     first row / column " << cluster.firstRow() << " / " << cluster.column() << std::endl;
    //   }
    // }
    // ////
    // store best match (if any)
    nMatched = matchedRecHits.size();
    if ( nMatched>0 )  rechit = matchedRecHits[0].first;
    // rechit = matchRecHitOnDet(&simHit,detId,ivrh->second);
    // std::cout << "SimHitInfo.. matched RecHit at " << rechit << std::endl;
  }
  simHitData.rhNMatched.push_back(nMatched);
  if ( rechit ) {
    simHitData.hasRecHit.push_back(true);
    ROOT::Math::XYZPointF localPos(rechit->localPosition().x(),rechit->localPosition().y(),
				   rechit->localPosition().z());
    simHitData.rhLocalPos.push_back(localPos);
    ROOT::Math::XYZVectorF localErr(sqrt(rechit->localPositionError().xx()),
				    sqrt(rechit->localPositionError().yy()),0.);
    simHitData.rhLocalErr.push_back(localErr);
    ROOT::Math::XYZPointF globalPos(rechit->globalPosition().x(),rechit->globalPosition().y(),
				    rechit->globalPosition().z());
    simHitData.rhGlobalPos.push_back(globalPos);
    simHitData.detRawId.push_back(rawid);

    const Phase2TrackerCluster1D& clustIt = *(rechit->cluster());
    simHitData.clusterSize.push_back(clustIt.size());
    // simHitData.clusterNSimTracks.push_back(clusterSimTrackIds.size());
    simHitData.clusterFirstStrip.push_back(clustIt.firstStrip());
    simHitData.clusterFirstRow.push_back(clustIt.firstRow());
    simHitData.clusterColumn.push_back(clustIt.column());
    simHitData.clusterEdge.push_back(clustIt.edge());
    simHitData.clusterThreshold.push_back(clustIt.threshold());
  }
  else {
    simHitData.hasRecHit.push_back(false);
    simHitData.rhLocalPos.push_back(ROOT::Math::XYZPointF(0.,0.,0.));
    simHitData.rhLocalErr.push_back(ROOT::Math::XYZVectorF(0.,0.,0.));
    simHitData.rhGlobalPos.push_back(ROOT::Math::XYZPointF(0.,0.,0.));
    simHitData.clusterSize.push_back(0);
    // simHitData.clusterNSimTracks.push_back(0);
    simHitData.detRawId.push_back(0);
    simHitData.clusterFirstStrip.push_back(0);
    simHitData.clusterFirstRow.push_back(0);
    simHitData.clusterColumn.push_back(0);
    simHitData.clusterEdge.push_back(0);
    simHitData.clusterThreshold.push_back(0);
  }

};


void SimHitInfo::clear() {
  simHitData.localPos.clear();
  simHitData.globalPos.clear();
  simHitData.localDir.clear();
  simHitData.globalDir.clear();
  simHitData.path.clear();
  simHitData.theta.clear();
  simHitData.phi.clear();
  simHitData.pabs.clear();
  simHitData.tof.clear();
  simHitData.energyLoss.clear();
  simHitData.processType.clear();
  simHitData.particleType.clear();
  simHitData.layer.clear();
  simHitData.moduleType.clear();
  simHitData.detNormal.clear();
  simHitData.trackId.clear();
  simHitData.trackType.clear();
  simHitData.trackMom.clear();
  simHitData.hasRecHit.clear();

  simHitData.rhNMatched.clear();
  simHitData.rhLocalPos.clear();
  simHitData.rhLocalErr.clear();
  simHitData.rhGlobalPos.clear();
  // simHitData.Hit_layer.clear();
  // simHitData.Hit_ModuleType.clear();
  simHitData.clusterSize.clear();
  // simHitData.clusterNSimTracks.clear();
  simHitData.detRawId.clear();
  simHitData.clusterFirstStrip.clear();
  simHitData.clusterFirstRow.clear();
  simHitData.clusterColumn.clear();
  simHitData.clusterEdge.clear();
  simHitData.clusterThreshold.clear();
};

