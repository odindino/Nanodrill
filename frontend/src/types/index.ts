// SPM 檔案介面
export interface SPMFile {
    name: string;
    path: string;
    number: number;
    type: string;
    modTime: number;
    modTimeStr: string;
  }
  
  // 檔案描述介面
  export interface FileDescription {
    FileName: string;
    Caption: string;
    Scale: string;
    PhysUnit: string;
    Offset?: string;
  }
  
  // 元數據信息介面
  export interface MetadataInfo {
    Version?: string;
    Date?: string;
    Time?: string;
    UserName?: string;
    
    SetPoint?: string;
    SetPointPhysUnit?: string;
    FeedBackModus?: string;
    Bias?: string;
    BiasPhysUnit?: string;
    Ki?: string;
    Kp?: string;
    FeedbackOnCh?: string;
    
    XScanRange?: string;
    YScanRange?: string;
    XPhysUnit?: string;
    YPhysUnit?: string;
    Speed?: string;
    LineRate?: string;
    Angle?: string;
    xPixel?: string;
    yPixel?: string;
    yCenter?: string;
    xCenter?: string;
    
    LockInFreq?: string;
    LockInFreqPhysUnit?: string;
    LockInAmpl?: string;
    LockInAmplPhysUnit?: string;
    
    // 檔案描述陣列
    fileDescriptions?: FileDescription[];
    
    // 允許動態屬性
    [key: string]: any;
  }
  
  // 圖像數據響應介面
  export interface ImageDataResponse {
    success: boolean;
    imageData?: string;
    dimensions?: {
      width: number;
      height: number;
      xRange: number;
      yRange: number;
      xUnit: string;
      yUnit: string;
    };
    rawData?: number[][];
    error?: string;
  }
  
  // API 響應介面
  export interface ApiResponse {
    success: boolean;
    message?: string;
    error?: string;
    [key: string]: any;
  }