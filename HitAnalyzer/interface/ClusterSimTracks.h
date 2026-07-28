#ifndef HITANALYZER_CLUSTERSIMTRACKS_H
#define HITANALYZER_CLUSTERSIMTRACKS_H

#include "SimDataFormats/TrackerDigiSimLink/interface/PixelDigiSimLink.h"
#include "DataFormats/Phase2TrackerCluster/interface/Phase2TrackerCluster1D.h"
/* #include "DataFormats/TrackerRecHit2D/interface/Phase2TrackerRecHit1D.h" */
#include "SimDataFormats/TrackerDigiSimLink/interface/PixelDigiSimLink.h"
#include "DataFormats/DetId/interface/DetId.h"
#include "DataFormats/Common/interface/DetSetVector.h"

class ClusterSimTracks {
  //
  // Class to return (and cache) SimTrack ids for a cluster
  //
 public:
  
 ClusterSimTracks(const Phase2TrackerCluster1D& cluster, const DetId& detId,
		  const edm::DetSetVector<PixelDigiSimLink>& pixelSimLinks):
  cluster_(cluster), detId_(detId), pixelSimLinks_(pixelSimLinks), simTracksValid_(false) {};

  //
  // Get SimTrack ids for specific channel
  //
  std::set<unsigned int> simTrackIdsPerChannel(unsigned int channel) const;
  //
  // Check if SimTrack id contributed to cluster
  //
  bool simTrackInCluster(unsigned int simTrackId) const;
  //
  // All SimTrack ids contributing to cluster
  //
  const std::set<unsigned int>& simTrackIds() const;
  //
  // Access to DetId (for reference)
  //
  const DetId& detId() const {return detId_;};
  //
  // Verify if DetId matches with current object
  //
  bool sameDet(const DetId& detId) const {return detId_==detId;};
  
 private:
  const Phase2TrackerCluster1D& cluster_;                    // Pointer to cluster
  const DetId detId_;                                        // DetId (for reference)
  const edm::DetSetVector<PixelDigiSimLink>& pixelSimLinks_; // PixelDigiSimLinks for finding SimTrack contributions
  mutable bool simTracksValid_;                              // Has cache been filled?
  mutable std::set<unsigned int> simTrackIds_;               // Cache of all SimTrack ids
};
#endif
