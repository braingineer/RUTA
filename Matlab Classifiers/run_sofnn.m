% EXACT DATA
%% TRAIN NET
net = train_sofnn(trainX, trainY);

%% TEST NET
disp(' ');
disp('Training data...');
pred = test_sofnn(net, trainX, trainY);
fprintf('MAPE: %f SMAPE: %f\n', mape(trainY, pred), smape(trainY, pred));
figure;
plot(1:size(trainX,1), trainY,'b*');
hold on;
plot(1:size(trainX,1), pred,'r');

disp(' ');
disp('Testing data...');
pred = test_sofnn(net, testX, testY);
fprintf('MAPE: %f SMAPE: %f\n', mape(testY, pred), smape(testY, pred));
figure;
plot(1:size(testX,1), testY,'b*');
hold on;
plot(1:size(testX,1), pred,'r');

%%
% DIRECTION DATA
%% TRAIN_NET
net = train_sofnn(dir_trainX, dir_trainY);

%% TEST NET
disp(' ');
disp('Training data...');
pred = test_sofnn(net, dir_trainX, dir_trainY) >= 0.5;
fprintf('Accuracy: %f\n', sum(pred==dir_trainY)*100/size(pred,1));
figure;
plot(1:size(dir_trainX,1), dir_trainY,'b*');
hold on;
plot(1:size(dir_trainX,1), pred,'r.');
ylim([-1 2]);

disp(' ');
disp('Testing data...');
pred = test_sofnn(net, dir_testX, dir_testY) >= .5;
fprintf('Accuracy: %f\n', sum(pred==dir_testY)*100/size(pred,1));
figure;
plot(1:size(dir_testX,1), dir_testY,'b*');
hold on;
plot(1:size(dir_testX,1), pred,'r.');
ylim([-1 2]);