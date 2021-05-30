'''
生成测试集
修改图像信息的宽度 高度  bbox area的大小
删掉一个category的vehicle
'''
import json

'''
:type
annotations
images
categories
'''

#写入文件的位置
out_file="panda_test_gt_for_tiny.json"
#读取anno文件
anno_src_file_panda_coco="anno.json"
src_annos=json.load(open(anno_src_file_panda_coco))
#生成目标文件的副本 避免修改源文件
tiny_test_annos={}

#需要修改的部分为  images:图像本身的大小*0.1   annos:bbox的大小*0.1  seg的大小*0.1  顺便把area的大小更改一下w*h
resize_src_annos={}
resize_src_annos['images']=src_annos['images']
resize_src_annos['annotations']=src_annos['annotations']
for item in resize_src_annos['images']:
    item['height']=(int)(item['height']/10)
    item['width']=(int)(item['width']/10)

# print("-"*10,"test output for src_anno['images'] ","-"*10)
# for item in resize_src_annos['images']:
#     print("{0} , {1} ".format(item['height'],item['width']))
# print("-"*10,"end test output for src_anno['images'] ","-"*10)

for item in resize_src_annos['annotations']:
    bbox=item['bbox']
    for i in range(0,len(bbox)):
        item['bbox'][i]=(int)(item['bbox'][i]/10)
    seg=item['segmentation']
    for i in range(0,len(seg[0])):
        item['segmentation'][0][i]=(int)(item['segmentation'][0][i]/10)
    item['area']=(int)(bbox[2]*bbox[3])
    #为每个annotation添加logo uncertain in_dense_image==false 同时ignore 为false
    item['ignore']=False
    item['uncertain']=False
    item['logo']=False
    item['in_dense_image']=False
# print("-"*10,"test output for src_anno['annotations']['bbox']","-"*10)
# for item in resize_src_annos['annotations']:
#     print(item['bbox'],item['area'])
# print("-"*10,"end test output for src_anno['annotations']['bbox']","-"*10)

# print("-"*10,"test output for src_anno['annotations']['bbox']","-"*10)
# for item in resize_src_annos['annotations']:
#     print(item['segmentation'])
# print("-"*10,"end test output for src_anno['annotations']['bbox']","-"*10)
tiny_test_annos['type']=src_annos['type']
tiny_test_annos['annotations']=resize_src_annos['annotations']
tiny_test_annos['images']=resize_src_annos['images']
tiny_test_annos['categories']=[src_annos['categories'][0]]


with open(out_file,'w') as f:
    json.dump(tiny_test_annos,f)
print("success!")
