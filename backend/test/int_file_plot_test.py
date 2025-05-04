#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SPM .int 檔案測試工具

此程式用於測試 .int 檔案的讀取和可視化。
命令行用法：
    python int_file_plot_test.py 路徑/到/檔案.int [scale] [x_pixels] [y_pixels]

範例：
    python int_file_plot_test.py data/sample.int 1.0 512 512
"""

import os
import sys
import argparse
import numpy as np
import logging
import re
import plotly.io as pio

# 設置顯示模式為瀏覽器
pio.renderers.default = "browser"

# 添加父目錄到系統路徑以便引入模組
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 引入項目模組
from core.parsers.int_parser import IntParser
from core.analysis.int_analysis import IntAnalysis

def find_parameters_from_txt(int_file_path):
    """
    從對應的 txt 檔案中尋找參數
    
    Args:
        int_file_path: .int 檔案路徑
    
    Returns:
        dict: 包含找到的參數的字典
    """
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
            for filename in os.listdir(int_dir):
                if filename.endswith('.txt') and filename.startswith(f"{prefix}_{number}"):
                    txt_file_path = os.path.join(int_dir, filename)
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
    # 解析命令行參數
    parser = argparse.ArgumentParser(description='SPM .int 檔案測試工具')
    parser.add_argument('int_file', help='.int 檔案路徑')
    parser.add_argument('--scale', type=float, help='數值縮放因子 (通常在 txt 檔案中的 Scale 參數)')
    parser.add_argument('--x_pixels', type=int, help='X方向像素數 (通常在 txt 檔案中的 xPixel 參數)')
    parser.add_argument('--y_pixels', type=int, help='Y方向像素數 (通常在 txt 檔案中的 yPixel 參數)')
    parser.add_argument('--x_range', type=float, help='X方向掃描範圍')
    parser.add_argument('--y_range', type=float, help='Y方向掃描範圍')
    parser.add_argument('--colormap', default='Viridis', help='顏色映射名稱 (如: Viridis, Plasma, Inferno, Magma, Jet)')
    parser.add_argument('--flatten', choices=['none', 'mean', 'polyfit', 'plane'], default='none', help='平面化方法')
    parser.add_argument('--polyfit_degree', type=int, default=2, help='使用多項式平面化時的階數')
    parser.add_argument('--save', action='store_true', help='儲存輸出圖像')
    parser.add_argument('--output', help='輸出檔案路徑 (預設: int檔案名稱_plot.png)')
    
    args = parser.parse_args()
    
    # 檢查 .int 檔案是否存在
    if not os.path.exists(args.int_file):
        logger.error(f"檔案不存在: {args.int_file}")
        sys.exit(1)
    
    # 從 txt 檔案中獲取參數
    params = find_parameters_from_txt(args.int_file)
    
    # 命令行參數覆蓋自動檢測的參數
    if args.scale is not None:
        params['scale'] = args.scale
    if args.x_pixels is not None:
        params['x_pixels'] = args.x_pixels
    if args.y_pixels is not None:
        params['y_pixels'] = args.y_pixels
    if args.x_range is not None:
        params['x_range'] = args.x_range
    if args.y_range is not None:
        params['y_range'] = args.y_range
    
    logger.info(f"使用參數: scale={params['scale']}, x_pixels={params['x_pixels']}, y_pixels={params['y_pixels']}")
    
    try:
        # 使用 IntParser 解析 .int 檔案
        parser = IntParser(args.int_file, params['scale'], params['x_pixels'], params['y_pixels'])
        image_data = parser.parse()
        
        logger.info(f"成功解析 .int 檔案，數據形狀: {image_data.shape}")
        
        # 應用平面化處理 (如果需要)
        if args.flatten != 'none':
            logger.info(f"應用平面化處理: {args.flatten}")
            
            if args.flatten == 'mean':
                image_data = IntAnalysis.linewise_flatten_mean(image_data)
            elif args.flatten == 'polyfit':
                image_data = IntAnalysis.linewise_flatten_polyfit(image_data, args.polyfit_degree)
            elif args.flatten == 'plane':
                image_data = IntAnalysis.plane_flatten(image_data)
        
        # 獲取基本統計資訊
        stats = IntAnalysis.get_topo_stats(image_data)
        logger.info(f"數據統計: 最小值={stats['min']:.2f}, 最大值={stats['max']:.2f}, 平均值={stats['mean']:.2f}")
        
        # 檔案基本名稱 (不含路徑和副檔名)
        base_name = os.path.splitext(os.path.basename(args.int_file))[0]
        
        # 使用 Plotly 繪製圖像
        dimensions = (params['x_range'], params['y_range'])
        fig = IntAnalysis.generate_topo_plot(image_data, dimensions, base_name, args.colormap, params['phys_unit'])
        
        # 添加統計資訊到圖像
        stat_text = (f"Min: {stats['min']:.2f} {params['phys_unit']}, "
                    f"Max: {stats['max']:.2f} {params['phys_unit']}, "
                    f"Mean: {stats['mean']:.2f} {params['phys_unit']}, "
                    f"RMS: {stats['rms']:.2f} {params['phys_unit']}")
        
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
        
        # 如果需要保存圖像
        if args.save:
            output_path = args.output if args.output else f"{base_name}_plot.png"
            fig.write_image(output_path, width=800, height=700, scale=2)
            logger.info(f"已儲存圖像到: {output_path}")
        
        # 顯示圖像
        fig.show()
        
    except Exception as e:
        logger.error(f"處理 .int 檔案時出錯: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()