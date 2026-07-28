#include "Phase2Tracking/HitAnalyzer/interface/ClusterSimTracks.h"
// #include "Phase2Tracking/HitAnalyzer/interface/CommonHitInfo.h"
// #include "DataFormats/DetId/interface/DetId.h"
//
// return SimTrack ids for a given DetId / channel
//
std::set<unsigned int> ClusterSimTracks::simTrackIdsPerChannel(unsigned int channel) const {
  std::set<unsigned int> result;
  edm::DetSetVector<PixelDigiSimLink>::const_iterator DSViter(pixelSimLinks_.find(detId_));
  if (DSViter == pixelSimLinks_.end())  return result;
  for (edm::DetSet<PixelDigiSimLink>::const_iterator it = DSViter->data.begin(); it != DSViter->data.end(); ++it) {
    if (channel == it->channel()) {
      result.insert(it->SimTrackId());
    }
  }
  return result;
};

bool ClusterSimTracks::simTrackInCluster(unsigned int simTrackId) const {
  //
  // Return true if <simTrackId> contributed to one or more channels of <cluster>
  //
  // caching handled by simTrackIds()
  //
  const std::set<unsigned int>& trackIds = simTrackIds();
  
  return std::find(trackIds.begin(),trackIds.end(),simTrackId)!=trackIds.end();
};

const std::set<unsigned int>& ClusterSimTracks::simTrackIds() const {  
  //
  // List of all SimTrackIds associated to this cluster
  //
  if ( simTracksValid_ )  return simTrackIds_;
  //
  // Loop over all channels
  //
  for ( unsigned int ic=0; ic<cluster_.size(); ++ic ) {
    // get channel number
    unsigned int channel(Phase2TrackerDigi::pixelToChannel(cluster_.firstRow()+ic, cluster_.column()));
    // get SimTrackIds for this channel
    std::set<unsigned int> trackIds(simTrackIdsPerChannel(channel));
    simTrackIds_.insert(trackIds.begin(),trackIds.end());
  }

  simTracksValid_ = true;
  return simTrackIds_;
};
