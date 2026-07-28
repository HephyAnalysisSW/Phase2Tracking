#include "Phase2Tracking/HitAnalyzer/interface/CommonHitInfo.h"
#include "DataFormats/DetId/interface/DetId.h"

// #include <iostream>

// #include <stacktrace>


std::vector<unsigned int> CommonHitInfo::getSimTrackId(const DetId& detId, unsigned int channel) {
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

void CommonHitInfo::fillSimHitsPerDet(const std::vector<const edm::PSimHitContainer*>& simHitsRaw) {
  //
  // fill map of SimHits / detId
  //
  simHitsPerDet_.clear();
  // for (unsigned int simhitidx = 0; simhitidx < 2; ++simhitidx) {  // loop over both barrel and endcap hits
  //   // std::cout<< simhitidx << " " << simHitsRaw[simhitidx]->size() << std::endl;
  //   for (edm::PSimHitContainer::const_iterator simhitIt(simHitsRaw[simhitidx]->begin());
  //	 simhitIt != simHitsRaw[simhitidx]->end(); ++simhitIt) {
  // loop over both barrel and endcap hits
  for (auto simhitsIt=simHitsRaw.begin(); simhitsIt!=simHitsRaw.end(); ++simhitsIt) {
    for (auto simhitIt=(**simhitsIt).begin(); simhitIt!=(**simhitsIt).end(); ++simhitIt) {
      const PSimHit* simhit(&*simhitIt);
      unsigned int rawid(simhit->detUnitId());
      DetSimHitsMap::iterator idet(simHitsPerDet_.find(rawid));
      if ( idet!=simHitsPerDet_.end() ) {
	// std::cout << "CommonHitInfoadding sim entry for det id " << rawid << std::endl;
	idet->second.push_back(simhit);
      }
      else {
	// std::cout << "CommonHitInfonew sim entry for det id " << rawid << std::endl;
	simHitsPerDet_.insert(DetSimHitsPair(rawid,std::vector<const PSimHit*>{simhit}));
      }
    }
  }
  // for (auto it(simHitsPerDet_.begin()); it!=simHitsPerDet_.end(); ++it ) {
  //   std::cout << it->second.size() << " sim hits for det id "<< it->first << std::endl;
  // }
  // std::cout << std::endl;

};

void CommonHitInfo::fillRecHitsPerDet(const Phase2TrackerRecHit1DCollectionNew& rechits) {
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
	  // std::cout << "CommonHitInfoadding rec entry for det id " << rawid << std::endl;
	  idet->second.push_back(rechit);
	}
	else {
	  // std::cout << "CommonHitInfonew rec entry for det id " << rawid << std::endl;
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

//const Phase2TrackerRecHit1D* CommonHitInfo::matchRecHitOnDet(const PSimHit* simHit, const DetId& detId,
//							  const std::vector<const Phase2TrackerRecHit1D*>& detRecHits) {
CommonHitInfo::RecHitDistancePairs
CommonHitInfo::matchRecHitOnDet(const PSimHit* simHit, const DetId& detId,
			     const std::vector<const Phase2TrackerRecHit1D*>& detRecHits) {
  //
  // loop over RecHits (assumes simHit and detRecHits are on the same DetUnit!!)
  //
  // std::cout << "CommonHitInfo  Checking SimHit at " << simHit << " detid " << simHit->detUnitId() << " loc pos "
  // 		<< simHit->localPosition().x() << " / " << simHit->localPosition().y() << std::endl;
  //  const Phase2TrackerRecHit1D* rechit(0);
  //  std::vector< const Phase2TrackerRecHit1D* rechit(0);
  //
  // prepare result
  //
  CommonHitInfo::RecHitDistancePairs matchedRecHits;
  //
  // restart cache of ClusterSimTracks objects with new detid (only useful
  //   if SimHits on same Det are treated in sequence)
  //
  if ( cstByCluster_.size()>0 ) {
    const ClusterSimTracks& cst = cstByCluster_.begin()->second;
    // std::cout << "  Existing *detId = " << &cst.detId() << " " << cst.detId().rawId() <<
    //   " / new *detId = " << &detId << " " << detId.rawId() << std::endl;
    if ( !cst.sameDet(detId) ) {
      // std::cout << "  Changed DetId" << std::endl;
      cstByCluster_.clear();
    }
  }
  // else {
  //   std::cout << "  cstByCluster is empty" << std::endl;
  // }
    
  // float dxmin(1.e30);
  for ( std::vector<const Phase2TrackerRecHit1D*>::const_iterator irh=detRecHits.begin();
	irh!=detRecHits.end(); ++irh ) {
    // Get the cluster from the rechit and loop over channels
    RecHitClusterMap::const_iterator icl(clustersByHit_.find(*irh));
    const Phase2TrackerCluster1D* clusterPtr(0);
    if ( icl==clustersByHit_.end() ) {
      clusterPtr = &(*(**irh).cluster());
      clustersByHit_.insert(std::pair<const Phase2TrackerRecHit1D*, const Phase2TrackerCluster1D*>(*irh,clusterPtr));
    }
    else {
      clusterPtr = icl->second;
    }
    const Phase2TrackerCluster1D& cluster = *(**irh).cluster();

    const ClusterSimTracks* cst(0);
    ClusterSimTracksMap::const_iterator cstit = cstByCluster_.find(&cluster);
    // std::cout << "  #entries of cstByCluster_ = " << cstByCluster_.size() << std::endl;
    // for ( auto it=cstByCluster_.begin(); it!=cstByCluster_.end(); ++it )
    //   std::cout << "   cluster pointer = " << it->first << " cst pointer " << &(it->second) 
    // 		<< " rawid " << (it->second).detId().rawId() << std::endl;
    if ( cstit==cstByCluster_.end() ) {
      // std::cout << "    Adding CST for cluster at " << &cluster << " on det " << detId << std::endl;
      cstit =
	cstByCluster_.insert({&cluster,ClusterSimTracks(cluster,detId,*pixelSimLinks)}).first;
    }
    // else {
    //   std::cout << "    Reusing CST for cluster at " << &cluster << " on det " << detId << std::endl;
    // }
    cst = &(cstit->second);
    // ClusterSimTracks cSimTrackIds(cluster,detId,*pixelSimLinks);
    bool matched = cst->simTrackInCluster(simHit->trackId());
    // // std::cout << "CommonHitInfo      cluster size " << cluster.size() << std::endl;
    // // std::cout << "CommonHitInfo    Checking RecHit at " << *irh
    // // 	      << " 1st strip " << (**irh).cluster()->firstStrip()
    // // 	      << " 1st row " << (**irh).cluster()->firstRow()
    // // 	      << " columns "<< (**irh).cluster()->column()
    // // 	      << " detid " << (**irh).geographicalId() << std::endl;
    // bool matched(false);
    // for (unsigned int i(0); i < cluster.size(); ++i) {
    //   // std::cout << "CommonHitInfo        channel " << i << std::endl;
    //   // const Phase2TrackerCluster1D& cluster = *(**irh).cluster();
    //   // // std::cout << "CommonHitInfo      cluster size " << cluster.size() << std::endl;
    //   // find SimTracks contributing to the channel
    //   unsigned int channel(Phase2TrackerDigi::pixelToChannel(cluster.firstRow() + i, cluster.column()));
    //   std::vector<unsigned int> simTrackIds = getSimTrackId(detId,channel);
    //   // // std::cout << "CommonHitInfo          " << simTrackIds.size() << " simTracks" << std::endl;
    //   matched = std::find(simTrackIds.begin(),simTrackIds.end(),(*simHit).trackId())!=simTrackIds.end();
    //   // if match was found: consider RecHit
    //   // std::cout << "CommonHitInfo        matched : " << matched << std::endl;
    //   if ( matched ) break;
    // }
    //
    // select closest RecHit
    //
    if ( matched ) {
      float dx = fabs((**irh).localPosition().x()-(*simHit).localPosition().x());
      matchedRecHits.push_back(RecHitDistancePair(&(**irh),dx));
      // // std::cout << "CommonHitInfo      dx, dxmin " << dx << " " << dxmin;
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

