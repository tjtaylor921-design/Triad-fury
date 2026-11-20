import sys
from rembg import remove,new_session
from PIL import Image
D=sys.argv[1];a,b=int(sys.argv[2]),int(sys.argv[3])
s=new_session('u2net')
for fr in range(a,b):
    im=Image.open(f'{D}/full/f{fr+1:03d}.png').convert('RGB')
    remove(im,session=s).save(f'{D}/cut/c{fr:03d}.png')
print('done',a,b,flush=True)
