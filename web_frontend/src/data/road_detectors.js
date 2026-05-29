/**
 * 北京市主要道路检测器部署点（静态坐标数据）
 * 从 data_generator/road_data.py 提取，供前端地图使用
 */

const ROAD_DETECTORS = [
  // === 海淀区 ===
  { detector_id: "D00001", detector_name: "中关村大街-海淀黄庄路口", district: "海淀区", road_type: "主干路", direction: "南向北", lng: 116.312, lat: 39.989 },
  { detector_id: "D00002", detector_name: "中关村大街-海淀黄庄路口", district: "海淀区", road_type: "主干路", direction: "北向南", lng: 116.312, lat: 39.989 },
  { detector_id: "D00003", detector_name: "中关村大街-海淀黄庄路口", district: "海淀区", road_type: "主干路", direction: "东向西", lng: 116.312, lat: 39.989 },
  { detector_id: "D00004", detector_name: "中关村大街-海淀黄庄路口", district: "海淀区", road_type: "主干路", direction: "西向东", lng: 116.312, lat: 39.989 },
  { detector_id: "D00005", detector_name: "学院路-五道口路口", district: "海淀区", road_type: "主干路", direction: "南向北", lng: 116.324, lat: 39.998 },
  { detector_id: "D00006", detector_name: "学院路-五道口路口", district: "海淀区", road_type: "主干路", direction: "北向南", lng: 116.324, lat: 39.998 },
  { detector_id: "D00007", detector_name: "学院路-清华东路口", district: "海淀区", road_type: "主干路", direction: "南向北", lng: 116.328, lat: 40.003 },
  { detector_id: "D00008", detector_name: "学院路-清华东路口", district: "海淀区", road_type: "主干路", direction: "北向南", lng: 116.328, lat: 40.003 },
  { detector_id: "D00009", detector_name: "西二旗大街-上地七街路口", district: "海淀区", road_type: "主干路", direction: "南向北", lng: 116.306, lat: 40.051 },
  { detector_id: "D00010", detector_name: "西二旗大街-上地七街路口", district: "海淀区", road_type: "主干路", direction: "北向南", lng: 116.306, lat: 40.051 },
  { detector_id: "D00011", detector_name: "知春路-中关村大街口", district: "海淀区", road_type: "主干路", direction: "东向西", lng: 116.316, lat: 39.984 },
  { detector_id: "D00012", detector_name: "知春路-中关村大街口", district: "海淀区", road_type: "主干路", direction: "西向东", lng: 116.316, lat: 39.984 },
  { detector_id: "D00013", detector_name: "上地信息路-上地三街", district: "海淀区", road_type: "次干路", direction: "南向北", lng: 116.289, lat: 40.039 },
  { detector_id: "D00014", detector_name: "上地信息路-上地三街", district: "海淀区", road_type: "次干路", direction: "北向南", lng: 116.289, lat: 40.039 },
  { detector_id: "D00015", detector_name: "学院南路-交大东路路口", district: "海淀区", road_type: "次干路", direction: "南向北", lng: 116.336, lat: 39.945 },
  { detector_id: "D00077", detector_name: "五道口地铁站周边道路", district: "海淀区", road_type: "支路", direction: "南向北", lng: 116.319, lat: 39.997 },
  { detector_id: "D00078", detector_name: "五道口地铁站周边道路", district: "海淀区", road_type: "支路", direction: "北向南", lng: 116.319, lat: 39.997 },
  { detector_id: "D00079", detector_name: "西二旗地铁站周边道路", district: "海淀区", road_type: "支路", direction: "东向西", lng: 116.308, lat: 40.049 },
  { detector_id: "D00080", detector_name: "西二旗地铁站周边道路", district: "海淀区", road_type: "支路", direction: "西向东", lng: 116.308, lat: 40.049 },
  { detector_id: "D00095", detector_name: "西二旗大街-西二旗桥", district: "海淀区", road_type: "次干路", direction: "东向西", lng: 116.299, lat: 40.046 },
  { detector_id: "D00096", detector_name: "西二旗大街-西二旗桥", district: "海淀区", road_type: "次干路", direction: "西向东", lng: 116.299, lat: 40.046 },

  // === 朝阳区 ===
  { detector_id: "D00016", detector_name: "望京SOHO周边道路", district: "朝阳区", road_type: "主干路", direction: "南向北", lng: 116.472, lat: 39.996 },
  { detector_id: "D00017", detector_name: "望京SOHO周边道路", district: "朝阳区", road_type: "主干路", direction: "北向南", lng: 116.472, lat: 39.996 },
  { detector_id: "D00018", detector_name: "望京SOHO周边道路", district: "朝阳区", road_type: "主干路", direction: "东向西", lng: 116.472, lat: 39.996 },
  { detector_id: "D00019", detector_name: "望京SOHO周边道路", district: "朝阳区", road_type: "主干路", direction: "西向东", lng: 116.472, lat: 39.996 },
  { detector_id: "D00020", detector_name: "国贸桥-建外大街", district: "朝阳区", road_type: "主干路", direction: "南向北", lng: 116.446, lat: 39.908 },
  { detector_id: "D00021", detector_name: "国贸桥-建外大街", district: "朝阳区", road_type: "主干路", direction: "北向南", lng: 116.446, lat: 39.908 },
  { detector_id: "D00022", detector_name: "国贸桥-建外大街", district: "朝阳区", road_type: "主干路", direction: "东向西", lng: 116.446, lat: 39.908 },
  { detector_id: "D00023", detector_name: "三里屯路-工体北路路口", district: "朝阳区", road_type: "次干路", direction: "南向北", lng: 116.449, lat: 39.935 },
  { detector_id: "D00024", detector_name: "三里屯路-工体北路路口", district: "朝阳区", road_type: "次干路", direction: "北向南", lng: 116.449, lat: 39.935 },
  { detector_id: "D00025", detector_name: "慈云寺路-东四环路口", district: "朝阳区", road_type: "主干路", direction: "南向北", lng: 116.484, lat: 39.926 },
  { detector_id: "D00026", detector_name: "慈云寺路-东四环路口", district: "朝阳区", road_type: "主干路", direction: "北向南", lng: 116.484, lat: 39.926 },
  { detector_id: "D00027", detector_name: "东四环中路-红庙路口", district: "朝阳区", road_type: "快速路", direction: "南向北", lng: 116.458, lat: 39.921 },
  { detector_id: "D00028", detector_name: "东四环中路-红庙路口", district: "朝阳区", road_type: "快速路", direction: "北向南", lng: 116.458, lat: 39.921 },
  { detector_id: "D00073", detector_name: "京承高速-望和桥入口", district: "朝阳区", road_type: "高速", direction: "南向北", lng: 116.435, lat: 39.978 },
  { detector_id: "D00074", detector_name: "京承高速-望和桥入口", district: "朝阳区", road_type: "高速", direction: "北向南", lng: 116.435, lat: 39.978 },
  { detector_id: "D00075", detector_name: "京沪高速-分钟寺桥入口", district: "朝阳区", road_type: "高速", direction: "南向北", lng: 116.475, lat: 39.873 },
  { detector_id: "D00076", detector_name: "京沪高速-分钟寺桥入口", district: "朝阳区", road_type: "高速", direction: "北向南", lng: 116.475, lat: 39.873 },
  { detector_id: "D00091", detector_name: "酒仙桥路-将台路口", district: "朝阳区", road_type: "次干路", direction: "南向北", lng: 116.487, lat: 39.959 },
  { detector_id: "D00092", detector_name: "酒仙桥路-将台路口", district: "朝阳区", road_type: "次干路", direction: "北向南", lng: 116.487, lat: 39.959 },
  { detector_id: "D00093", detector_name: "东三环南路-潘家园桥", district: "朝阳区", road_type: "快速路", direction: "南向北", lng: 116.442, lat: 39.877 },
  { detector_id: "D00094", detector_name: "东三环南路-潘家园桥", district: "朝阳区", road_type: "快速路", direction: "北向南", lng: 116.442, lat: 39.877 },
  { detector_id: "D00103", detector_name: "望京西路-望京桥", district: "朝阳区", road_type: "主干路", direction: "南向北", lng: 116.459, lat: 39.973 },
  { detector_id: "D00104", detector_name: "望京西路-望京桥", district: "朝阳区", road_type: "主干路", direction: "北向南", lng: 116.459, lat: 39.973 },

  // === 西城区 ===
  { detector_id: "D00029", detector_name: "西单北大街-西长安街路口", district: "西城区", road_type: "主干路", direction: "南向北", lng: 116.373, lat: 39.914 },
  { detector_id: "D00030", detector_name: "西单北大街-西长安街路口", district: "西城区", road_type: "主干路", direction: "北向南", lng: 116.373, lat: 39.914 },
  { detector_id: "D00031", detector_name: "西单北大街-西长安街路口", district: "西城区", road_type: "主干路", direction: "东向西", lng: 116.373, lat: 39.914 },
  { detector_id: "D00032", detector_name: "西单北大街-西长安街路口", district: "西城区", road_type: "主干路", direction: "西向东", lng: 116.373, lat: 39.914 },
  { detector_id: "D00033", detector_name: "复兴路-木樨地路口", district: "西城区", road_type: "主干路", direction: "南向北", lng: 116.335, lat: 39.907 },
  { detector_id: "D00034", detector_name: "复兴路-木樨地路口", district: "西城区", road_type: "主干路", direction: "北向南", lng: 116.335, lat: 39.907 },
  { detector_id: "D00035", detector_name: "阜成路-花园桥路口", district: "西城区", road_type: "主干路", direction: "东向西", lng: 116.341, lat: 39.931 },

  // === 东城区 ===
  { detector_id: "D00036", detector_name: "东单北大街-东长安街路口", district: "东城区", road_type: "主干路", direction: "南向北", lng: 116.417, lat: 39.913 },
  { detector_id: "D00037", detector_name: "东单北大街-东长安街路口", district: "东城区", road_type: "主干路", direction: "北向南", lng: 116.417, lat: 39.913 },
  { detector_id: "D00038", detector_name: "东单北大街-东长安街路口", district: "东城区", road_type: "主干路", direction: "东向西", lng: 116.417, lat: 39.913 },
  { detector_id: "D00039", detector_name: "东单北大街-东长安街路口", district: "东城区", road_type: "主干路", direction: "西向东", lng: 116.417, lat: 39.913 },
  { detector_id: "D00040", detector_name: "崇文门内大街-东单北大街", district: "东城区", road_type: "主干路", direction: "南向北", lng: 116.414, lat: 39.905 },
  { detector_id: "D00041", detector_name: "崇文门内大街-东单北大街", district: "东城区", road_type: "主干路", direction: "北向南", lng: 116.414, lat: 39.905 },
  { detector_id: "D00081", detector_name: "北京站站前街", district: "东城区", road_type: "支路", direction: "南向北", lng: 116.427, lat: 39.904 },
  { detector_id: "D00082", detector_name: "北京站站前街", district: "东城区", road_type: "支路", direction: "北向南", lng: 116.427, lat: 39.904 },
  { detector_id: "D00083", detector_name: "朝阳门内大街-朝阳门桥", district: "东城区", road_type: "主干路", direction: "东向西", lng: 116.434, lat: 39.928 },
  { detector_id: "D00084", detector_name: "朝阳门内大街-朝阳门桥", district: "东城区", road_type: "主干路", direction: "西向东", lng: 116.434, lat: 39.928 },

  // === 丰台区 ===
  { detector_id: "D00042", detector_name: "西三环南路-六里桥", district: "丰台区", road_type: "快速路", direction: "南向北", lng: 116.311, lat: 39.884 },
  { detector_id: "D00043", detector_name: "西三环南路-六里桥", district: "丰台区", road_type: "快速路", direction: "北向南", lng: 116.311, lat: 39.884 },
  { detector_id: "D00044", detector_name: "南三环西路-玉泉营桥", district: "丰台区", road_type: "快速路", direction: "南向北", lng: 116.345, lat: 39.865 },
  { detector_id: "D00045", detector_name: "南三环西路-玉泉营桥", district: "丰台区", road_type: "快速路", direction: "北向南", lng: 116.345, lat: 39.865 },
  { detector_id: "D00046", detector_name: "蒲黄榆路-刘家窑桥", district: "丰台区", road_type: "主干路", direction: "南向北", lng: 116.423, lat: 39.868 },
  { detector_id: "D00047", detector_name: "蒲黄榆路-刘家窑桥", district: "丰台区", road_type: "主干路", direction: "北向南", lng: 116.423, lat: 39.868 },
  { detector_id: "D00097", detector_name: "西四环南路-岳各庄桥", district: "丰台区", road_type: "快速路", direction: "南向北", lng: 116.278, lat: 39.883 },
  { detector_id: "D00098", detector_name: "西四环南路-岳各庄桥", district: "丰台区", road_type: "快速路", direction: "北向南", lng: 116.278, lat: 39.883 },
  { detector_id: "D00099", detector_name: "丰台科技园周边道路", district: "丰台区", road_type: "次干路", direction: "南向北", lng: 116.282, lat: 39.831 },
  { detector_id: "D00100", detector_name: "丰台科技园周边道路", district: "丰台区", road_type: "次干路", direction: "北向南", lng: 116.282, lat: 39.831 },
  { detector_id: "D00101", detector_name: "宋家庄地铁站周边道路", district: "丰台区", road_type: "支路", direction: "南向北", lng: 116.428, lat: 39.841 },
  { detector_id: "D00102", detector_name: "宋家庄地铁站周边道路", district: "丰台区", road_type: "支路", direction: "北向南", lng: 116.428, lat: 39.841 },

  // === 石景山区 ===
  { detector_id: "D00048", detector_name: "复兴路-公主坟路口", district: "石景山区", road_type: "主干路", direction: "南向北", lng: 116.314, lat: 39.908 },
  { detector_id: "D00049", detector_name: "复兴路-公主坟路口", district: "石景山区", road_type: "主干路", direction: "北向南", lng: 116.314, lat: 39.908 },
  { detector_id: "D00050", detector_name: "复兴路-公主坟路口", district: "石景山区", road_type: "主干路", direction: "东向西", lng: 116.314, lat: 39.908 },
  { detector_id: "D00051", detector_name: "石景山路-八角桥", district: "石景山区", road_type: "主干路", direction: "东向西", lng: 116.225, lat: 39.907 },
  { detector_id: "D00052", detector_name: "石景山路-八角桥", district: "石景山区", road_type: "主干路", direction: "西向东", lng: 116.225, lat: 39.907 },

  // === 通州区 ===
  { detector_id: "D00053", detector_name: "新华大街-通州北苑路口", district: "通州区", road_type: "主干路", direction: "南向北", lng: 116.656, lat: 39.907 },
  { detector_id: "D00054", detector_name: "新华大街-通州北苑路口", district: "通州区", road_type: "主干路", direction: "北向南", lng: 116.656, lat: 39.907 },
  { detector_id: "D00055", detector_name: "新华大街-通州北苑路口", district: "通州区", road_type: "主干路", direction: "东向西", lng: 116.656, lat: 39.907 },
  { detector_id: "D00056", detector_name: "运河西大街-物资学院路口", district: "通州区", road_type: "主干路", direction: "东向西", lng: 116.634, lat: 39.918 },
  { detector_id: "D00057", detector_name: "运河西大街-物资学院路口", district: "通州区", road_type: "主干路", direction: "西向东", lng: 116.634, lat: 39.918 },
  { detector_id: "D00085", detector_name: "东六环-通州北关入口", district: "通州区", road_type: "高速", direction: "南向北", lng: 116.647, lat: 39.931 },
  { detector_id: "D00086", detector_name: "东六环-通州北关入口", district: "通州区", road_type: "高速", direction: "北向南", lng: 116.647, lat: 39.931 },

  // === 昌平区 ===
  { detector_id: "D00058", detector_name: "北清路-永丰路路口", district: "昌平区", road_type: "主干路", direction: "南向北", lng: 116.228, lat: 40.068 },
  { detector_id: "D00059", detector_name: "北清路-永丰路路口", district: "昌平区", road_type: "主干路", direction: "北向南", lng: 116.228, lat: 40.068 },
  { detector_id: "D00060", detector_name: "北清路-永丰路路口", district: "昌平区", road_type: "主干路", direction: "东向西", lng: 116.228, lat: 40.068 },
  { detector_id: "D00061", detector_name: "永丰路-北清路路口", district: "昌平区", road_type: "主干路", direction: "南向北", lng: 116.232, lat: 40.073 },
  { detector_id: "D00062", detector_name: "永丰路-北清路路口", district: "昌平区", road_type: "主干路", direction: "北向南", lng: 116.232, lat: 40.073 },
  { detector_id: "D00071", detector_name: "京藏高速-西三旗入口", district: "昌平区", road_type: "高速", direction: "东向西", lng: 116.339, lat: 40.023 },
  { detector_id: "D00072", detector_name: "京藏高速-西三旗入口", district: "昌平区", road_type: "高速", direction: "西向东", lng: 116.339, lat: 40.023 },
  { detector_id: "D00087", detector_name: "立汤路-天通苑路口", district: "昌平区", road_type: "主干路", direction: "南向北", lng: 116.407, lat: 40.072 },
  { detector_id: "D00088", detector_name: "立汤路-天通苑路口", district: "昌平区", road_type: "主干路", direction: "北向南", lng: 116.407, lat: 40.072 },
  { detector_id: "D00089", detector_name: "天通苑周边道路", district: "昌平区", road_type: "支路", direction: "南向北", lng: 116.412, lat: 40.067 },
  { detector_id: "D00090", detector_name: "天通苑周边道路", district: "昌平区", road_type: "支路", direction: "北向南", lng: 116.412, lat: 40.067 },
  { detector_id: "D00105", detector_name: "回龙观西大街-回龙观桥", district: "昌平区", road_type: "主干路", direction: "东向西", lng: 116.326, lat: 40.074 },
  { detector_id: "D00106", detector_name: "回龙观西大街-回龙观桥", district: "昌平区", road_type: "主干路", direction: "西向东", lng: 116.326, lat: 40.074 },

  // === 大兴区 ===
  { detector_id: "D00063", detector_name: "京开高速-西红门南桥", district: "大兴区", road_type: "高速", direction: "南向北", lng: 116.342, lat: 39.798 },
  { detector_id: "D00064", detector_name: "京开高速-西红门南桥", district: "大兴区", road_type: "高速", direction: "北向南", lng: 116.342, lat: 39.798 },
  { detector_id: "D00065", detector_name: "南六环-京开高速入口", district: "大兴区", road_type: "高速", direction: "东向西", lng: 116.348, lat: 39.768 },
  { detector_id: "D00066", detector_name: "南六环-京开高速入口", district: "大兴区", road_type: "高速", direction: "西向东", lng: 116.348, lat: 39.768 },

  // === 顺义区 ===
  { detector_id: "D00067", detector_name: "顺平路-枯柳树环岛", district: "顺义区", road_type: "主干路", direction: "南向北", lng: 116.653, lat: 40.128 },
  { detector_id: "D00068", detector_name: "顺平路-枯柳树环岛", district: "顺义区", road_type: "主干路", direction: "北向南", lng: 116.653, lat: 40.128 },
  { detector_id: "D00069", detector_name: "顺义区-首都机场高速", district: "顺义区", road_type: "高速", direction: "南向北", lng: 116.608, lat: 40.053 },
  { detector_id: "D00070", detector_name: "顺义区-首都机场高速", district: "顺义区", road_type: "高速", direction: "北向南", lng: 116.608, lat: 40.053 },
]

/** 需要从地图中隐藏的区域（无检测器数据的远郊区） */
export const EXCLUDED_DISTRICTS = ['房山区', '门头沟区', '延庆区', '怀柔区', '密云区', '平谷区']

/** 按区域分组获取检测器列表 */
export function getDetectorsByDistrict(district) {
  return ROAD_DETECTORS.filter(d => d.district === district)
}

/** 获取所有检测器 */
export function getAllDetectors() {
  return ROAD_DETECTORS
}

export default ROAD_DETECTORS
