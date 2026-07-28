#include <iostream>
#include <cmath>
#include <ROOT/RVec.hxx>
using RVecF = ROOT::VecOps::RVec<float>;

float floatMod(float a, float b) {
  //
  // change fmod behaviour for negative numbers
  //   (fmod will return -fmod(|a|,b) for a<0)
  //   
  float result = std::fmod(a,b);
  if ( result < 0. )  result += b;
  return result;
}


RVecF floatMod(const RVecF& a, float b) {
  //
  // apply floatMod to RVec of floats
  //
  RVecF result = RVecF(a.size());
  for ( unsigned int i=0; i<a.size(); ++i ) {
    result[i] = floatMod(a[i],b);
  }
  return result;
}
