# 生成华丽电器产品图片
import openai, os, time, json
from urllib.request import urlopen

client = openai.OpenAI()
OUT = r'D:\13486\Desktop\企业网站\frontend\public\images'

PRODUCTS = [
    ('hero-bg', 'Wide-angle view of a modern power tool factory assembly line, industrial setting, professional lighting, blue and orange tones, no text, no watermark'),
    ('factory', 'Modern electric tool manufacturing factory exterior with company sign area, clean architecture, sunny day, professional industrial photography, no text, no watermark'),
    ('drill', 'Professional red electric power drill, side view, isolated on white background, commercial product photography, studio lighting, centered composition, high detail, no text, no logo, no watermark'),
    ('hammer', 'Professional high-power rotary hammer / demolition hammer, red and black, diagonal view, isolated on white background, commercial product photography, studio lighting, no text, no logo, no watermark'),
    ('grinder', 'Professional angle grinder, red body, side view, grinding disc attached, isolated on white background, commercial product photography, studio lighting, centered, no text, no logo, no watermark'),
    ('cutter', 'Professional electric cut-off saw / metal cutting machine, red frame, with cutting blade, isolated on white background, commercial product photography, studio lighting, no text, no logo, no watermark'),
    ('sander', 'Professional electric sander / sanding machine, red body, orbital pad visible, isolated on white background, commercial product photography, studio lighting, no text, no logo, no watermark'),
    ('wrench', 'Professional high-torque impact wrench, red body, 1/2 inch drive, isolated on white background, commercial product photography, studio lighting, centered, no text, no logo, no watermark'),
]

for name, prompt in PRODUCTS:
    path = f'{OUT}/{"products/" if name != "hero-bg" and name != "factory" else ""}{name}.jpg'
    print(f'[{'='*40}]')
    print(f'  Generating: {name}.jpg')
    try:
        resp = client.images.generate(
            model='gpt-image-2',
            prompt=prompt,
            size='1024x1024',
            quality='high',
            n=1
        )
        url = resp.data[0].url
        img_data = urlopen(url).read()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(img_data)
        print(f'  ✅ Saved: {name}.jpg')
    except Exception as e:
        print(f'  ❌ Error: {e}')
    time.sleep(1)

print(f'\n{'='*40}')
print('✅ 全部图片生成完成！')
print(f'📁 目录: {OUT}/')
print(json.dumps([p[0] for p in PRODUCTS], ensure_ascii=False, indent=2))
print(f'📍 {OUT}/products/ 产品图片')
print(f'📄 {OUT}/hero-bg.jpg 和 {OUT}/factory.jpg 背景图')
