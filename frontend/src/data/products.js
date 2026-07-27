export const productCategories = ['全部', '电钻系列', '电锤系列', '角磨机系列', '型材切割机', '砂光机系列', '冲击扳手系列']

export const categoryImages = {
  '电钻系列': '/images/products/drill.webp',
  '电锤系列': '/images/products/rotary-hammer.webp',
  '角磨机系列': '/images/products/angle-grinder.webp',
  '型材切割机': '/images/products/cut-off-saw.webp',
  '砂光机系列': '/images/products/sander.webp',
  '冲击扳手系列': '/images/products/impact-wrench.webp',
}

const productData = [
  { category: '电钻系列', name: '手电钻', model: 'HL-D101', level: '家用级', specs: { '功率': '500W', '转速': '0-2800rpm', '夹头': '10mm', '重量': '1.3kg' }, fullDesc: '轻便手电钻，适用于家庭日常钻孔作业，木材、塑料、金属薄板钻孔得心应手。', applications: ['家庭维修', 'DIY 手工', '家具安装'] },
  { category: '电钻系列', name: '冲击钻', model: 'HL-ID201', level: '专业级', specs: { '功率': '850W', '转速': '0-3200rpm', '冲击率': '48000bpm', '重量': '1.8kg' }, fullDesc: '专业冲击钻，具备钻孔与冲击双模式切换，适用于砖墙、混凝土等多种建材钻孔。', applications: ['装修施工', '管线安装', '室内装修'] },
  { category: '电钻系列', name: '锤钻', model: 'HL-RH301', level: '工业级', specs: { '功率': '1200W', '转速': '0-1500rpm', '冲击能': '3.5J', '重量': '5.2kg' }, fullDesc: '工业级锤钻，SDS-plus 夹头系统，大冲击能效，适用于钢筋混凝土钻孔作业。', applications: ['建筑施工', '混凝土钻孔', '钢结构安装'] },
  { category: '电锤系列', name: '电锤', model: 'HL-RH501', level: '专业级', specs: { '功率': '1050W', '冲击能': '5.0J', '转速': '0-950rpm', '重量': '5.8kg' }, fullDesc: '专业级电锤，高效破拆能力，配备减震手柄，长时间作业不易疲劳。', applications: ['墙体开槽', '管道安装', '拆除工程'] },
  { category: '电锤系列', name: '电镐', model: 'HL-BH601', level: '工业级', specs: { '功率': '1500W', '冲击能': '12J', '冲击率': '1800bpm', '重量': '12.5kg' }, fullDesc: '重型工业电镐，超大冲击能，适用于混凝土破碎、路面拆除等高强度作业。', applications: ['混凝土破碎', '路面拆除', '矿山开采'] },
  { category: '电锤系列', name: '无刷电锤', model: 'HL-BL401', level: '专业级', specs: { '功率': '800W', '冲击能': '3.8J', '转速': '0-1200rpm', '重量': '3.6kg' }, fullDesc: '无刷电机电锤，高效节能、寿命更长，轻量化设计适合高空作业。', applications: ['高空作业', '室内装修', '设备安装'] },
  { category: '角磨机系列', name: '角磨机 100mm', model: 'HL-AG101', level: '家用级', specs: { '功率': '750W', '转速': '11000rpm', '砂轮': '100mm', '重量': '1.6kg' }, fullDesc: '小型角磨机，轻巧便携，适合家庭 DIY 切割打磨作业。', applications: ['家庭 DIY', '金属切割', '焊缝打磨'] },
  { category: '角磨机系列', name: '角磨机 125mm', model: 'HL-AG201', level: '专业级', specs: { '功率': '1200W', '转速': '10000rpm', '砂轮': '125mm', '重量': '2.1kg' }, fullDesc: '专业角磨机，大功率电机，适合装修现场各种切割打磨任务。', applications: ['装修施工', '管道切割', '石材打磨'] },
  { category: '角磨机系列', name: '角磨机 230mm', model: 'HL-AG301', level: '工业级', specs: { '功率': '2000W', '转速': '6500rpm', '砂轮': '230mm', '重量': '5.4kg' }, fullDesc: '重型角磨机，超大切割深度，适用于型材、管材批量切割作业。', applications: ['钢材切割', '桥梁施工', '船舶制造'] },
  { category: '型材切割机', name: '型材切割机 305mm', model: 'HL-MC301', level: '专业级', specs: { '功率': '1800W', '转速': '3800rpm', '锯片': '305mm', '重量': '15.5kg' }, fullDesc: '专业型材切割机，精准角度调节，切割效率高，适合金属加工车间使用。', applications: ['金属加工', '门窗制造', '钢结构'] },
  { category: '型材切割机', name: '型材切割机 355mm', model: 'HL-MC351', level: '工业级', specs: { '功率': '2200W', '转速': '3600rpm', '锯片': '355mm', '重量': '18.2kg' }, fullDesc: '工业级型材切割机，大截面切割能力，配备激光定位辅助系统。', applications: ['重型钢结构', '桥梁工程', '设备制造'] },
  { category: '型材切割机', name: '斜切锯', model: 'HL-SC201', level: '专业级', specs: { '功率': '1500W', '转速': '4500rpm', '锯片': '255mm', '重量': '12.8kg' }, fullDesc: '多功能斜切锯，45°-90° 精准角度调节，适合相框、装饰线条等精细切割。', applications: ['木工制作', '装饰装修', '相框加工'] },
  { category: '砂光机系列', name: '平板砂光机', model: 'HL-S101', level: '家用级', specs: { '功率': '300W', '转速': '12000rpm', '砂纸': '280×100mm', '重量': '1.8kg' }, fullDesc: '平板砂光机，振动式打磨设计，适合木板、墙面等大面积砂光打磨。', applications: ['木工打磨', '墙面砂光', '旧漆去除'] },
  { category: '砂光机系列', name: '三角砂光机', model: 'HL-DS201', level: '专业级', specs: { '功率': '250W', '转速': '14000rpm', '砂纸': '三角形', '重量': '1.2kg' }, fullDesc: '三角细节砂光机，精准到达边角区域，是精细打磨作业的首选工具。', applications: ['边角打磨', '家具修复', '汽车修补'] },
  { category: '砂光机系列', name: '带式砂光机', model: 'HL-BS301', level: '工业级', specs: { '功率': '1200W', '转速': '350-550m/min', '砂带': '100×610mm', '重量': '7.5kg' }, fullDesc: '工业带式砂光机，强力去除材料表面，粗磨、精磨多档调速。', applications: ['金属去毛刺', '木材粗磨', '大面积整平'] },
  { category: '冲击扳手系列', name: '冲击扳手 1/2"', model: 'HL-IW201', level: '专业级', specs: { '扭矩': '450Nm', '转速': '1800rpm', '冲击率': '2800ipm', '重量': '2.3kg' }, fullDesc: '1/2 英寸冲击扳手，大扭矩输出，适用于汽车轮胎拆卸、机械装配。', applications: ['汽车维修', '机械装配', '轮胎更换'] },
  { category: '冲击扳手系列', name: '高扭矩冲击扳手', model: 'HL-IW401', level: '工业级', specs: { '扭矩': '1200Nm', '转速': '1500rpm', '冲击率': '2200ipm', '重量': '4.8kg' }, fullDesc: '超高扭矩冲击扳手，专为重型机械、大型螺栓紧固设计，经久耐用。', applications: ['重型机械', '工程车辆', '矿山设备'] },
  { category: '冲击扳手系列', name: '无刷冲击扳手', model: 'HL-BL601', level: '专业级', specs: { '扭矩': '650Nm', '转速': '2200rpm', '冲击率': '3200ipm', '重量': '1.8kg' }, fullDesc: '无刷电机冲击扳手，轻巧高效，三档扭矩调节，适应不同工况。', applications: ['汽车服务', '工业装配', '户外维修'] },
]

export const products = productData.map(product => ({
  ...product,
  image: categoryImages[product.category],
  highlights: ['高效动力系统', '人体工学握持', '多重安全防护', '严格耐久测试'],
}))

export function getProductByModel(model) {
  return products.find(product => product.model === model)
}
