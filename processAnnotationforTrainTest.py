'''
function : PANDA annotations for coco format -> PANDA annotation for tiny_set format
每个切片大小为 640*512  这个看不明白的看修改images部分就明白了
将PANDA数据集缩小了10倍  因为之前的数据集太大了  网络传输时间太长了就缩小了 放在coco中
'''
import json
from PIL import Image

#需要更新的key
''' task 
:type   fin
annotations    fin
images  fin
categories  fin
old images  fin
'''
#写入文件的位置
out_file="panda_train_test_for_tiny_1024_1024.json"
#读取anno文件
anno_src_file_panda_coco="anno.json"
src_annos=json.load(open(anno_src_file_panda_coco))
#生成目标文件的副本 避免修改源文件
tiny_train_annos={}



#一些预处理  预处理结果都放在resize_src_anno中
resize_src_annos={}
#1  将源文件中的图像的大小改为之前的0.1
#2  将category==1的都找出来为检测目标

#--------------------------1
#需要修改的部分为  images:图像本身的大小*0.1   annos:bbox的大小*0.1  seg的大小*0.1  顺便把area的大小更改一下w*h

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

# print("-"*10,"test output for src_anno['annotations']['bbox']","-"*10)
# for item in resize_src_annos['annotations']:
#     print(item['bbox'],item['area'])
# print("-"*10,"end test output for src_anno['annotations']['bbox']","-"*10)

# print("-"*10,"test output for src_anno['annotations']['bbox']","-"*10)
# for item in resize_src_annos['annotations']:
#     print(item['segmentation'])
# print("-"*10,"end test output for src_anno['annotations']['bbox']","-"*10)
#----------------------------------end 1

#----------------------------------2
erase_cate_annos=[]
for item in resize_src_annos['annotations']:
    if item['category_id']==1:
        erase_cate_annos.append(item)
resize_src_annos['annotations']=erase_cate_annos

# print("-"*10,"test output for src_anno['annotations']['category_id']","-"*10)
# for item in resize_src_annos['annotations']:
#     print(item['category_id'])
# print("-"*10,"end test output for src_anno['annotations']['category_id']","-"*10)
#----------------------------------end 2




#type
tiny_train_annos['type']=src_annos['type']


#categories
tiny_train_annos['categories']=[src_annos['categories'][0]]

#old images
tiny_train_annos['old images']=resize_src_annos['images']

# print("-"*10,"test output for tiny_trian['old images']","-"*10)
# for item in tiny_train_annos['old images']:
#     print(item)
# print("-"*10,"end test output for tiny_trian['old images']","-"*10)




#images
'''
    由于images中的标注是通过标注中corner的方式对每个图像进行切割，对于图片本质上并没有变化，对于images部分的更新处理放在本部分进行
    这里的每个切片的大小为640*512  
'''
#------------------def 一些工具函数
#定义了通过图片的id从修改过大小的resize_src_annos中找到对应的annotations标注  并返回id相同的annotations
def find_id2annos(id):
    res=[]
    annos=resize_src_annos['annotations']
    for item in annos:
        if item['image_id']==id:
            res.append(item)
    return res
#定一个通过图像文件名获取标注中的大小信息  并返回对应的图像大小
def find_name2size(img_name):
    res=[]
    infos=tiny_train_annos['old images']
    for item in infos:
        if item['file_name']==img_name:
            return [item['width'],item['height']]

#----------------------end def

corner_width=1024
corner_height=1024
corner_image_id=0

img_ids={}  #获取文件名称与id的键值对方便代码的语义化
for x in tiny_train_annos['old images']:
    img_ids[x['file_name']]=x['id']
img_names=img_ids.keys()


# 将原图像进行分割得到分割后的images中的内部标记
images = [] #分割后的图像信息存放的临时变量
new_img_id=0
for img_name in img_names:
    # 获取之前图片对应的大小
    width, height = find_name2size(img_name)
    # 查看需要对一张图切割的份数
    k_x = (int)(width / corner_width)
    k_y = (int)(height / corner_height)
    if k_x * width != width:
        k_x = k_x + 1
    if k_x * height != height:
        k_y = k_y + 1

    # 对old images中的width 和 heigth进行切割修改
    corners = []
    for x in range(0, k_x):
        for y in range(0, k_y):
            corner = []
            tl_x = x * corner_width
            tl_y = y * corner_height
            if tl_x + corner_width >= width:
                tl_x = width - corner_width
            if tl_y + corner_height >= height:
                tl_y = height - corner_height
            br_x = tl_x + corner_width
            br_y = tl_y + corner_height
            corner.append(tl_x)
            corner.append(tl_y)
            corner.append(br_x)
            corner.append(br_y)
            corners.append(corner)
    corner_image = {}
    # 生成由一张图片切割生成的多组分割数据
    for item in corners:
        corner_image = {}
        corner_image['file_name'] = img_name
        corner_image['height'] = corner_height
        corner_image['width'] = corner_width
        corner_image['id'] = new_img_id
        new_img_id=new_img_id+1
        corner_image['corner'] = item
        images.append(corner_image)
tiny_train_annos['images']=images
print("success split images into corner ")
# print("-"*10,"test output for tiny_trian['images']","-"*10)
# print(tiny_train_annos['images'][0])
# print(tiny_train_annos['images'][1])
# print(tiny_train_annos['images'][2])
# print("-"*10,"end test output for tiny_trian['images']","-"*10)


#annotations
'''  process method
#对每张图片进行处理
#找出来所有的corner
#找出来所有corner所在的原始图片的bbox列表
#判断是否在corner内部
#如果是则将处理的结果根据公式进行处理
#将处理后的bbox 与原来的anno进行整合。是一个old images对应多个anno操作
#整合所有的新的bbox_n的annos
#覆盖所有的annnotations
'''
#------------------def 工具函数
# 用于检测corner 与bbox 是否为包含关系
def judjeContented(corner, bbox):
    c_tlx = corner[0]
    c_tly = corner[1]
    c_brx = corner[2]
    c_bry = corner[3]

    b_tlx = bbox[0]
    b_tly = bbox[1]
    b_brx = b_tlx + bbox[3]  # bbox[3] : width
    b_bry = b_tly + bbox[2]  # bbox[2] : height
    if (c_tlx <= b_tlx and c_tly <= b_tly) and (c_brx >= b_brx and c_bry >= b_bry):
        return True
    return False
#--------------------end def
new_annos=[] #将新生成的annos临时存放在这里面
new_gt_id=0
for img in tiny_train_annos['old images']:
    file_name=img['file_name']
    file_id=img['id']
    #找出来所有的corner  old_image->file_name   ==    images->file_name
    split_imgs_infos=[]
    for split_img in tiny_train_annos['images']:
        if split_img['file_name']==file_name:
            split_imgs_infos.append(split_img)
    #找出来所有corner所在的原始图片的bbox列表
    src_annos=[]
    for src_anno in resize_src_annos['annotations']:
        if src_anno['image_id']==file_id:
            src_annos.append(src_anno)
#     print("split_imgs_infos : {0}, src_annos : {1}".format(len(split_imgs_infos),len(src_annos)))
    #判断每个bbox是否在corner内部
    for img_info in split_imgs_infos:
        corner=img_info['corner']
        for src_anno in src_annos:
            bbox=src_anno['bbox']
            if judjeContented(corner,bbox):
                bbox_tmp=[]#临时存放bbox的修改值
                node_tmp={}#临时存放单个anno
                node_tmp_sorted={}#由于之前的键的顺序与目标文件不同需要调整
                bbox_tmp.append(bbox[0]-corner[0])
                bbox_tmp.append(bbox[1]-corner[1])
                bbox_tmp.append(bbox[2])
                bbox_tmp.append(bbox[3])
                node_tmp=src_anno
                '''修改一些tiny_set中与PANDA中不同的属性定义 并添加了log in_dense_image size属性，size的语义暂时不知道什么意思先用area代替？？？？？'''
                node_tmp['ignore']=False
                node_tmp['uncertain']=False
                node_tmp['logo']=False
                node_tmp['in_dense_image']=False
                node_tmp['size']=node_tmp['area']
                node_tmp['image_id']=img_info['id']
                node_tmp['id']=new_gt_id
                new_gt_id=new_gt_id+1

                #修改顺序
                node_tmp_sorted['segmentation']=node_tmp['segmentation']
                node_tmp_sorted['bbox']=node_tmp['bbox']
                node_tmp_sorted['category_id']=node_tmp['category_id']
                node_tmp_sorted['area']=node_tmp['area']
                node_tmp_sorted['iscrowd']=node_tmp['iscrowd']
                node_tmp_sorted['image_id']=node_tmp['image_id']
                node_tmp_sorted['id']=node_tmp['id']
                node_tmp_sorted['ignore']=node_tmp['ignore']
                node_tmp_sorted['uncertain']=node_tmp['uncertain']
                node_tmp_sorted['logo']=node_tmp['logo']
                node_tmp_sorted['in_dense_image']=node_tmp['in_dense_image']
                node_tmp_sorted['size']=node_tmp['size']

                new_annos.append(node_tmp_sorted)#将修改完成的anno添加到目标对象的anno变量中中
#将新生成的annos 添加到tiny_set的annotations中
tiny_train_annos['annotations']=new_annos

# print("-"*10,"test output for tiny_train['annotations']","-"*10)
# for item in tiny_train_annos['annotations']:
#     print(item)
# print("-"*10,"end test output for tiny_train['annotations']","-"*10)


with open(out_file,'w') as f:
    json.dump(tiny_train_annos,f)
print("success!")