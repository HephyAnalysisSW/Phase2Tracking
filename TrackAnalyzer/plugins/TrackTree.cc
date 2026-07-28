// This is largely copied from https://github.com/cms-sw/cmssw/blob/master/RecoLocalTracker/Phase2TrackerRecHits/test/RecHitsValidation.cc

#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "CommonTools/Utils/interface/TFileDirectory.h"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "FWCore/Framework/interface/ConsumesCollector.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/PluginManager/interface/ModuleDef.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/Math/interface/deltaR.h"

#include "Phase2Tracking/TrackAnalyzer/interface/TrackInfo.h"

#include "TTree.h"

class TrackTree : public edm::one::EDAnalyzer<edm::one::SharedResources> {
  public:
    explicit TrackTree(const edm::ParameterSet&);
    void analyze(const edm::Event&, const edm::EventSetup&);

  private:
    virtual void beginJob() override;
    virtual void endJob() override;
    void initEventStructure();
    // std::vector<unsigned int> getSimTrackId(edm::Handle<edm::DetSetVector<PixelDigiSimLink> >&,
    // 					    const DetId&, unsigned int);


    // const edm::ESGetToken<TrackerGeometry, TrackerDigiGeometryRecord> esTokenGeom_;
    // const edm::ESGetToken<TrackerTopology, TrackerTopologyRcd> esTokenTopo_;
    // const edm::EDGetTokenT<Phase2TrackerRecHit1DCollectionNew> tokenRecHits_;
    // const edm::EDGetTokenT<Phase2TrackerCluster1DCollectionNew> tokenClusters_;
    // const edm::EDGetTokenT<edm::DetSetVector<PixelDigiSimLink> > tokenLinks_;
    // const edm::EDGetTokenT<edm::PSimHitContainer> tokenSimHitsB_;
    // const edm::EDGetTokenT<edm::PSimHitContainer> tokenSimHitsE_;
    const edm::EDGetTokenT<reco::TrackCollection> tokenRecTracks_;
    const edm::EDGetTokenT<edm::SimTrackContainer> tokenSimTracks_;
    const edm::EDGetTokenT<edm::SimVertexContainer> tokenSimVertices_;

    // std::vector<edm::EDGetTokenT<edm::PSimHitContainer>> shInfoSimHitTokens_;
    // std::vector<edm::EDGetTokenT<edm::PSimHitContainer>> rhInfoSimHitTokens_;

    // const double simtrackminpt_;

    TrackInfo trackInfo_;
  
    TTree* trackTree_;

};

// std::vector<unsigned int> TrackTree::getSimTrackId(edm::Handle<edm::DetSetVector<PixelDigiSimLink> >& pixelSimLinks,
// 						      const DetId& detId, unsigned int channel) {
//   std::vector<unsigned int> retvec;
//   edm::DetSetVector<PixelDigiSimLink>::const_iterator DSViter(pixelSimLinks->find(detId));
//   if (DSViter == pixelSimLinks->end())  return retvec;
//   for (edm::DetSet<PixelDigiSimLink>::const_iterator it = DSViter->data.begin(); it != DSViter->data.end(); ++it) {
//     if (channel == it->channel()) {
//       retvec.push_back(it->SimTrackId());
//     }
//   }
//   return retvec;
// };


TrackTree::TrackTree(const edm::ParameterSet& cfg)
  // : esTokenGeom_(esConsumes()),
  //   esTokenTopo_(esConsumes()),
  : tokenRecTracks_(consumes<reco::TrackCollection>(cfg.getParameter<edm::InputTag>("rectracks"))),
    tokenSimTracks_(consumes<edm::SimTrackContainer>(cfg.getParameter<edm::InputTag>("simtracks"))),
    tokenSimVertices_(consumes<edm::SimVertexContainer>(cfg.getParameter<edm::InputTag>("simvertices")))
{
  // //
  // // create TTree
  // //
  // edm::Service<TFileService> fs;
  // trackTree_ = fs->make<TTree>( "TrackTree", "TrackTree" );
  // trackInfo_.setBranches(*trackTree_);
}

void TrackTree::analyze(const edm::Event& event, const edm::EventSetup& eventSetup) {
    initEventStructure();
    //
    // access to and selection of reconstructed tracks
    //
    edm::Handle<reco::TrackCollection> recTrackHandle;
    event.getByToken(tokenRecTracks_,recTrackHandle);
    reco::TrackCollection recTracks;
    for ( auto rt=recTrackHandle.product()->begin(); rt!=recTrackHandle.product()->end(); ++rt ) {
      // cuts need to be added to cfg !!!
      if ( rt->pt()>0.3 ) {
	recTracks.push_back(*rt);
      }
    }
    //
    // access to and selection of simulated tracks
    //
    edm::Handle<edm::SimTrackContainer> simTrackHandle;
    event.getByToken(tokenSimTracks_,simTrackHandle);
    edm::SimTrackContainer simTracks;
    for ( auto st=simTrackHandle.product()->begin(); st!=simTrackHandle.product()->end(); ++st ) {
      // cuts need to be added to cfg !!!
      if ( st->momentum().pt()>0.3 && abs(st->type())==13 ) {
	simTracks.push_back(*st);
      }
    }
    //
    // access to simulated vertices
    //      
    edm::Handle<edm::SimVertexContainer> simVertexHandle;
    event.getByToken(tokenSimVertices_,simVertexHandle);
    const edm::SimVertexContainer& simVertices(*simVertexHandle.product());

    std::cout << "#selected RecTracks = " << recTracks.size() << std::endl;
    std::cout << "#selected SimTracks = " << simTracks.size() << std::endl;
    std::cout << "#SimVertices = " << simVertices.size() << std::endl;
    std::cout << std::endl;
    //
    if ( recTracks.size()==0 || simTracks.size()==0 )  return;
    //
    // match SimTracks to RecTracks by deltaR
    //
    for ( auto rt=recTracks.begin(); rt!=recTracks.end(); ++rt ) {
      //
      // find SimTrack with smallest deltaR
      //
      double dr2Min(999999.);
      const SimTrack* stMin(nullptr);
      for ( auto st=simTracks.begin(); st!=simTracks.end(); ++st ) {
	double dr2 = deltaR2<math::XYZVector,math::XYZTLorentzVectorD>(rt->momentum(),st->momentum());
	if ( dr2<dr2Min ) {
	  dr2Min = dr2;
	  stMin = &(*st);
	}
      }
      if ( stMin==nullptr ) {
	std::cout << "*** Did not find matching SimTrack!!!" << std::endl;
	continue;
      }
      std::cout << "*** Found SimTrack with deltaR**2 = " << dr2Min << std::endl;
      //
      // get SimVertex corresponding to SimTrack
      //
      int iv(stMin->vertIndex());
      const SimVertex* simVertex(nullptr);
      if ( iv>=0 ) {
	if ( iv>=(int)simVertices.size() ) {
	  std::cout << "*** mismatch between SimVertex index (" << iv << ") and #SimVertices ("
		    << simVertices.size() << ")" << std::endl;
	}
	else {
	  simVertex = &simVertices[iv];
	}
      }
      else {
	std::cout << "*** no SimVertex associated to SimTrack" << std::endl;
      }
      //
      // Fill info for this track
      //
      trackInfo_.fillTrackInfo(&(*rt),stMin,simVertex);
    }
    
    //
    // Fill tree
    //
    std::cout << "Filling trackTree with " << trackInfo_.trackData.Track_chi2.size() << " entries" << std::endl;
    trackTree_->Fill();
    //
    // loop over reconstruct
   // const TrackerGeometry* tkGeom = &eventSetup.getData(esTokenGeom_);
  // const TrackerTopology* tTopo = &eventSetup.getData(esTokenTopo_);

  // edm::Handle<Phase2TrackerRecHit1DCollectionNew> rechits;
  // event.getByToken(tokenRecHits_, rechits);
  
  // edm::Handle<Phase2TrackerCluster1DCollectionNew> clusters;
  // event.getByToken(tokenClusters_, clusters);
  // if ( clusters->size() != rechits->size() ) {
  //   std::cout << "*** Different sizes for clusters (" << clusters->size()
  // 	      << ") and rechits (" << rechits->size() << ")" << std::endl;
  // }

  // edm::Handle<edm::DetSetVector<PixelDigiSimLink> > pixelSimLinks;
  // event.getByToken(tokenLinks_, pixelSimLinks);
  // edm::Handle<edm::PSimHitContainer> simHitHandle;
  // std::vector<const edm::PSimHitContainer*> shInfoSimHitsRaw;
  // for ( auto tokenIt=shInfoSimHitTokens_.begin(); tokenIt!=shInfoSimHitTokens_.end(); ++tokenIt ) {
  //   event.getByToken(*tokenIt, simHitHandle);
  //   shInfoSimHitsRaw.push_back(simHitHandle.product());
  // }
  // std::vector<const edm::PSimHitContainer*> rhInfoSimHitsRaw;
  // for ( auto tokenIt=rhInfoSimHitTokens_.begin(); tokenIt!=rhInfoSimHitTokens_.end(); ++tokenIt ) {
  //   event.getByToken(*tokenIt, simHitHandle);
  //   rhInfoSimHitsRaw.push_back(simHitHandle.product());
  // }
  

  // edm::Handle<edm::SimTrackContainer> simTracksRaw;
  // event.getByToken(tokenSimTracks_, simTracksRaw);
  // std::map<unsigned int, SimTrack> simTracks;
  // for (edm::SimTrackContainer::const_iterator simTrackIt(simTracksRaw->begin()); simTrackIt != simTracksRaw->end();
  //      ++simTrackIt) {
  //   if (simTrackIt->momentum().pt() > simtrackminpt_) {
  //     simTracks.insert(std::pair<unsigned int, SimTrack>(simTrackIt->trackId(), *simTrackIt));
  //   }
  //   simTrackInfo_.fillSimTrackInfo(*simTrackIt);
  // }
  // simTrackTree->Fill();
  // simHitInfo_.setupEvent(tTopo,tkGeom,pixelSimLinks.product(),shInfoSimHitsRaw,*rechits.product(),&simTracks);
  // for (auto detHitsIt=simHitInfo_.simHitsPerDet().begin(); detHitsIt!=simHitInfo_.simHitsPerDet().end(); ++detHitsIt ) {
  //   DetId detId(detHitsIt->first);
  //   unsigned int layer = (tTopo->side(detId) != 0) * 1000;  // don't split up endcap sides
  //   layer += tTopo->layer(detId);    
  //   TrackerGeometry::ModuleType mType = tkGeom->getDetectorType(detId);
  //   if ( mType!=TrackerGeometry::ModuleType::Ph2PSP && 
  // 	 mType!=TrackerGeometry::ModuleType::Ph2PSS &&
  // 	 mType!=TrackerGeometry::ModuleType::Ph2SS )  continue;

  //   const GeomDetUnit* geomDetUnit(tkGeom->idToDetUnit(detId));
  //   if (!geomDetUnit) {
  //     std::cout << "*** did not find geomDetUnit ***" << std::endl;
  //     continue;
  //   }
  //   for (auto simhitIt=detHitsIt->second.begin(); simhitIt!=detHitsIt->second.end(); ++simhitIt) {
  //     simHitInfo_.fillSimHitInfo(**simhitIt);
  //   }
  // }


      
  // simHitTree->Fill();
  // recHitInfo_.setupEvent(tTopo,tkGeom,pixelSimLinks.product(),rhInfoSimHitsRaw,*rechits.product(),&simTracks);
  // for (Phase2TrackerRecHit1DCollectionNew::const_iterator DSViter = rechits->begin();
  //      DSViter != rechits->end(); ++DSViter) {

  //   unsigned int rawid(DSViter->detId());
  //   DetId detId(rawid);
  //   unsigned int layer = (tTopo->side(detId) != 0) * 1000;  // don't split up endcap sides
  //   layer += tTopo->layer(detId);
  //   TrackerGeometry::ModuleType mType = tkGeom->getDetectorType(detId);
  //   if ( mType!=TrackerGeometry::ModuleType::Ph2PSP && 
  //  	 mType!=TrackerGeometry::ModuleType::Ph2PSS &&
  //  	 mType!=TrackerGeometry::ModuleType::Ph2SS )  continue;    

  //   const GeomDetUnit* geomDetUnit(tkGeom->idToDetUnit(detId));
  //   if (!geomDetUnit)
  //     continue;


  //   for (edmNew::DetSet<Phase2TrackerRecHit1D>::const_iterator rechitIt = DSViter->begin();
  //    	 rechitIt != DSViter->end(); ++rechitIt) {
  //     recHitInfo_.fillRecHitInfo(*rechitIt,rawid,geomDetUnit, // &pixelSimLinks,simTracks,
  // 				 rhInfoSimHitsRaw,debugHitMatch_);
  //   }
  // }
  // recHitTree->Fill();

}
 
void TrackTree::beginJob()
{
  edm::Service<TFileService> fs;
  trackTree_ = fs->make<TTree>( "TrackTree", "TrackTree" );
  trackInfo_.setBranches(*trackTree_);
}

void TrackTree::endJob()
{}

void TrackTree::initEventStructure()
{
  trackInfo_.clear();
}

DEFINE_FWK_MODULE(TrackTree);
