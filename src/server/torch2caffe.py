from torch.autograd import Variable
import torch.onnx
import torch
from PIL import Image
from srresnet import _NetG
import onnx
# import caffe2.python.onnx.backend as backend
import onnx_caffe2.backend as backend
import numpy as np

def recursion_change_bn(module):
    if isinstance(module, torch.nn.InstanceNorm2d) or isinstance(module, torch.nn.BatchNorm2d):
        module.track_running_stats = 1
    else:
        for i, (name, module1) in enumerate(module._modules.items()):
            module1 = recursion_change_bn(module1)
    return module


def adjust(img):
    img = img*255.
    img[img<0] = 0
    img[img>255.] = 255.            
    img = img.transpose(1,2,0)
    return img.astype(np.uint8)



# load model
model = torch.load("/media/SRResNet/model/original.pth", map_location={'cuda:0': 'cpu'})['model']
# ok_model = _NetG()

# state_dict = model.state_dict()
# model = _NetG()
# model.load_state_dict(state_dict)

for i, (name, module) in enumerate(model._modules.items()):
    module = recursion_change_bn(model)

model.cpu()

# st_d = model.state_dict()
# from collections import OrderedDict
# new_state_dict = OrderedDict()
# for k, v in st_d.items():
#     if k not in unneeded:
#         new_state_dict[k] = v
# # load params
# ok_model.load_state_dict(new_state_dict)

# Evaluation Mode
model.train(False)

# # # # Create dummy input
x = np.array(Image.open('horse.png'))
x = np.expand_dims(x.astype(np.float32).transpose(2,0,1), axis=0) / 255.
inp = torch.Tensor(torch.from_numpy(x).float())
output_torch = model(inp)

# # # Export ONNX model
torch.onnx.export(model, inp, "/media/SRResNet/model.proto", verbose=True)

# # # Load ONNX model
onnx_model = onnx.load("/media/SRResNet/model.proto")
# onnx_model.ir_version = 1
# # Check Formation
onnx.checker.check_graph(onnx_model.graph)

# # Print Graph to get blob names
onnx.helper.printable_graph(onnx_model.graph)

# # Check model output
rep = backend.prepare(onnx_model, device="CPU")
inp_onnx = x 
print(inp_onnx)
output_onnx = rep.run(inp_onnx)


print(adjust(output_torch.data.numpy()[0]))
print(adjust(output_onnx[0][0]))

img_torch = adjust(output_torch.data.numpy()[0])
img_onnx = adjust(output_onnx[0][0])
print(np.max(np.abs(img_torch - img_onnx)))
print(np.mean(np.abs(img_torch - img_onnx)))
# # # # Verify the numerical correctness upto 3 decimal places
# np.testing.assert_almost_equal(output_torch.data.numpy(), output_onnx[0], decimal=3)

j = Image.fromarray(img_torch)
j.save('test_torch.png')
j = Image.fromarray(img_onnx)
j.save('test_onnx.png')
# print(im_h)

