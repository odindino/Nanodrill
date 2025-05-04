#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
測試 int_analysis.py 模組的腳本

此腳本直接使用 int_analysis.py 中的方法來處理和顯示 .int 檔案。
使用方式：
    python int_analysis_test.py [檔案路徑.int] [flatten_method]

預設使用檔案：
    ./testfiles/20250425_Janus Stacking SiO2_13K_457TopoFwd.int

flatten_method 可選值:
    - none: 不進行平面化處理 (預設)
    - mean: 使用線性平面化
    - polyfit: 使用多項式平面化
    - plane: 使用全局平面擬合

範例：
    python int_analysis_test.py
    python int_analysis_test.py mean
    python int_analysis_test.py ./custom/path/file.int plane
"""

import os
import sys
import numpy as np
import re
import logging
import plotly.io as pio

# 添加父目錄到系統路徑以便引入模組
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 設置預設輸出為瀏覽器
pio.renderers.default = "browser"

# 引入項目模組
from core.parsers.int_parser import IntParser
from core.analysis.int_analysis import IntAnalysis

# 預設測試檔案路徑
DEFAULT_TEST_FILE = "./testfiles/20250425_Janus Stacking SiO2_13K_457TopoFwd.int"

def find_parameters_from_txt(int_file_path):
    """從對應的 txt 檔案中尋找參數"""
    # 預設參數
    params = {
        'scale': 1.0,
        'x_pixels': 512,
        'y_pixels': 512,
        'x_range': 100.0,
        'y_range': 100.0,
        'phys_unit': 'nm'
    }
    
    try:
        # 嘗試找出對應的 txt 檔案
        txt_file_path = None
        int_dir = os.path.dirname(int_file_path)
        int_basename = os.path.basename(int_file_path)
        
        # 嘗試從 int 文件名找出 txt 文件名的模式
        match = re.search(r'(.+?)_(\d+)([^_]*?)\.(int|dat)$', int_basename, re.IGNORECASE)
        if match:
            prefix = match.group(1)
            number = match.group(2)
            
            # 在同一目錄中尋找可能的 txt 檔案
            for filename in os.listdir(int_dir or '.'):
                if filename.endswith('.txt') and filename.startswith(f"{prefix}_{number}"):
                    txt_file_path = os.path.join(int_dir or '.', filename)
                    break
        
        # 如果找到了 txt 檔案，解析它
        if txt_file_path and os.path.exists(txt_file_path):
            logger.info(f"找到對應的 TXT 檔案: {txt_file_path}")
            
            with open(txt_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 解析基本參數
            # 像素數
            x_pixel_match = re.search(r'xPixel\s*:\s*([^\n]+)', content)
            if x_pixel_match:
                try:
                    params['x_pixels'] = int(x_pixel_match.group(1).strip())
                except ValueError:
                    pass
            
            y_pixel_match = re.search(r'yPixel\s*:\s*([^\n]+)', content)
            if y_pixel_match:
                try:
                    params['y_pixels'] = int(y_pixel_match.group(1).strip())
                except ValueError:
                    pass
            
            # 掃描範圍
            x_range_match = re.search(r'XScanRange\s*:\s*([^\n]+)', content)
            if x_range_match:
                try:
                    params['x_range'] = float(x_range_match.group(1).strip())
                except ValueError:
                    pass
            
            y_range_match = re.search(r'YScanRange\s*:\s*([^\n]+)', content)
            if y_range_match:
                try:
                    params['y_range'] = float(y_range_match.group(1).strip())
                except ValueError:
                    pass
            
            # 物理單位
            x_unit_match = re.search(r'XPhysUnit\s*:\s*([^\n]+)', content)
            if x_unit_match:
                params['phys_unit'] = x_unit_match.group(1).strip()
            
            # 解析檔案描述區段以尋找 scale
            file_desc_pattern = r'FileDescBegin(.*?)FileDescEnd'
            file_descs = re.findall(file_desc_pattern, content, re.DOTALL)
            
            for desc_content in file_descs:
                filename_match = re.search(r'FileName\s*:\s*([^\n]+)', desc_content)
                if filename_match and filename_match.group(1).strip() == int_basename:
                    scale_match = re.search(r'Scale\s*:\s*([^\n]+)', desc_content)
                    if scale_match:
                        try:
                            params['scale'] = float(scale_match.group(1).strip())
                        except ValueError:
                            pass
                    
                    unit_match = re.search(r'PhysUnit\s*:\s*([^\n]+)', desc_content)
                    if unit_match:
                        params['phys_unit'] = unit_match.group(1).strip()
            
            logger.info(f"從 TXT 檔案獲取到的參數: {params}")
        else:
            logger.warning(f"未找到對應的 TXT 檔案，使用預設參數")
    
    except Exception as e:
        logger.error(f"獲取參數時出錯: {str(e)}")
    
    return params

def main():
    # 處理命令行參數
    if len(sys.argv) == 1:
        # 沒有提供參數，使用預設值
        int_file_path = DEFAULT_TEST_FILE
        flatten_method = 'none'
    elif len(sys.argv) == 2:
        # 提供了一個參數，判斷是檔案路徑還是平面化方法
        if sys.argv[1] in ['none', 'mean', 'polyfit', 'plane']:
            int_file_path = DEFAULT_TEST_FILE
            flatten_method = sys.argv[1]
        else:
            int_file_path = sys.argv[1]
            flatten_method = 'none'
    else:
        # 提供了兩個或更多參數
        int_file_path = sys.argv[1]
        flatten_method = sys.argv[2]
    
    # 驗證平面化方法
    if flatten_method not in ['none', 'mean', 'polyfit', 'plane']:
        print(f"錯誤: 未知的平面化方法 '{flatten_method}'")
        print("可用選項: none, mean, polyfit, plane")
        sys.exit(1)
    
    # 檢查檔案是否存在
    if not os.path.exists(int_file_path):
        print(f"錯誤: 檔案不存在 - {int_file_path}")
        print(f"請確認檔案路徑是否正確，或者手動指定有效的 .int 檔案路徑")
        sys.exit(1)
    
    print(f"使用檔案: {int_file_path}")
    print(f"平面化方法: {flatten_method}")
    
    # 檢查是否能夠引入 int_analysis 模組
    try:
        print(f"正在使用 IntAnalysis 模組")
        print("-" * 50)
    except NameError:
        print("錯誤: 無法引入 IntAnalysis 模組")
        sys.exit(1)
    
    # 獲取參數
    params = find_parameters_from_txt(int_file_path)
    print(f"使用參數: scale={params['scale']}, "
          f"x_pixels={params['x_pixels']}, y_pixels={params['y_pixels']}, "
          f"x_range={params['x_range']}, y_range={params['y_range']}, "
          f"physUnit={params['phys_unit']}")
    print("-" * 50)
    
    try:
        # 使用 IntParser 解析 INT 檔案
        print(f"解析檔案: {int_file_path}")
        parser = IntParser(int_file_path, params['scale'], params['x_pixels'], params['y_pixels'])
        image_data = parser.parse()
        
        print(f"原始數據形狀: {image_data.shape}")
        print(f"數值範圍: {np.min(image_data):.2f} 到 {np.max(image_data):.2f} {params['phys_unit']}")
        print("-" * 50)
        
        # 應用平面化處理 (如果需要)
        if flatten_method != 'none':
            print(f"應用平面化處理: {flatten_method}")
            
            if flatten_method == 'mean':
                image_data = IntAnalysis.linewise_flatten_mean(image_data)
            elif flatten_method == 'polyfit':
                image_data = IntAnalysis.linewise_flatten_polyfit(image_data, deg=2)
            elif flatten_method == 'plane':
                image_data = IntAnalysis.plane_flatten(image_data)
            
            print(f"平面化後數值範圍: {np.min(image_data):.2f} 到 {np.max(image_data):.2f} {params['phys_unit']}")
            print("-" * 50)
        
        # 獲取統計數據
        stats = IntAnalysis.get_topo_stats(image_data)
        print(f"統計數據:")
        print(f"  最小值: {stats['min']:.2f} {params['phys_unit']}")
        print(f"  最大值: {stats['max']:.2f} {params['phys_unit']}")
        print(f"  平均值: {stats['mean']:.2f} {params['phys_unit']}")
        print(f"  RMS: {stats['rms']:.2f} {params['phys_unit']}")
        print("-" * 50)
        
        # 檔案基本名稱
        base_name = os.path.splitext(os.path.basename(int_file_path))[0]
        
        # 直接使用 IntAnalysis 生成圖像
        print("生成 Plotly 圖像...")
        
        # 使用 generate_topo_plot 方法
        dimensions = (params['x_range'], params['y_range']) if params['x_range'] and params['y_range'] else None
        fig = IntAnalysis.generate_topo_plot(
            image_data,
            dimensions=dimensions,
            title=f"{base_name} ({flatten_method if flatten_method != 'none' else 'original'})",
            colormap="Viridis",
            phys_unit=params['phys_unit']
        )
        
        # 添加統計信息註解
        stat_text = (f"Min: {stats['min']:.2f}, Max: {stats['max']:.2f}, "
                    f"Mean: {stats['mean']:.2f}, RMS: {stats['rms']:.2f} {params['phys_unit']}")
        
        fig.add_annotation(
            x=0.5,
            y=1.05,
            xref="paper",
            yref="paper",
            text=stat_text,
            showarrow=False,
            font=dict(size=12),
            align="center",
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="gray",
            borderwidth=1,
            borderpad=4
        )
        
        print("顯示圖像...")
        fig.show()
        
        # 進一步測試 - 生成靜態圖像的base64字符串
        print("-" * 50)
        print("測試生成靜態圖像...")
        base64_img = IntAnalysis.generate_topo_image(
            image_data,
            dimensions=dimensions,
            title=base_name,
            colormap="Viridis",
            phys_unit=params['phys_unit']
        )
        
        print(f"靜態圖像生成成功，Base64 長度: {len(base64_img)}")
        print("-" * 50)
        
        # 生成線性剖面
        print("測試線性剖面功能...")
        
        # 在圖像中心創建一條水平剖面線
        center_y = image_data.shape[0] // 2
        start_point = [center_y, 0]
        end_point = [center_y, image_data.shape[1] - 1]
        
        profile_data = IntAnalysis.get_line_profile(
            image_data,
            start_point,
            end_point,
            physical_scale=params['x_range'] / image_data.shape[1] if params['x_range'] else 1.0
        )
        
        print(f"剖面長度: {profile_data['length']:.2f} {params['phys_unit']}")
        print(f"剖面點數: {len(profile_data['distance'])}")
        
        # 使用 IntAnalysis 生成剖面圖像
        profile_img_data = IntAnalysis.generate_profile_image(
            profile_data,
            title=f"{base_name} - Horizontal Profile"
        )
        
        print(f"剖面圖像生成成功，Base64 長度: {len(profile_img_data)}")
        print("-" * 50)
        
        print("所有測試通過！IntAnalysis.py 模組正確運作。")
        
    except Exception as e:
        print(f"錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()