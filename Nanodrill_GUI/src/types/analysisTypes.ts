// src/types/analysisTypes.ts
export interface ImageStats {
  min: number;
  max: number;
  mean: number;
  median: number;
  std: number;
  rms: number;
}

export interface Dimensions {
  width: number;
  height: number;
  xRange: number;
  yRange: number;
}

// Point type for line profile
export interface Point {
  x: number;
  y: number;
}

// ProfilePoint type for line profile data
export interface ProfilePoint {
  distance: number;
  value: number;
  x: number;
  y: number;
}
