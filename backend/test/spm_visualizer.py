#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SPM 檔案視覺化測試工具

此程式使用 int_parser 和 txt_parser 函式庫來解析 SPM 檔案並繪製形貌圖像。
預設讀取 './testfiles/20250425_Janus Stacking SiO2_13K_457TopoFwd.int' 
和 './testfiles/20250425_Janus Stacking SiO2_13K_457.txt' 檔案。

使用方式:
    python spm_visualizer.py [--txt TXT_PATH] [--int INT_PATH] [--colormap COLORMAP]

範例:
    python spm_visualizer.py
    python spm_visualizer.py --colormap Plasma
    python spm_visualizer.py --txt path/to/file.txt --int path/to/file.int
"""

import os
import sys
import argparse
import logging
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio

# 將父目錄添加到系統路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 匯入解析器模組
from core.parsers.int_parser import IntParser
from core.parsers.txt_parser import TxtParser

# 設置 Plotly 渲染模式為瀏覽器
pio.renderers.default = "browser"

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ensure_test_directory_exists():
    """確保測試檔案目錄存在"""
    test_dir = './testfiles'
    if not os.path.exists(test_dir):
        logger.info(f"創建測試檔案目錄: {test_dir}")
        os.makedirs(test_dir)
        logger.warning(f"注意: 測試檔案目錄已創建，但尚未包含預設檔案")
        return False
    return True

def parse_txt_file(txt_path):
    """解析 TXT 檔案獲取參數"""
    if not os.path.exists(txt_path):
        logger.error(f"TXT 檔案不存在: {txt_path}")
        return None
    
    try:
        # 使用 TxtParser 解析檔案
        txt_parser = TxtParser(txt_path)
        metadata = txt_parser.parse()
        logger.info(f"成功解析 TXT 檔案: {txt_path}")
        return metadata
    except Exception as e:
        logger.error(f"解析 TXT 檔案時出錯: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def find_int_file_parameters(metadata, int_filename):
    """從 TXT 元數據中查找 INT 檔案的參數"""
    params = {
        'scale': 1.0,
        'x_pixels': 512,  # 預設值
        'y_pixels': 512,  # 預設值
        'phys_unit': 'nm',
        'x_range': 100.0,
        'y_range': 100.0,
    }
    
    # 從元數據中獲取像素數
    if 'xPixel' in metadata:
        try:
            params['x_pixels'] = int(metadata['xPixel'])
            logger.info(f"從元數據獲取 X 像素數: {params['x_pixels']}")
        except (ValueError, TypeError):
            logger.warning(f"無法轉換 X 像素數: {metadata['xPixel']}")
    
    if 'yPixel' in metadata:
        try:
            params['y_pixels'] = int(metadata['yPixel'])
            logger.info(f"從元數據獲取 Y 像素數: {params['y_pixels']}")
        except (ValueError, TypeError):
            logger.warning(f"無法轉換 Y 像素數: {metadata['yPixel']}")
    
    # 獲取掃描範圍
    if 'XScanRange' in metadata:
        try:
            params['x_range'] = float(metadata['XScanRange'])
            logger.info(f"從元數據獲取 X 掃描範圍: {params['x_range']}")
        except (ValueError, TypeError):
            logger.warning(f"無法轉換 X 掃描範圍: {metadata['XScanRange']}")
    
    if 'YScanRange' in metadata:
        try:
            params['y_range'] = float(metadata['YScanRange'])
            logger.info(f"從元數據獲取 Y 掃描範圍: {params['y_range']}")
        except (ValueError, TypeError):
            logger.warning(f"無法轉換 Y 掃描範圍: {metadata['YScanRange']}")
    
    # 從文件描述中查找 INT 檔案的參數
    file_descriptions = metadata.get('fileDescriptions', [])
    for desc in file_descriptions:
        if desc.get('FileName') == int_filename:
            logger.info(f"找到匹配的檔案描述: {int_filename}")
            
            # 獲取比例因子
            if 'Scale' in desc:
                try:
                    params['scale'] = float(desc['Scale'])
                    logger.info(f"從檔案描述獲取比例因子: {params['scale']}")
                except (ValueError, TypeError):
                    logger.warning(f"無法轉換比例因子: {desc['Scale']}")
            
            # 獲取物理單位
            if 'PhysUnit' in desc:
                params['phys_unit'] = desc['PhysUnit']
                logger.info(f"從檔案描述獲取物理單位: {params['phys_unit']}")
            
            break
    
    # 獲取偏壓和設定點信息
    params['bias'] = metadata.get('Bias', None)
    params['bias_unit'] = metadata.get('BiasPhysUnit', None)
    params['set_point'] = metadata.get('SetPoint', None)
    params['set_point_unit'] = metadata.get('SetPointPhysUnit', None)
    params['date'] = metadata.get('Date', None)
    params['time'] = metadata.get('Time', None)
    params['user_name'] = metadata.get('UserName', None)
    params['angle'] = metadata.get('Angle', None)
    
    return params

def parse_int_file(int_path, x_pixels, y_pixels, scale):
    """解析 INT 檔案獲取圖像數據"""
    if not os.path.exists(int_path):
        logger.error(f"INT 檔案不存在: {int_path}")
        return None
    
    try:
        # 使用 IntParser 解析檔案
        int_parser = IntParser(int_path, scale, x_pixels, y_pixels)
        image_data = int_parser.parse()
        logger.info(f"成功解析 INT 檔案: {int_path}, 形狀: {image_data.shape}")
        return image_data
    except Exception as e:
        logger.error(f"解析 INT 檔案時出錯: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def get_topo_stats(image_data):
    """計算形貌數據的統計信息"""
    # 移除NaN值進行計算
    valid_data = image_data[~np.isnan(image_data)]
    
    stats = {
        "min": float(np.min(valid_data)),
        "max": float(np.max(valid_data)),
        "mean": float(np.mean(valid_data)),
        "median": float(np.median(valid_data)),
        "std": float(np.std(valid_data)),
        "rms": float(np.sqrt(np.mean(np.square(valid_data - np.mean(valid_data)))))
    }
    
    return stats

def apply_flatten(image_data, method='mean', degree=2):
    """應用平面化處理"""
    result = image_data.copy()
    
    if method == 'mean':
        # 按行減去均值
        for i in range(len(result)):
            result[i] -= np.mean(result[i])
        logger.info("應用線性平面化處理")
        
    elif method == 'polyfit':
        # 按行使用多項式擬合
        y_size, x_size = result.shape
        x = np.arange(x_size)
        
        for i in range(y_size):
            fit = np.polyfit(x, result[i], degree)
            poly = np.poly1d(fit)
            result[i] -= poly(x)
        logger.info(f"應用多項式平面化處理 (階數: {degree})")
        
    elif method == 'plane':
        # 全局平面擬合
        y_size, x_size = result.shape
        
        # 創建坐標網格
        x, y = np.meshgrid(np.arange(x_size), np.arange(y_size))
        x = x.flatten()
        y = y.flatten()
        z = result.flatten()
        
        # 擬合平面 z = ax + by + c
        A = np.column_stack((x, y, np.ones_like(x)))
        coeffs, _, _, _ = np.linalg.lstsq(A, z, rcond=None)
        
        # 根據擬合結果創建平面
        plane = coeffs[0] * x.reshape(y_size, x_size) + coeffs[1] * y.reshape(y_size, x_size) + coeffs[2]
        
        # 從原始數據中減去平面
        result -= plane
        logger.info("應用全局平面擬合處理")
        
    return result

def generate_topo_plot(image_data, params, title=None, colormap="Viridis", flatten_method=None):
    """生成並顯示形貌圖"""
    # 如果提供了平面化方法
    if flatten_method and flatten_method != 'none':
        image_data = apply_flatten(image_data, flatten_method)
    
    # 如果沒有提供標題，使用 INT 檔案名
    if title is None:
        title = os.path.basename(params.get('int_path', 'Topography'))
    
    # 獲取尺寸
    y_size, x_size = image_data.shape
    
    # 創建X和Y坐標網格，使用掃描範圍
    x = np.linspace(0, params['x_range'], x_size)
    y = np.linspace(0, params['y_range'], y_size)
    
    # 創建 Plotly 圖形
    fig = go.Figure(data=go.Heatmap(
        z=image_data,
        x=x,
        y=y,
        colorscale=colormap,
        colorbar=dict(
            title=f'Height ({params["phys_unit"]})',
            titleside='right',
            titlefont=dict(size=14)
        )
    ))
    
    # 獲取統計數據
    stats = get_topo_stats(image_data)
    
    # 設置佈局
    fig.update_layout(
        title=title,
        xaxis_title=f'X ({params["phys_unit"]})',
        yaxis_title=f'Y ({params["phys_unit"]})',
        xaxis=dict(
            scaleanchor="y",
            constrain='domain'
        ),
        autosize=True,
        width=800,
        height=700,
        margin=dict(l=65, r=50, t=90, b=65)
    )
    
    # 添加統計信息
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
    
    # 添加額外掃描參數信息
    scan_info = []
    if params.get('date'):
        scan_info.append(f"Date: {params['date']} {params.get('time', '')}")
    if params.get('bias') and params.get('bias_unit'):
        scan_info.append(f"Bias: {params['bias']} {params['bias_unit']}")
    if params.get('set_point') and params.get('set_point_unit'):
        scan_info.append(f"SetPoint: {params['set_point']} {params['set_point_unit']}")
    if params.get('angle') is not None:
        scan_info.append(f"Angle: {params['angle']}°")
    
    if scan_info:
        scan_text = "<br>".join(scan_info)
        fig.add_annotation(
            x=0.01,
            y=0.99,
            xref="paper",
            yref="paper",
            text=scan_text,
            showarrow=False,
            font=dict(size=11),
            align="left",
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="gray",
            borderwidth=1,
            borderpad=4,
            xanchor="left",
            yanchor="top"
        )
    
    return fig

def save_plot(fig, output_path=None, int_path=None):
    """儲存圖像"""
    if output_path is None and int_path:
        base_name = os.path.splitext(os.path.basename(int_path))[0]
        output_path = f"{base_name}_plot.png"
    elif output_path is None:
        output_path = "topo_plot.png"
    
    fig.write_image(output_path, width=800, height=700, scale=2)
    logger.info(f"已儲存圖像到: {output_path}")
    return output_path

def main():
    # 預設檔案路徑
    DEFAULT_INT_FILE = './testfiles/20250425_Janus Stacking SiO2_13K_457TopoFwd.int'
    DEFAULT_TXT_FILE = './testfiles/20250425_Janus Stacking SiO2_13K_457.txt'
    
    # 確保測試目錄存在
    ensure_test_directory_exists()
    
    # 解析命令行參數
    parser = argparse.ArgumentParser(description='SPM 檔案視覺化測試工具')
    parser.add_argument('--txt', help='.txt 檔案路徑', default=DEFAULT_TXT_FILE)
    parser.add_argument('--int', help='.int 檔案路徑', default=DEFAULT_INT_FILE)
    parser.add_argument('--colormap', default='Oranges', help='顏色映射名稱 (例如: Viridis, Plasma, Oranges)')
    parser.add_argument('--flatten', choices=['none', 'mean', 'polyfit', 'plane'], default='none', help='平面化方法')
    parser.add_argument('--save', action='store_true', help='儲存圖像')
    parser.add_argument('--output', help='輸出檔案路徑')
    
    args = parser.parse_args()
    
    # 檢查檔案是否存在
    if not os.path.exists(args.int):
        logger.error(f"INT 檔案不存在: {args.int}")
        return 1
    
    if not os.path.exists(args.txt):
        logger.warning(f"TXT 檔案不存在: {args.txt}")
        return 1
    
    try:
        # 解析 TXT 檔案
        metadata = parse_txt_file(args.txt)
        if not metadata:
            logger.error("無法解析 TXT 檔案，程式終止")
            return 1
        
        # 從 TXT 元數據中獲取 INT 檔案的參數
        int_filename = os.path.basename(args.int)
        params = find_int_file_parameters(metadata, int_filename)
        params['int_path'] = args.int  # 保存路徑用於後續使用
        
        # 解析 INT 檔案
        image_data = parse_int_file(args.int, params['x_pixels'], params['y_pixels'], params['scale'])
        if image_data is None:
            logger.error("無法解析 INT 檔案，程式終止")
            return 1
        
        # 生成形貌圖
        fig = generate_topo_plot(
            image_data, 
            params, 
            title=int_filename, 
            colormap=args.colormap,
            flatten_method=args.flatten
        )
        
        # 如果需要保存圖像
        if args.save:
            save_plot(fig, args.output, args.int)
        
        # 顯示圖像
        fig.show()
        
        logger.info("成功完成視覺化")
        return 0
        
    except Exception as e:
        logger.error(f"運行時出錯: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())