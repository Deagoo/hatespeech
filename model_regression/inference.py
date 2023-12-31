import torch
import customDatasetTest
import os
import mymodel
import sys
sys.path.append('../evaluation')
import evaluate_model

dataset = '../../../datasets/HateSPic/MMHS/' # Path to dataset
split = 'MMHS_lstm_embeddings_regression/' + 'test.txt'

batch_size = 64
workers = 4

model_name = 'MMHS_regression_FCM_I_epoch_219_ValLoss_0.1.pth'
model_name = model_name.strip('.pth')

gpus = [0]
gpu = 0
CUDA_VISIBLE_DEVICES = 0

if not os.path.exists(dataset + 'results/' + model_name):
    os.makedirs(dataset + 'results/' + model_name)

output_file_path = dataset + 'results/' + model_name + '/test.txt'
output_file = open(output_file_path, "w")

if os.path.isfile(dataset + '/MMCNN_models/' + model_name + '.pth.tar'):
    state_dict = torch.load(dataset + '/MMCNN_models/' + model_name + '.pth.tar', map_location={'cuda:1':'cuda:0', 'cuda:2':'cuda:0', 'cuda:3':'cuda:0'})
else:
    state_dict = torch.load(dataset + '/MMCNN_models_loss/' + model_name + '.pth.tar', map_location={'cuda:1': 'cuda:0', 'cuda:2': 'cuda:0', 'cuda:3': 'cuda:0'})

model = mymodel.MyModel()
model = torch.nn.DataParallel(model, device_ids=gpus).cuda(gpu)
model.load_state_dict(state_dict)


test_dataset = customDatasetTest.customDatasetTest(dataset, split, Rescale=299)
test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=workers, pin_memory=True, sampler=None)

with torch.no_grad():
    model.eval()
    for i,(tweet_id, image, image_text, tweet, target) in enumerate(test_loader):

        image_var = torch.autograd.Variable(image)
        image_text_var = torch.autograd.Variable(image_text)
        tweet_var = torch.autograd.Variable(tweet)

        outputs = model(image_var, image_text_var, tweet_var)

        for idx,el in enumerate(outputs):
            class_label = 0
            if float(target[idx]) > 0.5: class_label = 1
            output_file.write(str(tweet_id[idx]) + ',' + str(class_label) + ',' + str(float(el)) + '\n')

        print(str(i) + ' / ' + str(len(test_loader)))

output_file.close()
print("Running evaluation on Test set")
evaluate_model.run_evaluation(model_name,'regression')